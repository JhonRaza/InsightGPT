"""
Embeddings and vector search utilities for InsightGPT
Handles document embedding generation and similarity search using FAISS
"""
from typing import List, Tuple
import numpy as np
import faiss
import openai
import streamlit as st
from config import Config


class EmbeddingStore:
    """Manage document embeddings and similarity search"""
    
    def __init__(self, api_key: str):
        """
        Initialize embedding store
        
        Args:
            api_key: OpenAI API key for generating embeddings
        """
        self.config = Config()
        self.api_key = api_key
        openai.api_key = api_key
        
        self.chunks = []
        self.index = None
        self.dimension = self.config.EMBEDDING_DIMENSION
    
    def create_embeddings(self, text_chunks: List[str]) -> bool:
        """
        Create embeddings for text chunks and build FAISS index
        
        Args:
            text_chunks: List of text chunks to embed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not text_chunks:
                st.error("No text chunks provided for embedding")
                return False
            
            self.chunks = text_chunks
            embeddings = []
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Generate embeddings in batches
            batch_size = 10
            total_batches = (len(text_chunks) + batch_size - 1) // batch_size
            
            for i in range(0, len(text_chunks), batch_size):
                batch = text_chunks[i:i + batch_size]
                current_batch = i // batch_size + 1
                
                status_text.text(f"Generating embeddings... ({current_batch}/{total_batches})")
                
                try:
                    batch_embeddings = self._get_embeddings_batch(batch)
                    embeddings.extend(batch_embeddings)
                    
                    # Update progress
                    progress = min(1.0, (i + batch_size) / len(text_chunks))
                    progress_bar.progress(progress)
                    
                except Exception as e:
                    st.error(f"Error generating embeddings for batch {current_batch}: {str(e)}")
                    return False
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype='float32')
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_array)
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            self.index.add(embeddings_array)
            
            return True
            
        except Exception as e:
            st.error(f"Error creating embeddings: {str(e)}")
            return False
    
    def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a batch of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        response = openai.embeddings.create(
            model=self.config.EMBEDDING_MODEL,
            input=texts
        )
        
        return [item.embedding for item in response.data]
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[str, float]]:
        """
        Search for most similar chunks to query
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of tuples (chunk_text, similarity_score)
        """
        try:
            if self.index is None or not self.chunks:
                st.error("No embeddings available. Please process a document first.")
                return []
            
            top_k = top_k or self.config.TOP_K_RESULTS
            top_k = min(top_k, len(self.chunks))  # Don't exceed available chunks
            
            # Generate query embedding
            query_embedding = self._get_embeddings_batch([query])[0]
            query_vector = np.array([query_embedding], dtype='float32')
            faiss.normalize_L2(query_vector)
            
            # Search
            distances, indices = self.index.search(query_vector, top_k)
            
            # Return results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.chunks):
                    results.append((self.chunks[idx], float(distance)))
            
            return results
            
        except Exception as e:
            st.error(f"Error searching embeddings: {str(e)}")
            return []
    
    def get_all_chunks(self) -> List[str]:
        """Get all stored text chunks"""
        return self.chunks.copy()
    
    def is_ready(self) -> bool:
        """Check if embedding store is ready for search"""
        return self.index is not None and len(self.chunks) > 0
    
    def get_stats(self) -> dict:
        """Get statistics about the embedding store"""
        return {
            'total_chunks': len(self.chunks),
            'embedding_dimension': self.dimension,
            'index_ready': self.is_ready()
        }


def format_search_results(results: List[Tuple[str, float]]) -> str:
    """
    Format search results for display
    
    Args:
        results: List of (chunk_text, similarity_score) tuples
        
    Returns:
        Formatted string
    """
    if not results:
        return "No relevant content found."
    
    formatted = []
    for i, (chunk, score) in enumerate(results, 1):
        formatted.append(f"**Result {i}** (Relevance: {score:.3f})\n{chunk}\n")
    
    return "\n---\n\n".join(formatted)


def merge_overlapping_chunks(chunks: List[str], similarity_threshold: float = 0.8) -> List[str]:
    """
    Remove highly similar overlapping chunks to reduce redundancy
    
    Args:
        chunks: List of text chunks
        similarity_threshold: Threshold for considering chunks as duplicates
        
    Returns:
        Deduplicated list of chunks
    """
    if len(chunks) <= 1:
        return chunks
    
    # Simple deduplication based on exact matches and high overlap
    unique_chunks = []
    seen = set()
    
    for chunk in chunks:
        # Create a normalized version for comparison
        normalized = ' '.join(chunk.lower().split())
        
        # Check if we've seen this chunk or a very similar one
        is_duplicate = False
        for seen_chunk in seen:
            # Calculate simple overlap
            overlap = len(set(normalized.split()) & set(seen_chunk.split()))
            total = len(set(normalized.split()) | set(seen_chunk.split()))
            
            if total > 0 and overlap / total > similarity_threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_chunks.append(chunk)
            seen.add(normalized)
    
    return unique_chunks
