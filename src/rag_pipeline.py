"""Retrieval-Augmented Generation (RAG) pipeline for the Vehicle Troubleshooting Assistant.

Connects semantic vector retrieval over ChromaDB with a grounded LLM prompt architecture,
enforcing strict anti-hallucination guardrails, mandatory source record citations [VTR-XXXXX],
automotive safety disclaimers, and structured multi-section diagnostic responses.
"""

import re
from typing import Any, Dict, List, Optional
from src.chroma_manager import ChromaDBManager
from src.llm_provider import BaseLLMProvider, LLMResponse, get_llm_provider
from src.semantic_search import SemanticSearchEngine
from src.utils import setup_logger

logger = setup_logger("rag_pipeline")

PROMPT_VERSION = "2.1.0-grounded-automotive-diagnostic"

SYSTEM_PROMPT = """You are an expert Automotive Diagnostic Troubleshooting Assistant.
Your mission is to provide accurate, cautious, and helpful vehicle troubleshooting guidance grounded STRICTLY in the provided retrieved diagnostic records.

STRICT OPERATIONAL RULES:
1. GROUNDING & HONESTY: Answer ONLY using the facts, possible causes, symptoms, and diagnostic steps documented in the retrieved records. If the retrieved records do not contain enough information to diagnose the issue, explicitly state that the context is insufficient.
2. NO HALLUCINATION: Never invent diagnostic trouble codes, torque specifications, sensor voltages, wiring pinouts, or vehicle-specific service bulletins not present in the context.
3. CAUSALITY vs CORRELATION: A diagnostic trouble code (DTC) indicates that a circuit or monitored parameter is outside calibrated thresholds; it does NOT prove that the sensor or component itself has failed. Clearly distinguish between possible causes and confirmed failures.
4. MANDATORY CITATIONS: Whenever stating a diagnostic fault, symptom, cause, or check, cite the source record ID in square brackets, e.g., [VTR-P00B7].
5. AUTOMOTIVE SAFETY: Vehicle systems such as High-Voltage (hybrid/EV) battery loops, Hydraulic Braking systems, Supplemental Restraint Systems (airbags), and steering linkages carry severe safety risks. Always advise that high-risk diagnostics and repairs be performed by an ASE-certified automotive technician.

REQUIRED ANSWER FORMAT:
### 1. Summary of Reported Problem
Synthesize the reported symptom and how it maps to automotive subsystems.

### 2. Possible Causes (Supported by Retrieved Knowledge)
List the most probable causes documented in the retrieved records, citing the specific [VTR-XXXXX] records for each cause.

### 3. Step-by-Step Diagnostic & Inspection Procedures
Provide prioritized, non-destructive diagnostic checks supported by the records (visual checks, wiring harness inspection, OBD-II data verification).

### 4. Limitations & Missing Information
State any diagnostic ambiguities, missing vehicle details (make, model, engine code), or areas where the retrieved context is insufficient.

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
) -> str:
    """Constructs the user message incorporating query and optional retrieved context."""
    if is_baseline_no_context:
        return (
            f"VEHICLE SYMPTOM / DRIVER COMPLAINT:\n\"{query}\"\n\n"
            f"RETRIEVED TROUBLESHOOTING CONTEXT:\n"
            f"[NO RETRIEVED CONTEXT AVAILABLE. Answer using general automotive background knowledge only.]\n\n"
            f"Please analyze this vehicle problem following the required structured format."
        )

    return (
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
    ) -> Dict[str, Any]:
        """Executes a full RAG query or an unassisted baseline query.

        Args:
            query_text: Natural language symptom description.
            query_id: Optional query identifier (e.g. 'Q01').
            top_k: Number of documents to retrieve (defaults to self.default_top_k).
            where_filter: Optional metadata filter dict.
            is_baseline: If True, executes as an unassisted baseline without retrieved context.

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

        # Step 2: Format Context
        context_str = format_context_documents(retrieved_docs) if not is_baseline else ""

        # Step 3: Construct Grounded Prompt
        user_prompt = construct_user_prompt(
            query=clean_query,
            context_text=context_str,
            is_baseline_no_context=is_baseline,
        )

        # Step 4: Dispatch to LLM Provider
        llm_response: LLMResponse = self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=1024,
        )

        # Step 5: Extract Citations from generated answer
        cited_ids = extract_cited_record_ids(llm_response.content)

        # Step 6: Assemble Standardized Experiment Payload
        execution_status = "success" if llm_response.is_success else "failed"

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
            "retrieval_k": k if not is_baseline else 0,
            "retrieved_documents": formatted_retrieved,
            "retrieved_record_ids": [d["record_id"] for d in formatted_retrieved],
            "llm_provider": self.llm_provider.name,
            "llm_model": self.llm_provider.model_name,
            "generation_mode": self.llm_provider.generation_mode,
            "prompt_version": self.prompt_version,
            "system_prompt": SYSTEM_PROMPT,
            "context_used": context_str,
            "user_prompt": user_prompt,
            "generated_answer": llm_response.content,
            "source_record_ids": cited_ids,
            "latency_ms": llm_response.latency_ms,
            "tokens_used": llm_response.tokens_used,
            "execution_status": execution_status,
            "error_message": llm_response.error,
        }

