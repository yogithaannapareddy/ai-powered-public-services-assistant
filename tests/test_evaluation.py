"""
Quantitative Evaluation Suite for AI-Powered Public Services Assistant.
Runs a benchmark on representative citizen service queries and measures:
- Retrieval Relevance
- Answer Grounding / Correctness
- Citation Correctness
- Latency (ms)
"""

import time
import pytest
from src.document_loader import DocumentLoader
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline

# Evaluation benchmark dataset
EVALUATION_DATASET = [
    {
        "query": "How do I send an interstate parcel via Speed Post and track it?",
        "expected_category": "Post Office Services",
        "expected_terms": ["Speed Post", "parcel", "track", "13"],
        "expected_source": "Speed Post"
    },
    {
        "query": "How can I open an IPPB zero balance account at my doorstep?",
        "expected_category": "Post Office Services",
        "expected_terms": ["IPPB", "Aadhaar", "doorstep", "biometric"],
        "expected_source": "India Post Payments Bank"
    },
    {
        "query": "What Officially Valid Documents (OVD) are required for bank KYC?",
        "expected_category": "Banking Services",
        "expected_terms": ["Aadhaar", "PAN", "KYC", "Passport"],
        "expected_source": "Reserve Bank of India"
    },
    {
        "query": "Do I need to enter my UPI PIN to receive money or cashback?",
        "expected_category": "Banking Services",
        "expected_terms": ["UPI PIN", "receive", "never", "fraud"],
        "expected_source": "UPI"
    },
    {
        "query": "What time does Tatkal train ticket reservation open for AC classes?",
        "expected_category": "Public Transportation",
        "expected_terms": ["10:00", "Tatkal", "AC"],
        "expected_source": "Railways"
    },
    {
        "query": "How do students get a concessional state transport bus pass?",
        "expected_category": "Public Transportation",
        "expected_terms": ["bonafide", "pass", "student"],
        "expected_source": "Bus"
    },
    {
        "query": "How do I apply for an Income Certificate and how long does it take?",
        "expected_category": "Government Services",
        "expected_terms": ["Income", "Certificate", "ServicePlus"],
        "expected_source": "Certificate"
    },
    {
        "query": "Are driving licenses and RC stored in DigiLocker legally valid?",
        "expected_category": "Government Services",
        "expected_terms": ["DigiLocker", "Rule 9A", "valid"],
        "expected_source": "DigiLocker"
    }
]

@pytest.fixture(scope="module")
def populated_rag_pipeline():
    """Build and populate vector store with complete knowledge base for evaluation."""
    vs = VectorStore(persist_dir="data/eval_chroma_db", collection_name="eval_collection")
    loader = DocumentLoader()
    chunks = loader.load_all_sample_knowledge()
    vs.add_chunks(chunks)
    pipeline = RAGPipeline(vector_store=vs, api_key="")
    return pipeline

def test_evaluation_benchmark(populated_rag_pipeline):
    pipeline = populated_rag_pipeline
    
    total_queries = len(EVALUATION_DATASET)
    relevant_retrievals = 0
    correct_citations = 0
    grounded_answers = 0
    latencies = []

    print("\n" + "="*70)
    print("BENCHMARK EVALUATION RESULTS: PUBLIC SERVICES ASSISTANT RAG PIPELINE")
    print("="*70)

    for idx, item in enumerate(EVALUATION_DATASET, start=1):
        q = item["query"]
        expected_cat = item["expected_category"]
        expected_terms = item["expected_terms"]
        expected_source = item["expected_source"]

        res = pipeline.generate(query=q, category=expected_cat)
        answer = res.get("answer", "")
        citations = res.get("citations", [])
        latency = res.get("latency_ms", 0)
        latencies.append(latency)

        # 1. Measure Retrieval Relevance
        retrieved_docs = pipeline.retrieve(query=q, category=expected_cat, top_k=3)
        retrieved_text = " ".join([d["text"] for d in retrieved_docs])
        terms_found = sum(1 for term in expected_terms if term.lower() in retrieved_text.lower())
        retrieval_success = (terms_found >= 2)
        if retrieval_success:
            relevant_retrievals += 1

        # 2. Measure Citation Correctness
        citation_success = False
        if citations:
            for c in citations:
                if expected_source.lower() in c.source_title.lower() or expected_cat.lower() in c.category.lower():
                    citation_success = True
                    break
        if citation_success:
            correct_citations += 1

        # 3. Measure Answer Grounding
        answer_grounded = any(term.lower() in answer.lower() for term in expected_terms[:2])
        if answer_grounded:
            grounded_answers += 1

        print(f"[{idx}/{total_queries}] Query: '{q[:45]}...'")
        print(f"       Category: {expected_cat} | Latency: {latency} ms")
        print(f"       Retrieval Match: {'PASS' if retrieval_success else 'FAIL'} | Citation Match: {'PASS' if citation_success else 'FAIL'} | Grounding: {'PASS' if answer_grounded else 'FAIL'}")

    retrieval_relevance_pct = (relevant_retrievals / total_queries) * 100
    citation_accuracy_pct = (correct_citations / total_queries) * 100
    answer_correctness_pct = (grounded_answers / total_queries) * 100
    avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0

    print("-" * 70)
    print(f"SUMMARY METRICS:")
    print(f"  • Total Benchmark Queries:      {total_queries}")
    print(f"  • Retrieval Relevance Rate:     {retrieval_relevance_pct:.1f}% ({relevant_retrievals}/{total_queries})")
    print(f"  • Source Citation Accuracy:     {citation_accuracy_pct:.1f}% ({correct_citations}/{total_queries})")
    print(f"  • Answer Grounding / Accuracy:  {answer_correctness_pct:.1f}% ({grounded_answers}/{total_queries})")
    print(f"  • Average Retrieval Latency:    {avg_latency_ms:.1f} ms")
    print("=" * 70 + "\n")

    # Assert rigorous quality thresholds
    assert retrieval_relevance_pct >= 85.0, f"Retrieval relevance was {retrieval_relevance_pct}%"
    assert citation_accuracy_pct >= 85.0, f"Citation accuracy was {citation_accuracy_pct}%"
    assert answer_correctness_pct >= 85.0, f"Answer correctness was {answer_correctness_pct}%"
    assert avg_latency_ms < 500.0, f"Average latency was {avg_latency_ms} ms (expected < 500 ms)"
