from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

load_dotenv()

# Persistent storage directory for Qdrant
VECTORSTORE_DIR = Path("./vectorstore")
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

class ChordProgressionRAG:
    def __init__(self, pdf_chunks, progressions_csv_path, use_persistent_storage=True):
        print("\n🎵 Initializing KeyNote RAG with Qdrant...")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.use_persistent_storage = use_persistent_storage
        
        # Initialize Qdrant client
        if use_persistent_storage:
            print(f"💾 Using persistent storage at {VECTORSTORE_DIR}")
            self.qdrant_client = QdrantClient(path=str(VECTORSTORE_DIR))
        else:
            print("🧠 Using in-memory storage")
            self.qdrant_client = QdrantClient(location=":memory:")
        
        # Create or load PDF vectorstore
        self.pdf_vectorstore = self._initialize_pdf_vectorstore(pdf_chunks)
        
        # Load progression data
        print("🎸 Loading progression database...")
        self.progressions_df = pd.read_csv(progressions_csv_path)
        print(f"   ✓ Loaded {len(self.progressions_df)} progressions")
        
        # Create or load progression vectorstore
        self.progression_vectorstore = self._initialize_progression_vectorstore()
        
        print("✓ KeyNote RAG ready!\n")
    
    def _initialize_pdf_vectorstore(self, pdf_chunks):
        """Initialize or load PDF vectorstore"""
        collection_name = "keynote_pdfs"
        
        if pdf_chunks and len(pdf_chunks) > 0:
            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)
            
            if collection_exists and self.use_persistent_storage:
                print(f"📖 Loading existing PDF vectorstore ({collection_name})...")
                vectorstore = Qdrant(
                    client=self.qdrant_client,
                    collection_name=collection_name,
                    embeddings=self.embeddings
                )
                print(f"   ✓ Loaded existing collection with {self.qdrant_client.count(collection_name).count} vectors")
            else:
                print("📖 Creating PDF vectorstore...")
                vectorstore = Qdrant.from_documents(
                    pdf_chunks,
                    self.embeddings,
                    client=self.qdrant_client,
                    collection_name=collection_name
                )
                print(f"   ✓ Indexed {len(pdf_chunks)} PDF chunks")
            
            return vectorstore
        else:
            print("   ⚠️  No PDF chunks provided")
            return None
    
    def _initialize_progression_vectorstore(self):
        """Initialize or load progression vectorstore"""
        collection_name = "keynote_progressions"
        
        # Check if collection exists
        collections = self.qdrant_client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)
        
        if collection_exists and self.use_persistent_storage:
            print(f"🔍 Loading existing progression vectorstore ({collection_name})...")
            vectorstore = Qdrant(
                client=self.qdrant_client,
                collection_name=collection_name,
                embeddings=self.embeddings
            )
            print(f"   ✓ Loaded existing collection with {self.qdrant_client.count(collection_name).count} vectors")
        else:
            print("🔍 Creating progression vectorstore...")
            
            progression_docs = []
            for _, row in self.progressions_df.iterrows():
                text = f"Progression: {row['progression_roman']}. "
                text += f"Chords: {row['chords_example']}. "
                text += f"Frequency: {row['frequency']}. "
                text += f"Genres: {row['genres']}. "
                text += f"Mood: {row['mood']}. "
                text += f"Famous songs: {row['example_songs']}"
                
                doc = Document(
                    page_content=text,
                    metadata=row.to_dict()
                )
                progression_docs.append(doc)
            
            vectorstore = Qdrant.from_documents(
                progression_docs,
                self.embeddings,
                client=self.qdrant_client,
                collection_name=collection_name
            )
            print(f"   ✓ Indexed {len(progression_docs)} progressions")
        
        return vectorstore
    
    def search_progressions(self, query, k=5):
        """Search for relevant chord progressions"""
        return self.progression_vectorstore.similarity_search(query, k=k)
    
    def search_progressions_with_filter(self, query, genre_filter=None, k=5):
        """
        Advanced retrieval: Search with metadata filtering
        This is your "advanced retrieval technique" for Task 6
        """
        if genre_filter:
            # Qdrant supports metadata filtering
            filter_dict = {"genres": genre_filter}
            return self.progression_vectorstore.similarity_search(
                query, 
                k=k,
                filter=filter_dict
            )
        return self.search_progressions(query, k)
    
    def get_theory_context(self, query, k=3):
        """Get relevant music theory context from PDFs"""
        if not self.pdf_vectorstore:
            return []
        return self.pdf_vectorstore.similarity_search(query, k=k)
    
    def search_all(self, query, k=5, pdf_k=None, progression_k=None):
        """
        NEW: Unified search across both PDF and progression vectorstores
        
        Args:
            query: Search query
            k: Total number of results to return
            pdf_k: Number of results from PDF store (default: k//2)
            progression_k: Number of results from progression store (default: k//2)
        
        Returns:
            Dictionary with separate results from each store and combined results
        """
        if pdf_k is None:
            pdf_k = k // 2
        if progression_k is None:
            progression_k = k - pdf_k  # Ensures total equals k
        
        results = {
            'pdf_results': [],
            'progression_results': [],
            'combined_results': []
        }
        
        # Search PDFs
        if self.pdf_vectorstore:
            pdf_results = self.pdf_vectorstore.similarity_search(query, k=pdf_k)
            results['pdf_results'] = pdf_results
            results['combined_results'].extend(pdf_results)
        
        # Search progressions
        progression_results = self.progression_vectorstore.similarity_search(query, k=progression_k)
        results['progression_results'] = progression_results
        results['combined_results'].extend(progression_results)
        
        return results
    
    def search_all_with_scores(self, query, k=5, pdf_k=None, progression_k=None):
        """
        Unified search with similarity scores for better ranking
        
        Returns results sorted by relevance score across both vectorstores
        """
        if pdf_k is None:
            pdf_k = k // 2
        if progression_k is None:
            progression_k = k - pdf_k
        
        all_results = []
        
        # Search PDFs with scores
        if self.pdf_vectorstore:
            pdf_results = self.pdf_vectorstore.similarity_search_with_score(query, k=pdf_k)
            for doc, score in pdf_results:
                doc.metadata['source_type'] = 'pdf'
                doc.metadata['relevance_score'] = score
                all_results.append((doc, score))
        
        # Search progressions with scores
        progression_results = self.progression_vectorstore.similarity_search_with_score(query, k=progression_k)
        for doc, score in progression_results:
            doc.metadata['source_type'] = 'progression'
            doc.metadata['relevance_score'] = score
            all_results.append((doc, score))
        
        # Sort by score (lower is better for cosine distance)
        all_results.sort(key=lambda x: x[1])
        
        # Take top k
        top_results = all_results[:k]
        
        return {
            'results': [doc for doc, score in top_results],
            'scores': [score for doc, score in top_results]
        }

    def search_progressions_with_metadata_filter(self, query, genre=None, mood=None, k=5):
        """
        TECHNIQUE 1: Metadata Filtering
        Filter by genre and/or mood before semantic search
        """
        from qdrant_client.models import Filter, FieldCondition, MatchAny
        
        if not (genre or mood):
            return self.search_progressions(query, k)
        
        # Build filter conditions
        must_conditions = []
        
        if genre:
            # Check if genre is in the comma-separated genres field
            filtered_df = self.progressions_df[
                self.progressions_df['genres'].str.contains(genre, case=False, na=False)
            ]
        
        if mood:
            # Check if mood is in the comma-separated moods field  
            if genre:
                filtered_df = filtered_df[
                    filtered_df['mood'].str.contains(mood, case=False, na=False)
                ]
            else:
                filtered_df = self.progressions_df[
                    self.progressions_df['mood'].str.contains(mood, case=False, na=False)
                ]
        
        if len(filtered_df) == 0:
            print(f"⚠️  No progressions found with genre={genre}, mood={mood}. Using unfiltered search.")
            return self.search_progressions(query, k)
        
        # Create filtered documents for search
        filtered_docs = []
        from langchain_core.documents import Document
        
        for _, row in filtered_df.iterrows():
            text = f"Progression: {row['progression_roman']}. "
            text += f"Chords: {row['chords_example']}. "
            text += f"Frequency: {row['frequency']}. "
            text += f"Genres: {row['genres']}. "
            text += f"Mood: {row['mood']}. "
            text += f"Famous songs: {row['example_songs']}"
            
            doc = Document(page_content=text, metadata=row.to_dict())
            filtered_docs.append(doc)
        
        # Embed and search within filtered set
        embeddings_list = self.embeddings.embed_documents([d.page_content for d in filtered_docs])
        query_embedding = self.embeddings.embed_query(query)
        
        # Calculate cosine similarity
        import numpy as np
        similarities = np.dot(embeddings_list, query_embedding)
        
        # Get top k
        top_indices = np.argsort(similarities)[::-1][:k]
        results = [filtered_docs[i] for i in top_indices]
        
        return results
    
    def search_progressions_with_query_expansion(self, query, k=5):
        """
        TECHNIQUE 2: Query Expansion
        Expand the query with related musical terms
        """
        from langchain_openai import ChatOpenAI
        import os
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
        
        expansion_prompt = f"""Given this music query: "{query}"

Expand it with 3-5 related musical terms that would help find similar chord progressions.
Only return the expanded query as a single line of keywords, no explanation.

Example:
Input: "indie folk"
Output: indie folk acoustic singer-songwriter folk-pop intimate

Input: "{query}"
Output:"""
        
        try:
            response = llm.invoke(expansion_prompt)
            expanded_query = response.content.strip()
            print(f"📝 Expanded query: {expanded_query}")
            return self.search_progressions(expanded_query, k)
        except:
            return self.search_progressions(query, k)
    
    def search_progressions_with_reranking(self, query, lyrics_analysis=None, k=5, initial_k=10):
        """
        TECHNIQUE 3: Contextual Reranking
        Retrieve more candidates, then rerank with LLM based on full context
        """
        from langchain_openai import ChatOpenAI
        import os
        
        # Retrieve more candidates than needed
        initial_results = self.search_progressions(query, k=initial_k)
        
        if len(initial_results) <= k:
            return initial_results
        
        # Build context for reranking
        context = f"User query: {query}\n"
        if lyrics_analysis:
            context += f"Lyrics mood: {lyrics_analysis.get('mood', 'N/A')}\n"
            context += f"Lyrics energy: {lyrics_analysis.get('energy', 'N/A')}\n"
            context += f"Lyrics themes: {', '.join(lyrics_analysis.get('themes', []))}\n"
        
        # Ask LLM to rank
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
        
        candidates = []
        for i, doc in enumerate(initial_results):
            candidates.append(f"{i}. {doc.metadata['progression_roman']} - {doc.metadata['mood']} - {doc.metadata['genres']}")
        
        rerank_prompt = f"""{context}

Here are {len(candidates)} chord progressions. Rank them by relevance to the query.
Return ONLY the indices in order of relevance (comma-separated), like: 2,0,5,1,3

{chr(10).join(candidates)}

Top {k} indices:"""
        
        try:
            response = llm.invoke(rerank_prompt)
            indices_str = response.content.strip()
            ranked_indices = [int(i.strip()) for i in indices_str.split(',')[:k]]
            reranked = [initial_results[i] for i in ranked_indices if i < len(initial_results)]
            print(f"🔄 Reranked from {len(initial_results)} to {len(reranked)} results")
            return reranked[:k]
        except Exception as e:
            print(f"⚠️  Reranking failed: {e}, using original order")
            return initial_results[:k]
    
    def search_progressions_hybrid(self, query, k=5):
        """
        TECHNIQUE 4: Hybrid Search (Semantic + Keyword)
        Combines vector similarity with keyword matching
        """
        # Semantic search
        semantic_results = self.search_progressions(query, k=k*2)
        
        # Keyword matching (BM25-style)
        query_terms = query.lower().split()
        keyword_scores = []
        
        for doc in semantic_results:
            text = doc.page_content.lower()
            score = sum(text.count(term) for term in query_terms)
            keyword_scores.append(score)
        
        # Combine scores (normalize and average)
        import numpy as np
        if max(keyword_scores) > 0:
            keyword_scores = np.array(keyword_scores) / max(keyword_scores)
        else:
            keyword_scores = np.zeros(len(keyword_scores))
        
        # Semantic scores (inverse rank)
        semantic_scores = np.array([1.0 / (i+1) for i in range(len(semantic_results))])
        semantic_scores = semantic_scores / max(semantic_scores)
        
        # Weighted combination (60% semantic, 40% keyword)
        combined_scores = 0.6 * semantic_scores + 0.4 * keyword_scores
        
        # Sort by combined score
        top_indices = np.argsort(combined_scores)[::-1][:k]
        hybrid_results = [semantic_results[i] for i in top_indices]
        
        return hybrid_results
    
    def search_progressions_dynamic_k(self, query, lyrics_analysis=None, min_k=3, max_k=8):
        """
        TECHNIQUE 5: Dynamic k-value
        Adjust retrieval count based on query specificity
        """
        # Determine query specificity
        query_lower = query.lower()
        
        # Very specific queries (mentions specific progressions or keys)
        if any(term in query_lower for term in ['i-', 'ii-', 'iii-', 'iv-', 'v-', 'vi-', 'vii-']):
            k = min_k
            print(f"🎯 Specific query detected, using k={k}")
        # Specific genre + mood
        elif lyrics_analysis and len(query.split()) > 3:
            k = min_k + 1
            print(f"🎯 Detailed query with lyrics, using k={k}")
        # Broad queries
        else:
            k = max_k
            print(f"🎯 Broad query detected, using k={k}")
        
        return self.search_progressions(query, k=k)
    
    def search_progressions_by_section(self, section_type, harmonic_needs, emotional_intensity=None, k=3):
        """
        NEW: Section-specific progression search
        Search for progressions tailored to specific song sections (verse, chorus, bridge)
        
        Args:
            section_type: "verse", "chorus", or "bridge"
            harmonic_needs: Description of what the section needs harmonically
            emotional_intensity: Optional 1-10 scale intensity
            k: Number of results
            
        Returns:
            List of relevant progressions for this specific section
        """
        # Build section-specific query
        query = f"{section_type} {harmonic_needs}"
        
        if emotional_intensity:
            # Map intensity to energy descriptors
            if emotional_intensity >= 7:
                energy = "high energy climactic"
            elif emotional_intensity >= 4:
                energy = "moderate build"
            else:
                energy = "subdued intimate"
            query += f" {energy}"
        
        print(f"🎯 Section-specific search for {section_type}: {query[:60]}...")
        
        # Use standard search with enriched query
        results = self.search_progressions(query, k=k)
        
        return results
    
    def search_progressions_by_emotional_arc(self, emotional_arc, overall_mood, k=5):
        """
        NEW: Emotional arc-based search
        Find progressions that match the emotional journey of the song
        
        Args:
            emotional_arc: Description of emotional journey (e.g., "heartbreak to hope")
            overall_mood: Overall mood keywords
            k: Number of results
            
        Returns:
            List of progressions that support the emotional narrative
        """
        # Build arc-aware query
        query = f"{emotional_arc} {overall_mood} emotional journey storytelling"
        
        print(f"📖 Emotional arc search: {emotional_arc[:60]}...")
        
        # Use query expansion for richer semantic understanding
        results = self.search_progressions_with_query_expansion(query, k=k)
        
        return results
    
    def clear_vectorstores(self):
        """Clear all vectorstore collections (useful for rebuilding)"""
        collections = ["keynote_pdfs", "keynote_progressions"]
        for collection_name in collections:
            try:
                self.qdrant_client.delete_collection(collection_name)
                print(f"✓ Deleted collection: {collection_name}")
            except Exception as e:
                print(f"⚠️  Could not delete {collection_name}: {e}")