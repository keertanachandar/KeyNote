"""
KeyNote RAGAS Baseline Evaluation
Simple script - just run it!
"""

# ============================================================================
# IMPORTS
# ============================================================================

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset import TestsetGenerator
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_core.documents import Document
import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Add parent directory to path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, src_dir)

from utils.pdf_loader import load_music_theory_pdfs, chunk_documents
from utils.rag_system import ChordProgressionRAG
from agents.langgraph_orchestrator import LangGraphOrchestrator

load_dotenv()

print("\n" + "="*80)
print("KEYNOTE RAGAS BASELINE EVALUATION")
print("="*80)

# ============================================================================
# STEP 1: INITIALIZE KEYNOTE SYSTEM
# ============================================================================

print("\n📊 Step 1: Initializing KeyNote system...")

docs = load_music_theory_pdfs("../data/pdfs")
chunks = chunk_documents(docs) if docs else []
rag = ChordProgressionRAG(chunks, "../data/theorytab/progressions.csv")
orchestrator = LangGraphOrchestrator(rag)

print("✓ KeyNote system ready!")

# ============================================================================
# STEP 2: PREPARE DOCUMENTS FOR SYNTHETIC GENERATION
# ============================================================================

print("\n📚 Step 2: Loading documents for test generation...")

# Load progression data as documents
prog_df = pd.read_csv("../data/theorytab/progressions.csv")
progression_docs = []

for _, row in prog_df.iterrows():
    content = f"""Chord Progression: {row['progression_roman']}
Chords Example: {row['chords_example']}
Frequency: {row['frequency']}
Genres: {row['genres']}
Mood: {row['mood']}
Famous Songs: {row['example_songs']}

This progression is commonly used in {row['genres']} music and creates a {row['mood']} feeling."""
    
    doc = Document(
        page_content=content,
        metadata={
            "source": "progression_database",
            "progression": row['progression_roman'],
            "mood": row['mood'],
            "genres": row['genres']
        }
    )
    progression_docs.append(doc)

print(f"✓ Loaded {len(progression_docs)} progression documents")

# Load PDFs if available
pdf_docs = []
pdf_path = "../data/pdfs/"
if os.path.exists(pdf_path):
    try:
        loader = DirectoryLoader(pdf_path, glob="*.pdf", loader_cls=PyPDFLoader)
        all_pdf_docs = loader.load()
        # Filter pages with minimal text
        pdf_docs = [d for d in all_pdf_docs if len(d.page_content.strip()) > 100]
        print(f"✓ Loaded {len(pdf_docs)} PDF pages with text")
    except Exception as e:
        print(f"⚠️  Could not load PDFs: {e}")

# Combine all documents
all_docs = progression_docs + pdf_docs
print(f"✓ Total documents for test generation: {len(all_docs)}")

# ============================================================================
# STEP 3: GENERATE SYNTHETIC TEST DATA WITH RAGAS
# ============================================================================

print("\n🤖 Step 3: Generating synthetic test data...")
print("This may take 3-5 minutes...\n")

# Initialize RAGAS generator
generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
generator_embeddings = LangchainEmbeddingsWrapper(
    OpenAIEmbeddings(model="text-embedding-3-small")
)

generator = TestsetGenerator(
    llm=generator_llm,
    embedding_model=generator_embeddings
)

# Generate synthetic test set
testset_size = 10  # Adjust this number as needed
testset = generator.generate_with_langchain_docs(all_docs, testset_size=testset_size)

# Convert to DataFrame
synthetic_df = testset.to_pandas()
print(f"✓ Generated {len(synthetic_df)} synthetic test cases\n")

# Show sample questions
print("Sample questions generated:")
for i, row in synthetic_df.head(3).iterrows():
    query = row.get('user_input', row.get('question', ''))
    print(f"{i+1}. {query[:100]}...")
print()

# ============================================================================
# STEP 4: RUN TEST CASES THROUGH KEYNOTE
# ============================================================================

print("🎸 Step 4: Running test cases through KeyNote system...")
print("This may take 5-10 minutes...\n")

questions = []
answers = []
contexts = []
ground_truths = []

for i, row in synthetic_df.iterrows():
    print(f"Processing test case {i+1}/{len(synthetic_df)}...", end="\r")
    
    # Get the question
    query = row.get('user_input', row.get('question', ''))
    
    try:
        # Generate response using KeyNote
        results = orchestrator.generate_recommendations(
            query,
            lyrics=None,
            reference_artists=None
        )
        
        # Store question and answer
        questions.append(query)
        answers.append(results['synthesis'])
        
        # Extract contexts from retrieved progressions
        context_list = []
        for prog in results['progressions']:
            ctx = f"{prog.metadata['progression_roman']} ({prog.metadata['chords_example']}): "
            ctx += f"Mood: {prog.metadata['mood']}, "
            ctx += f"Examples: {prog.metadata.get('example_songs', 'N/A')[:100]}"
            context_list.append(ctx)
        contexts.append(context_list)
        
        # Ground truth from synthetic data
        ground_truth = row.get('reference', row.get('reference_contexts', 'N/A'))
        if isinstance(ground_truth, list):
            ground_truth = " ".join(str(x) for x in ground_truth) if ground_truth else "N/A"
        ground_truths.append(str(ground_truth))
        
    except Exception as e:
        print(f"\n⚠️  Error on test case {i+1}: {e}")
        questions.append(query)
        answers.append(f"Error: {str(e)}")
        contexts.append(["Error occurred"])
        ground_truths.append("N/A")

print(f"\n✓ Generated {len(answers)} responses")

# ============================================================================
# STEP 5: CREATE RAGAS DATASET
# ============================================================================

print("\n📊 Step 5: Creating RAGAS dataset...")

ragas_dataset = Dataset.from_dict({
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truth": ground_truths
})

print(f"✓ RAGAS dataset created with {len(ragas_dataset)} examples")

# ============================================================================
# STEP 6: RUN RAGAS EVALUATION
# ============================================================================

print("\n🔍 Step 6: Running RAGAS evaluation...")
print("This may take 2-5 minutes...\n")

result = evaluate(
    ragas_dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ],
)

print("✓ RAGAS evaluation complete!")

# ============================================================================
# STEP 7: DISPLAY AND SAVE RESULTS
# ============================================================================

print("\n" + "="*80)
print("RESULTS")
print("="*80)

# Convert to DataFrame
results_df = result.to_pandas()

# Calculate average scores
avg_scores = {
    'Faithfulness': results_df['faithfulness'].mean(),
    'Answer Relevancy': results_df['answer_relevancy'].mean(),
    'Context Precision': results_df['context_precision'].mean(),
    'Context Recall': results_df['context_recall'].mean(),
}

print("\n📈 AVERAGE SCORES (Baseline):")
print("-"*80)
for metric, score in avg_scores.items():
    print(f"{metric:.<40} {score:.3f}")
print("-"*80)

# Show individual scores
print("\n📊 Individual Test Case Scores:")
print("-"*80)
display_df = results_df[['question', 'faithfulness', 'answer_relevancy', 
                          'context_precision', 'context_recall']].copy()
display_df['question'] = display_df['question'].str[:60] + '...'
print(display_df.to_string(index=True))

# ============================================================================
# STEP 8: SAVE RESULTS
# ============================================================================

print("\n💾 Step 8: Saving results...")

# Save detailed results
results_df.to_csv("evaluation/baseline_results.csv", index=False)
print("✓ Detailed results saved to evaluation/baseline_results.csv")

# Save summary
summary_file = "evaluation/baseline_summary.txt"
with open(summary_file, 'w') as f:
    f.write("KEYNOTE RAGAS BASELINE EVALUATION SUMMARY\n")
    f.write("="*80 + "\n\n")
    f.write(f"Test Cases: {len(results_df)}\n")
    f.write(f"Test Set Size: {testset_size}\n")
    f.write(f"Documents Used: {len(all_docs)}\n\n")
    f.write("AVERAGE SCORES:\n")
    f.write("-"*80 + "\n")
    for metric, score in avg_scores.items():
        f.write(f"{metric:.<40} {score:.3f}\n")
    f.write("-"*80 + "\n")

print(f"✓ Summary saved to {summary_file}")

# ============================================================================
# DONE!
# ============================================================================

print("\n" + "="*80)
print("✅ BASELINE EVALUATION COMPLETE!")
print("="*80)
print("\nNext steps:")
print("1. Review evaluation/baseline_results.csv for detailed scores")
print("2. Review evaluation/baseline_summary.txt for summary")
print("3. Implement advanced retrieval (Task 6)")
print("4. Run comparison evaluation")
print("\n")