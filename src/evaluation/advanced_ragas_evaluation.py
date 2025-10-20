"""
KeyNote Advanced Retrieval Evaluation
Tests multiple advanced retrieval techniques
"""

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
import sys
import os
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from utils.rag_system import ChordProgressionRAG
from agents.langgraph_orchestrator import LangGraphOrchestrator

load_dotenv()

print("\n" + "="*80)
print("KEYNOTE ADVANCED RETRIEVAL EVALUATION")
print("="*80)

# Test cases (same as baseline)
test_cases = [
    {"query": "melancholic indie folk progressions", "ground_truth": "Minor key, indie folk examples"},
    {"query": "upbeat pop progressions", "ground_truth": "Major key, uplifting, pop examples"},
    {"query": "dark moody alternative rock progressions", "ground_truth": "Minor key, dark mood, alternative"},
    {"query": "simple acoustic folk progressions", "ground_truth": "Simple progressions, folk genre"},
    {"query": "jazzy sophisticated progressions", "ground_truth": "Complex progressions, jazz"},
    {"query": "energetic rock progressions", "ground_truth": "Power chords, rock, high energy"},
    {"query": "sad ballad progressions", "ground_truth": "Minor key, sad mood, ballad"},
    {"query": "nostalgic oldies progressions", "ground_truth": "Nostalgic mood, 1950s-60s"},
]

# Initialize system
print("\n📊 Initializing KeyNote...")
docs = load_music_theory_pdfs("data/pdfs")
chunks = chunk_documents(docs) if docs else []
rag = ChordProgressionRAG(chunks, "data/theorytab/progressions.csv")

print("✓ System ready!")

# Test each advanced retrieval technique
techniques = {
    "baseline": "search_progressions",
    "metadata_filter": "search_progressions_with_metadata_filter",
    "query_expansion": "search_progressions_with_query_expansion",
    "reranking": "search_progressions_with_reranking",
    "hybrid": "search_progressions_hybrid",
    "dynamic_k": "search_progressions_dynamic_k",
}

results_all = {}

for technique_name, method_name in techniques.items():
    print(f"\n{'='*80}")
    print(f"TESTING: {technique_name.upper()}")
    print(f"{'='*80}")
    
    questions = []
    contexts_list = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}: {test['query'][:40]}...")
        
        query = test['query']
        
        # Extract genre/mood for metadata filtering
        genre = None
        mood = None
        if technique_name == "metadata_filter":
            if "folk" in query:
                genre = "folk"
            elif "pop" in query:
                genre = "pop"
            elif "rock" in query:
                genre = "rock"
            elif "jazz" in query:
                genre = "jazz"
            
            if "melancholic" in query or "sad" in query:
                mood = "melancholic"
            elif "upbeat" in query or "energetic" in query:
                mood = "uplifting"
            elif "dark" in query or "moody" in query:
                mood = "dark"
        
        try:
            # Call appropriate method
            if technique_name == "baseline":
                results = rag.search_progressions(query, k=5)
            elif technique_name == "metadata_filter":
                results = rag.search_progressions_with_metadata_filter(query, genre=genre, mood=mood, k=5)
            elif technique_name == "query_expansion":
                results = rag.search_progressions_with_query_expansion(query, k=5)
            elif technique_name == "reranking":
                results = rag.search_progressions_with_reranking(query, lyrics_analysis=None, k=5)
            elif technique_name == "hybrid":
                results = rag.search_progressions_hybrid(query, k=5)
            elif technique_name == "dynamic_k":
                results = rag.search_progressions_dynamic_k(query, lyrics_analysis=None)
            
            questions.append(query)
            context_list = [f"{p.metadata['progression_roman']}: {p.metadata.get('example_songs', '')[:80]}" 
                           for p in results]
            contexts_list.append(context_list)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            questions.append(query)
            contexts_list.append(["Error"])
    
    # Store results
    results_all[technique_name] = {
        'contexts': contexts_list,
        'questions': questions
    }
    
    print(f"✓ {technique_name} complete")

# Evaluate each technique (using context precision and recall)
print("\n" + "="*80)
print("COMPUTING METRICS FOR EACH TECHNIQUE")
print("="*80)

summary_results = []

for technique_name in techniques.keys():
    print(f"\nEvaluating {technique_name}...")
    
    # Create minimal dataset (we only care about context metrics)
    dataset = Dataset.from_dict({
        "question": results_all[technique_name]['questions'],
        "answer": ["placeholder"] * len(test_cases),  # Dummy answers
        "contexts": results_all[technique_name]['contexts'],
        "ground_truth": [t['ground_truth'] for t in test_cases]
    })
    
    try:
        result = evaluate(dataset, metrics=[context_precision, context_recall])
        df = result.to_pandas()
        
        avg_precision = df['context_precision'].mean()
        avg_recall = df['context_recall'].mean()
        
        summary_results.append({
            'Technique': technique_name,
            'Context Precision': avg_precision,
            'Context Recall': avg_recall,
            'Combined Score': (avg_precision + avg_recall) / 2
        })
        
        print(f"  Precision: {avg_precision:.3f}, Recall: {avg_recall:.3f}")
    except Exception as e:
        print(f"  ✗ Evaluation failed: {e}")
        summary_results.append({
            'Technique': technique_name,
            'Context Precision': 0,
            'Context Recall': 0,
            'Combined Score': 0
        })

# Display comparison
print("\n" + "="*80)
print("ADVANCED RETRIEVAL COMPARISON")
print("="*80)

summary_df = pd.DataFrame(summary_results)
summary_df = summary_df.sort_values('Combined Score', ascending=False)
print(summary_df.to_string(index=False))

# Save results
summary_df.to_csv("src/evaluation/advanced_retrieval_comparison.csv", index=False)
print("\n✓ Results saved to src/evaluation/advanced_retrieval_comparison.csv")

# Identify best technique
best_technique = summary_df.iloc[0]['Technique']
best_score = summary_df.iloc[0]['Combined Score']

print(f"\n🏆 BEST TECHNIQUE: {best_technique.upper()}")
print(f"   Combined Score: {best_score:.3f}")

print("\n✅ ADVANCED RETRIEVAL EVALUATION COMPLETE!")