"""
KeyNote RAGAS Evaluation with Manual Test Cases
No synthetic generation - just evaluate!
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
print("KEYNOTE RAGAS BASELINE EVALUATION (Manual Test Cases)")
print("="*80)

# Initialize system
print("\n📊 Initializing KeyNote...")
docs = load_music_theory_pdfs("data/pdfs", use_cache=True, use_vision=True)
chunks = chunk_documents(docs) if docs else []
rag = ChordProgressionRAG(chunks, "data/theorytab/progressions.csv", use_persistent_storage=True)
orchestrator = LangGraphOrchestrator(rag)
print("✓ System ready!")

# Manual test cases
print("\n📝 Using manual test cases...")
test_cases = [
    {
        "query": "melancholic indie folk progressions",
        "ground_truth": "Should return minor key progressions like vi-IV-I-V with melancholic mood, indie folk examples like Bon Iver or Phoebe Bridgers."
    },
    {
        "query": "upbeat pop progressions for summer song",
        "ground_truth": "Should return major key progressions like I-V-vi-IV with uplifting mood, pop examples, high energy."
    },
    {
        "query": "dark moody alternative rock progressions",
        "ground_truth": "Should return minor key or power chord progressions with dark mood, alternative rock examples."
    },
    {
        "query": "simple acoustic folk progressions",
        "ground_truth": "Should return simple 3-4 chord progressions like I-IV-V, folk genre, beginner-friendly."
    },
    {
        "query": "jazzy sophisticated chord progressions",
        "ground_truth": "Should return ii-V-I or complex progressions, jazz examples, sophisticated harmony."
    },
    {
        "query": "energetic rock progressions",
        "ground_truth": "Should return power chord progressions, rock genre, high energy, anthemic quality."
    },
    {
        "query": "sad ballad progressions in minor key",
        "ground_truth": "Should return minor key progressions like i-iv-VII-III, sad mood, ballad examples."
    },
    {
        "query": "nostalgic oldies doo-wop progressions",
        "ground_truth": "Should return I-vi-IV-V or I-vi-ii-V, nostalgic mood, 1950s-60s examples."
    },
]

# Run test cases
print(f"Running {len(test_cases)} test cases...\n")

questions = []
answers = []
contexts = []
ground_truths = []

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}/{len(test_cases)}: {test['query'][:50]}...")
    
    try:
        results = orchestrator.generate_recommendations(test['query'], None, None)
        
        questions.append(test['query'])
        answers.append(results['synthesis'])
        
        context_list = [f"{p.metadata['progression_roman']}: {p.metadata.get('example_songs', '')[:100]}" 
                       for p in results['progressions']]
        contexts.append(context_list)
        ground_truths.append(test['ground_truth'])
        
        print(f"  ✓ Complete")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        questions.append(test['query'])
        answers.append("Error")
        contexts.append(["Error"])
        ground_truths.append(test['ground_truth'])

# Evaluate
print("\n🔍 Running RAGAS evaluation...")
dataset = Dataset.from_dict({
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truth": ground_truths
})

result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])

# Results
print("\n" + "="*80)
print("RESULTS")
print("="*80)

df = result.to_pandas()
avg_scores = {
    'Faithfulness': df['faithfulness'].mean(),
    'Answer Relevancy': df['answer_relevancy'].mean(),
    'Context Precision': df['context_precision'].mean(),
    'Context Recall': df['context_recall'].mean(),
}

print("\n📈 AVERAGE SCORES:")
for metric, score in avg_scores.items():
    print(f"{metric:.<40} {score:.3f}")

# Save
df.to_csv("src/evaluation/baseline_results.csv", index=False)
print("\n✓ Saved to evaluation/baseline_results.csv")

with open("src/evaluation/baseline_summary.txt", 'w') as f:
    f.write("KEYNOTE RAGAS BASELINE EVALUATION\n")
    f.write("="*80 + "\n\n")
    f.write(f"Test Cases: {len(test_cases)} (manual)\n\n")
    f.write("AVERAGE SCORES:\n")
    for metric, score in avg_scores.items():
        f.write(f"{metric:.<40} {score:.3f}\n")

print("✓ Saved to evaluation/baseline_summary.txt")
print("\n✅ BASELINE EVALUATION COMPLETE!")