from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import json
import hashlib
from pathlib import Path
import base64
from pdf2image import convert_from_path
from openai import OpenAI
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache directory for processed documents
CACHE_DIR = Path("./cache/processed_pdfs")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_pdf_hash(filepath: str) -> str:
    """Generate hash of PDF file for cache validation"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_from_cache(pdf_directory: str) -> Optional[List[Document]]:
    """Load processed documents from cache if available and valid"""
    cache_file = CACHE_DIR / "processed_documents.json"
    hash_file = CACHE_DIR / "pdf_hashes.json"
    
    if not cache_file.exists() or not hash_file.exists():
        return None
    
    try:
        # Load cached hashes
        with open(hash_file, 'r') as f:
            cached_hashes = json.load(f)
        
        # Verify all PDFs haven't changed
        current_hashes = {}
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        for filename in pdf_files:
            filepath = os.path.join(pdf_directory, filename)
            current_hashes[filename] = get_pdf_hash(filepath)
        
        # If hashes don't match, cache is invalid
        if current_hashes != cached_hashes:
            print("📝 PDFs have changed, cache invalidated")
            return None
        
        # Load cached documents
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)
        
        # Reconstruct Document objects
        documents = []
        for doc_data in cached_data:
            doc = Document(
                page_content=doc_data['page_content'],
                metadata=doc_data['metadata']
            )
            documents.append(doc)
        
        print(f"✓ Loaded {len(documents)} documents from cache")
        return documents
        
    except Exception as e:
        print(f"⚠️  Error loading cache: {e}")
        return None

def save_to_cache(documents: List[Document], pdf_directory: str):
    """Save processed documents to cache"""
    try:
        # Save document data
        cache_file = CACHE_DIR / "processed_documents.json"
        doc_data = [
            {
                'page_content': doc.page_content,
                'metadata': doc.metadata
            }
            for doc in documents
        ]
        
        with open(cache_file, 'w') as f:
            json.dump(doc_data, f, indent=2)
        
        # Save PDF hashes for validation
        hash_file = CACHE_DIR / "pdf_hashes.json"
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        hashes = {}
        
        for filename in pdf_files:
            filepath = os.path.join(pdf_directory, filename)
            hashes[filename] = get_pdf_hash(filepath)
        
        with open(hash_file, 'w') as f:
            json.dump(hashes, f, indent=2)
        
        print(f"✓ Saved {len(documents)} documents to cache")
        
    except Exception as e:
        print(f"⚠️  Error saving cache: {e}")

def analyze_page_with_vision(image_path: str, page_num: int, filename: str) -> str:
    """Use GPT-4 Vision to analyze a PDF page image"""
    try:
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create vision prompt for music theory content
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are analyzing a page from a music theory book. Extract and describe ALL content including:

1. Any text content (transcribe fully)
2. Musical notation and sheet music (describe what's shown)
3. Chord diagrams (list chords and their fingerings)
4. Tables and charts (describe structure and content)
5. Theoretical diagrams (circle of fifths, key relationships, etc.)
6. Any examples or exercises shown

Be comprehensive and specific. This content will be used for RAG retrieval to help songwriters learn music theory.
Format your response as clear, searchable text that captures all information on the page."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"   ✗ Vision API error for page {page_num}: {e}")
        return ""

def should_use_vision(page: Document, text_threshold: int = 100) -> bool:
    """Determine if a page should be processed with vision API"""
    text_content = page.page_content.strip()
    
    # Use vision if:
    # 1. Very little text extracted (likely scanned/image)
    # 2. Contains indicators of visual content
    visual_indicators = ['figure', 'diagram', 'chart', 'table', 'example', '♪', '♯', '♭']
    
    has_little_text = len(text_content) < text_threshold
    has_visual_indicators = any(indicator.lower() in text_content.lower() for indicator in visual_indicators)
    
    return has_little_text or has_visual_indicators

def process_pdf_with_vision(filepath: str, filename: str, output_dir: str = "./temp_images") -> List[Document]:
    """Process PDF pages with vision API where needed"""
    documents = []
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # First try regular text extraction
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        
        print(f"   Analyzing {len(pages)} pages...")
        
        # Convert PDF to images (one image per page)
        images = convert_from_path(filepath, dpi=200)
        
        for i, (page, image) in enumerate(zip(pages, images)):
            page_num = i + 1
            
            # Save temporary image
            image_path = os.path.join(output_dir, f"temp_page_{page_num}.jpg")
            image.save(image_path, 'JPEG')
            
            # Check if we should use vision
            if should_use_vision(page):
                print(f"   🔍 Using vision API for page {page_num}")
                vision_content = analyze_page_with_vision(image_path, page_num, filename)
                
                if vision_content:
                    # Combine original text with vision analysis
                    combined_content = f"{page.page_content.strip()}\n\n--- Vision Analysis ---\n{vision_content}"
                    
                    doc = Document(
                        page_content=combined_content,
                        metadata={
                            'source_file': filename,
                            'page': page_num,
                            'processing_method': 'vision_enhanced',
                            'has_visual_content': True
                        }
                    )
                    documents.append(doc)
                else:
                    # Fallback to original if vision fails
                    page.metadata['source_file'] = filename
                    page.metadata['processing_method'] = 'text_only'
                    documents.append(page)
            else:
                # Use original text extraction
                print(f"   📄 Using text extraction for page {page_num}")
                page.metadata['source_file'] = filename
                page.metadata['page'] = page_num
                page.metadata['processing_method'] = 'text_only'
                documents.append(page)
            
            # Clean up temp image
            os.remove(image_path)
        
        print(f"   ✓ Processed {len(documents)} pages")
        return documents
        
    except Exception as e:
        print(f"   ✗ Error processing {filename}: {e}")
        return []
    finally:
        # Cleanup temp directory
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

def load_music_theory_pdfs(pdf_directory: str, use_cache: bool = True, use_vision: bool = True):
    """Load PDFs and extract text (with optional vision processing and caching)"""
    
    # Try to load from cache first
    if use_cache:
        cached_docs = load_from_cache(pdf_directory)
        if cached_docs is not None:
            return cached_docs
    
    documents = []
    
    if not os.path.exists(pdf_directory):
        print(f"⚠️  Directory {pdf_directory} not found!")
        return documents
    
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    if use_vision:
        print(f"🔍 Vision processing enabled - this may take a while...")
    
    for filename in pdf_files:
        filepath = os.path.join(pdf_directory, filename)
        print(f"   Loading {filename}...")
        
        try:
            if use_vision:
                # Use enhanced vision processing
                docs = process_pdf_with_vision(filepath, filename)
                documents.extend(docs)
            else:
                # Use original text-only extraction
                loader = PyPDFLoader(filepath)
                pages = loader.load()
                
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
    
    # Save to cache
    if use_cache and documents:
        save_to_cache(documents, pdf_directory)
    
    return documents

def chunk_documents(documents, chunk_size=500, chunk_overlap=50, vision_chunk_size=1000, vision_chunk_overlap=100):
    """
    Smart chunking for RAG - uses larger chunks for vision-enhanced content
    
    Args:
        documents: List of Document objects
        chunk_size: Chunk size for text-only documents (default: 500)
        chunk_overlap: Overlap for text-only documents (default: 50)
        vision_chunk_size: Chunk size for vision-enhanced documents (default: 1000)
        vision_chunk_overlap: Overlap for vision-enhanced documents (default: 100)
    """
    if not documents:
        print("⚠️  No documents to chunk")
        return []
    
    # Separate vision-enhanced from text-only documents
    vision_docs = [doc for doc in documents if doc.metadata.get('processing_method') == 'vision_enhanced']
    text_docs = [doc for doc in documents if doc.metadata.get('processing_method') != 'vision_enhanced']
    
    all_chunks = []
    
    # Chunk text-only documents
    if text_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        text_chunks = text_splitter.split_documents(text_docs)
        all_chunks.extend(text_chunks)
        print(f"✓ Created {len(text_chunks)} text-only chunks (size={chunk_size}, overlap={chunk_overlap})")
    
    # Chunk vision-enhanced documents with larger size
    if vision_docs:
        vision_splitter = RecursiveCharacterTextSplitter(
            chunk_size=vision_chunk_size,
            chunk_overlap=vision_chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        vision_chunks = vision_splitter.split_documents(vision_docs)
        all_chunks.extend(vision_chunks)
        print(f"✓ Created {len(vision_chunks)} vision-enhanced chunks (size={vision_chunk_size}, overlap={vision_chunk_overlap})")
    
    print(f"✓ Total chunks created: {len(all_chunks)}")
    return all_chunks

def clear_cache():
    """Clear the document cache"""
    cache_file = CACHE_DIR / "processed_documents.json"
    hash_file = CACHE_DIR / "pdf_hashes.json"
    
    if cache_file.exists():
        os.remove(cache_file)
    if hash_file.exists():
        os.remove(hash_file)
    
    print("✓ Cache cleared")