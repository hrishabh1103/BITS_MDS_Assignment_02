"""Retrieval-Augmented Generation (RAG) pipeline for the Vehicle Troubleshooting Assistant.

Connects semantic vector retrieval over ChromaDB with a grounded LLM prompt architecture,
enforcing strict anti-hallucination guardrails, mandatory source record citations [VTR-XXXXX],
automotive safety disclaimers, and structured multi-section diagnostic responses.
"""

import re
from typing import Any, Dict, List, Optional
from src.chroma_manager import ChromaDBManager
from src.llm_provider import BaseLLMProvider, LLMResponse, get_llm_provider
from src.safety_guardrails import (
    SafetyAlert,
    build_safety_augmented_instructions,
    detect_safety_triggers,
    generate_safety_alerts,
)
from src.semantic_search import SemanticSearchEngine
from src.utils import setup_logger

logger = setup_logger("rag_pipeline")

PROMPT_VERSION = "2.2.0-grounded-automotive-diagnostic"

SYSTEM_PROMPT = """You are an expert Automotive Diagnostic Troubleshooting Assistant.
Your mission is to provide accurate, cautious, and helpful vehicle troubleshooting guidance grounded STRICTLY in the provided retrieved diagnostic records.

STRICT OPERATIONAL RULES:
1. GROUNDING & HONESTY: Answer ONLY using the facts, possible causes, symptoms, and diagnostic steps documented in the retrieved records. If the retrieved records do not contain enough information to diagnose the issue, explicitly state that the context is insufficient. Never force an answer from irrelevant records.
2. NO HALLUCINATION: Never invent diagnostic trouble codes, torque specifications, sensor reference voltages, resistance thresholds, wiring pinouts, or vehicle-specific service bulletins not present in the context.
3. CAUSALITY vs CORRELATION: A diagnostic trouble code (DTC) indicates that a circuit or monitored parameter is outside calibrated thresholds; it does NOT prove that the sensor or component itself has failed. Clearly distinguish between possible causes and confirmed failures.
4. MANDATORY CITATIONS: Whenever stating a diagnostic fault, symptom, cause, or check, cite the source record ID in square brackets, e.g., [VTR-P00B7].
5. AUTOMOTIVE SAFETY: Vehicle systems such as High-Voltage (hybrid/EV) battery loops, Hydraulic Braking systems, Supplemental Restraint Systems (airbags), and cooling thermal systems carry severe safety risks. Always advise that high-risk diagnostics and repairs be performed by an ASE-certified automotive technician.

REQUIRED ANSWER FORMAT:
### 1. Summary of Reported Problem
Synthesize the reported symptom and how it maps to automotive subsystems.

### 2. Possible Causes (Supported by Retrieved Knowledge)
List the most probable causes documented in the retrieved records, citing the specific [VTR-XXXXX] records for each cause. Clearly distinguish primary causes from secondary possibilities.

### 3. Step-by-Step Diagnostic & Inspection Procedures
Provide prioritized, non-destructive diagnostic checks supported by the records (visual checks, wiring harness inspection, OBD-II data verification).

### 4. Limitations & Missing Information
State any diagnostic ambiguities, missing vehicle details (make, model, engine code), or areas where the retrieved context is insufficient or mismatched.

### 5. Source Record Citations
Explicitly list all source record IDs that informed this answer.
"""


def format_context_documents(retrieved_docs: List[Dict[str, Any]]) -> str:
    """Formats a list of retrieved record dictionaries into an annotated context block."""
    if not retrieved_docs:
        return "NO RETRIEVED CONTEXT AVAILABLE. (No matching database records found)."

    context_blocks = []
    for doc in retrieved_docs:
        rank = doc.get("rank", 1)
        rec_id = doc.get("record_id") or doc.get("id", "UNKNOWN")
        title = doc.get("title", "")
        system = doc.get("vehicle_system", "")
        codes = doc.get("diagnostic_codes", "")
        severity = doc.get("severity", "")
        distance = doc.get("distance", 0.0)
        similarity = doc.get("similarity_score", 0.0)
        full_doc = doc.get("document", "")

        block = (
            f"--- [RECORD #{rank}: {rec_id}] ---\n"
            f"Title: {title}\n"
            f"Diagnostic Code(s): {codes}\n"
            f"Vehicle Subsystem: {system}\n"
            f"Severity Classification: {severity}\n"
            f"Retrieval Distance: {distance:.4f} (Cosine Similarity: {similarity:.4f})\n"
            f"Record Content:\n{full_doc}\n"
        )
        context_blocks.append(block)

    return "\n".join(context_blocks)


def construct_user_prompt(
    query: str,
    context_text: str,
    is_baseline_no_context: bool = False,
    vehicle_type: str = "Unknown",
    vehicle_info: Optional[Dict[str, Any]] = None,
) -> str:
    """Constructs the user message incorporating query, vehicle metadata, and optional retrieved context."""
    vehicle_meta_str = ""
    meta_parts = []
    if vehicle_type and vehicle_type != "Unknown":
        meta_parts.append(f"Powertrain Type: {vehicle_type}")
    if vehicle_info:
        for k in ("year", "make", "model", "engine"):
            if vehicle_info.get(k):
                meta_parts.append(f"{k.capitalize()}: {vehicle_info[k]}")
    if meta_parts:
        vehicle_meta_str = f"VEHICLE INFORMATION:\n" + " | ".join(meta_parts) + "\n\n"

    if is_baseline_no_context:
        return (
            f"{vehicle_meta_str}"
            f"VEHICLE SYMPTOM / DRIVER COMPLAINT:\n\"{query}\"\n\n"
            f"RETRIEVED TROUBLESHOOTING CONTEXT:\n"
            f"[NO RETRIEVED CONTEXT AVAILABLE. Answer using general automotive background knowledge only.]\n\n"
            f"Please analyze this vehicle problem following the required structured format."
        )

    return (
        f"{vehicle_meta_str}"
        f"VEHICLE SYMPTOM / DRIVER COMPLAINT:\n\"{query}\"\n\n"
        f"RETRIEVED TROUBLESHOOTING CONTEXT (FROM CHROMADB DATABASE):\n"
        f"{context_text}\n\n"
        f"Using ONLY the retrieved records above, provide a comprehensive, cautious diagnostic troubleshooting response. "
        f"Remember to cite record IDs (e.g., [VTR-XXXXX]) for every technical claim."
    )


def extract_cited_record_ids(text: str) -> List[str]:
    """Extracts all unique record IDs matching the pattern VTR-[A-Z0-9]+ cited in the answer."""
    matches = re.findall(r"VTR-[A-Z0-9]+", text)
    # Deduplicate while preserving appearance order
    seen = set()
    unique_ids = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            unique_ids.append(m)
    return unique_ids


class RAGPipeline:
    """End-to-end Retrieval-Augmented Generation pipeline for vehicle troubleshooting."""

    def __init__(
        self,
        search_engine: Optional[SemanticSearchEngine] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
        chroma_manager: Optional[ChromaDBManager] = None,
        default_top_k: int = 5,
    ):
        self.chroma_manager = chroma_manager or ChromaDBManager()
        self.search_engine = search_engine or SemanticSearchEngine(chroma_manager=self.chroma_manager)
        self.llm_provider = llm_provider or get_llm_provider(allow_mock_fallback=True)
        self.default_top_k = default_top_k
        self.prompt_version = PROMPT_VERSION
        logger.info(
            f"Initialized RAGPipeline (top_k={self.default_top_k}, "
            f"provider='{self.llm_provider.name}', model='{self.llm_provider.model_name}', "
            f"mode='{self.llm_provider.generation_mode}')"
        )

    def query(
        self,
        query_text: str,
        query_id: Optional[str] = None,
        top_k: Optional[int] = None,
        where_filter: Optional[Dict[str, Any]] = None,
        is_baseline: bool = False,
        vehicle_type: str = "Unknown",
        vehicle_info: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1536,
    ) -> Dict[str, Any]:
        """Executes a full RAG query or an unassisted baseline query with backend safety guardrails.

        Args:
            query_text: Natural language symptom description.
            query_id: Optional query identifier (e.g. 'Q01').
            top_k: Number of documents to retrieve (defaults to self.default_top_k).
            where_filter: Optional metadata filter dict.
            is_baseline: If True, executes as an unassisted baseline without retrieved context.
            vehicle_type: Vehicle powertrain type ('ICE', 'Hybrid', 'EV', 'Unknown').
            vehicle_info: Optional dictionary with vehicle attributes (make, model, year, engine).
            max_tokens: Configurable output token limit (default: 1536).

        Returns:
            Structured result dictionary compliant with assignment evaluation specifications.
        """
        k = top_k or self.default_top_k
        clean_query = query_text.strip()

        # Step 1: Semantic Retrieval (omitted if running unassisted baseline)
        retrieved_docs: List[Dict[str, Any]] = []
        if not is_baseline:
            retrieved_docs = self.search_engine.search(
                query=clean_query,
                top_k=k,
                query_id=query_id,
                where=where_filter,
            )

        # Step 2: Backend Safety Guardrails & Domain Mismatch Detection
        triggers = detect_safety_triggers(
            query=clean_query,
            retrieved_docs=retrieved_docs,
            vehicle_type=vehicle_type,
        )
        safety_alerts = generate_safety_alerts(triggers)
        safety_directives = build_safety_augmented_instructions(triggers)
        effective_system_prompt = SYSTEM_PROMPT + safety_directives

        # Step 3: Format Context
        context_str = format_context_documents(retrieved_docs) if not is_baseline else ""

        # Step 4: Construct Grounded Prompt
        user_prompt = construct_user_prompt(
            query=clean_query,
            context_text=context_str,
            is_baseline_no_context=is_baseline,
            vehicle_type=vehicle_type,
            vehicle_info=vehicle_info,
        )

        # Step 5: Dispatch to LLM Provider
        llm_response: LLMResponse = self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=effective_system_prompt,
            temperature=0.2,
            max_tokens=max_tokens,
        )

        # Step 6: Extract Citations from generated answer
        cited_ids = extract_cited_record_ids(llm_response.content)

        # Step 7: Truncation and Status Analysis
        tokens_used = llm_response.tokens_used or {}
        comp_tokens = tokens_used.get("completion_tokens", 0)
        is_truncated = (comp_tokens >= max_tokens) and (max_tokens > 0)

        if not llm_response.is_success:
            execution_status = "failed"
        elif is_truncated:
            execution_status = "truncated"
        else:
            execution_status = "success"

        # Format retrieved documents cleanly for serialization
        formatted_retrieved = []
        for d in retrieved_docs:
            formatted_retrieved.append({
                "rank": d.get("rank"),
                "record_id": d.get("record_id"),
                "title": d.get("title"),
                "diagnostic_codes": d.get("diagnostic_codes"),
                "vehicle_system": d.get("vehicle_system"),
                "severity": d.get("severity"),
                "distance": d.get("distance"),
                "similarity_score": d.get("similarity_score"),
                "excerpt": d.get("excerpt"),
                "metadata": d.get("metadata", {}),
            })

        return {
            "query_id": query_id or "adhoc",
            "query": clean_query,
            "is_baseline": is_baseline,
            "vehicle_type": vehicle_type,
            "vehicle_info": vehicle_info or {},
            "retrieval_k": k if not is_baseline else 0,
            "retrieved_documents": formatted_retrieved,
            "retrieved_record_ids": [d["record_id"] for d in formatted_retrieved],
            "llm_provider": self.llm_provider.name,
            "llm_model": self.llm_provider.model_name,
            "generation_mode": self.llm_provider.generation_mode,
            "prompt_version": self.prompt_version,
            "system_prompt": effective_system_prompt,
            "context_used": context_str,
            "user_prompt": user_prompt,
            "generated_answer": llm_response.content,
            "source_record_ids": cited_ids,
            "latency_ms": llm_response.latency_ms,
            "tokens_used": tokens_used,
            "is_truncated": is_truncated,
            "execution_status": execution_status,
            "error_message": llm_response.error,
            "safety_alerts": [a.__dict__ for a in safety_alerts],
            "safety_triggers": triggers,
            "context_mismatch": triggers.get("ice_12v_battery_mismatch", False),
        }

