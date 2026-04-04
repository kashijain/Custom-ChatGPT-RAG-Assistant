from __future__ import annotations

import pickle
import threading
from pathlib import Path

import faiss
import numpy as np


class FAISSVectorStore:
    def __init__(self, index_path: Path, metadata_path: Path) -> None:
        self.index_path = index_path
        self.metadata_path = metadata_path
        self._lock = threading.Lock()
        self._index: faiss.Index | None = None
        self._metadata: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.index_path.exists() and self.metadata_path.exists():
            self._index = faiss.read_index(str(self.index_path))
            with self.metadata_path.open("rb") as file:
                self._metadata = pickle.load(file)

    def _save(self) -> None:
        if self._index is None:
            return
        faiss.write_index(self._index, str(self.index_path))
        with self.metadata_path.open("wb") as file:
            pickle.dump(self._metadata, file)

    @staticmethod
    def _normalize_vectors(vectors: list[list[float]]) -> np.ndarray:
        matrix = np.array(vectors, dtype=np.float32)
        faiss.normalize_L2(matrix)
        return matrix

    def add_chunks(self, embeddings: list[list[float]], metadata: list[dict]) -> int:
        if not embeddings:
            return 0
        if len(embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata must have the same length.")

        matrix = self._normalize_vectors(embeddings)

        with self._lock:
            if self._index is None:
                self._index = faiss.IndexFlatIP(matrix.shape[1])
            elif self._index.d != matrix.shape[1]:
                raise ValueError("Embedding dimension does not match existing FAISS index.")

            self._index.add(matrix)
            self._metadata.extend(metadata)
            self._save()

        return len(metadata)

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        document_id: str | None = None,
    ) -> list[dict]:
        query_matrix = self._normalize_vectors([query_embedding])

        with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return []

            search_k = min(max(top_k * 5, top_k), self._index.ntotal)
            scores, indices = self._index.search(query_matrix, search_k)

            results: list[dict] = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                item = dict(self._metadata[idx])
                if document_id and item.get("document_id") != document_id:
                    continue
                item["score"] = float(score)
                results.append(item)
                if len(results) >= top_k:
                    break

        return results
