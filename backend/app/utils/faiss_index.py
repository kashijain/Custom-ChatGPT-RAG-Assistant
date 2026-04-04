import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple

class FAISSIndex:
    def __init__(self, index_path: str = "faiss_index"):
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "index.faiss")
        self.metadata_file = os.path.join(index_path, "metadata.pkl")
        self.index = None
        self.metadata = []  # List of dicts with chunk text and source
        
        # Ensure directory exists
        os.makedirs(index_path, exist_ok=True)
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and metadata."""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)

    def refresh(self):
        """
        Reload the latest FAISS index from disk.

        Upload and chat routes use separate FAISSIndex instances, so this keeps
        chat in sync immediately after a new upload is indexed.
        """
        self._load_index()

    def get_embedding_mode(self, source: str | None = None) -> str | None:
        """
        Return the embedding mode used for the latest matching document chunk.

        This prevents query/document embedding mismatches when a PDF was indexed
        with fallback embeddings during demo mode.
        """
        self.refresh()

        for metadata in reversed(self.metadata):
            if source and metadata.get("source") != source:
                continue
            return metadata.get("embedding_mode")

        return None
    
    def _save_index(self):
        """Save FAISS index and metadata."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
    
    def add_vectors(self, vectors: List[List[float]], metadata: List[dict]):
        """
        Add vectors to the index.
        
        Args:
            vectors: List of embedding vectors
            metadata: List of metadata dicts (e.g., {'text': chunk, 'source': filename})
        """
        if not vectors:
            return
        
        vectors_array = np.array(vectors, dtype=np.float32)
        
        if self.index is None:
            # Create new index
            dimension = vectors_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(vectors_array)
        self.metadata.extend(metadata)
        self._save_index()
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        source: str | None = None
    ) -> List[Tuple[dict, float]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of (metadata, distance) tuples
        """
        # Refresh from disk so this instance sees documents indexed by upload.py.
        self.refresh()

        if self.index is None or self.index.ntotal == 0:
            return []
        
        query_array = np.array([query_vector], dtype=np.float32)
        search_k = self.index.ntotal if source else min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_array, search_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:  # Valid index
                metadata = self.metadata[idx]
                if source and metadata.get("source") != source:
                    continue
                results.append((metadata, float(dist)))
        
        return results
    
    def clear_index(self):
        """Clear the index and metadata."""
        self.index = None
        self.metadata = []
        if os.path.exists(self.index_file):
            os.remove(self.index_file)
        if os.path.exists(self.metadata_file):
            os.remove(self.metadata_file)
