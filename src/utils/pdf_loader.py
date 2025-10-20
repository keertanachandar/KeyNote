from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def load_music_theory_pdfs(pdf_directory):
    """Load PDFs and extract text"""
    documents = []
    
    if not os.path.exists(pdf_directory):
        print(f"⚠️  Directory {pdf_directory} not found!")
        return documents
    
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    for filename in pdf_files:
        filepath = os.path.join(pdf_directory, filename)
        print(f"   Loading {filename}...")
        
        try:
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            
            # Filter pages with substantial text (>100 chars)
            # This skips pages that are mostly images/music notation
            text_pages = []
            for page in pages:
                if len(page.page_content.strip()) > 100:
                    page.metadata['source_file'] = filename
                    text_pages.append(page)
            
            documents.extend(text_pages)
            print(f"   ✓ Extracted {len(text_pages)} pages with text")
            
        except Exception as e:
            print(f"   ✗ Error loading {filename}: {e}")
    
    print(f"\n✓ Total pages loaded: {len(documents)}")
    return documents

def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    """Chunk documents for RAG"""
    if not documents:
        print("⚠️  No documents to chunk")
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✓ Created {len(chunks)} chunks (chunk_size={chunk_size}, overlap={chunk_overlap})")
    return chunks