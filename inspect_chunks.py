"""
Inspect PDF Chunking Results
Run this after the first load to see how PDFs were chunked
"""

import json
from pathlib import Path

def inspect_chunks():
    cache_file = Path("./cache/processed_pdfs/processed_documents.json")
    
    if not cache_file.exists():
        print("❌ No cache found yet. Wait for the first load to complete.")
        return
    
    print("\n" + "="*70)
    print("📊 PDF CHUNKING INSPECTION")
    print("="*70)
    
    with open(cache_file, 'r') as f:
        data = json.load(f)
    
    total_chunks = len(data)
    print(f"\n✅ Total chunks created: {total_chunks}")
    
    # Group by source file
    by_source = {}
    for doc in data:
        source = doc['metadata']['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(doc)
    
    print(f"\n📚 PDFs processed: {len(by_source)}")
    print("\n" + "-"*70)
    
    for source, chunks in sorted(by_source.items()):
        pdf_name = Path(source).name
        vision_chunks = sum(1 for c in chunks if c['metadata'].get('has_vision', False))
        text_chunks = len(chunks) - vision_chunks
        
        print(f"\n📄 {pdf_name}")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   - Text-only: {text_chunks}")
        print(f"   - Vision-enhanced: {vision_chunks}")
        
        # Show first chunk as sample
        first_chunk = chunks[0]
        content_preview = first_chunk['page_content'][:200].replace('\n', ' ')
        print(f"   First chunk preview: {content_preview}...")
        
        if first_chunk['metadata'].get('has_vision'):
            print(f"   ✨ Uses GPT-4 Vision for diagrams/tables")
    
    print("\n" + "-"*70)
    print("\n📊 CHUNK SIZE ANALYSIS")
    
    chunk_sizes = [len(doc['page_content']) for doc in data]
    avg_size = sum(chunk_sizes) / len(chunk_sizes)
    min_size = min(chunk_sizes)
    max_size = max(chunk_sizes)
    
    print(f"   Average chunk size: {avg_size:.0f} characters")
    print(f"   Smallest chunk: {min_size} characters")
    print(f"   Largest chunk: {max_size} characters")
    
    # Show a few sample chunks
    print("\n" + "-"*70)
    print("\n📝 SAMPLE CHUNKS (first 3)")
    
    for i, doc in enumerate(data[:3], 1):
        print(f"\n[Chunk {i}] Source: {Path(doc['metadata']['source']).name}")
        print(f"Page: {doc['metadata'].get('page', 'N/A')}")
        print(f"Has Vision: {doc['metadata'].get('has_vision', False)}")
        print(f"Content ({len(doc['page_content'])} chars):")
        print("-" * 50)
        print(doc['page_content'][:400])
        print("..." if len(doc['page_content']) > 400 else "")
    
    print("\n" + "="*70)
    print("✅ Inspection complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    inspect_chunks()

