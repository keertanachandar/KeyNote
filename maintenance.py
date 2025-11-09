#!/usr/bin/env python3
"""
KeyNote Maintenance Utility

Provides easy commands for managing caches and vectorstores.
Run from project root: python maintenance.py [command]
"""

import sys
import os
import shutil
from pathlib import Path

def clear_pdf_cache():
    """Clear cached PDF processing data"""
    cache_dir = Path("./cache/processed_pdfs")
    
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            print("✓ Cleared PDF cache")
            print(f"  Location: {cache_dir.absolute()}")
            print("  Next run will reprocess PDFs with vision API")
        except Exception as e:
            print(f"✗ Error clearing PDF cache: {e}")
    else:
        print("⚠️  PDF cache directory not found (nothing to clear)")

def clear_vectorstores():
    """Clear persistent Qdrant vectorstores"""
    vectorstore_dir = Path("./vectorstore")
    
    if vectorstore_dir.exists():
        try:
            shutil.rmtree(vectorstore_dir)
            vectorstore_dir.mkdir(parents=True, exist_ok=True)
            print("✓ Cleared vectorstores")
            print(f"  Location: {vectorstore_dir.absolute()}")
            print("  Next run will re-embed all documents")
        except Exception as e:
            print(f"✗ Error clearing vectorstores: {e}")
    else:
        print("⚠️  Vectorstore directory not found (nothing to clear)")

def clear_all():
    """Clear both PDF cache and vectorstores"""
    print("🧹 Clearing all caches and vectorstores...\n")
    clear_pdf_cache()
    print()
    clear_vectorstores()
    print("\n✅ All caches cleared! Next run will rebuild from scratch.")

def show_status():
    """Show current cache and vectorstore status"""
    print("📊 KeyNote Storage Status\n")
    print("="*60)
    
    # PDF Cache
    cache_dir = Path("./cache/processed_pdfs")
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*"))
        if cache_files:
            print(f"📂 PDF Cache: {len(cache_files)} files")
            print(f"   Location: {cache_dir.absolute()}")
            for f in cache_files:
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"   - {f.name} ({size_mb:.2f} MB)")
        else:
            print("📂 PDF Cache: Empty")
    else:
        print("📂 PDF Cache: Not initialized")
    
    print()
    
    # Vectorstores
    vectorstore_dir = Path("./vectorstore")
    if vectorstore_dir.exists():
        vectorstore_size = sum(f.stat().st_size for f in vectorstore_dir.rglob("*") if f.is_file())
        vectorstore_size_mb = vectorstore_size / (1024 * 1024)
        collections = [d.name for d in vectorstore_dir.iterdir() if d.is_dir()]
        
        print(f"🗄️  Vectorstores: {vectorstore_size_mb:.2f} MB")
        print(f"   Location: {vectorstore_dir.absolute()}")
        if collections:
            print(f"   Collections: {', '.join(collections)}")
        else:
            print("   Collections: None found")
    else:
        print("🗄️  Vectorstores: Not initialized")
    
    print()
    
    # Data sources
    print("📚 Data Sources:")
    
    progressions_path = Path("data/theorytab/progressions.csv")
    if progressions_path.exists():
        import pandas as pd
        try:
            df = pd.read_csv(progressions_path)
            print(f"   ✓ Progressions: {len(df)} rows")
        except:
            print(f"   ✓ Progressions: File exists (could not read)")
    else:
        print("   ✗ Progressions: Not found")
    
    pdfs_path = Path("data/pdfs")
    if pdfs_path.exists():
        pdf_files = list(pdfs_path.glob("*.pdf"))
        print(f"   ✓ PDFs: {len(pdf_files)} files")
    else:
        print("   ✗ PDFs: Directory not found")
    
    print("="*60)

def show_help():
    """Show usage help"""
    print("""
KeyNote Maintenance Utility
===========================

Usage: python maintenance.py [command]

Commands:
  clear-cache       Clear PDF processing cache
  clear-vectors     Clear Qdrant vectorstores
  clear-all         Clear everything (cache + vectorstores)
  status            Show current storage status
  help              Show this help message

Examples:
  python maintenance.py status
  python maintenance.py clear-all
  python maintenance.py clear-cache

Note: After clearing, the next app start will rebuild everything.
      First run: 2-5 minutes (vision API + embeddings)
      Subsequent runs: <5 seconds (cached)
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'clear-cache': clear_pdf_cache,
        'clear-vectors': clear_vectorstores,
        'clear-all': clear_all,
        'status': show_status,
        'help': show_help,
        '--help': show_help,
        '-h': show_help,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python maintenance.py help' for usage")

if __name__ == "__main__":
    main()

