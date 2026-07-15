"""
Retriever Module
================
Handles document embedding and retrieval
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from src.config import EMBEDDING_MODEL, DEVICE, TOP_K_RESULTS, SEARCH_TYPE, FAISS_INDEX_DIR


class RetrieverManager:
    """
    Manages the retrieval system
    Handles embedding and vector search, with on-disk FAISS caching
    """
    
    _instance = None
    _retriever = None
    _vectorstore = None
    _embeddings = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get or create the embeddings model (loaded once)"""
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": DEVICE},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings
    
    def _index_exists(self, index_dir: str = None) -> bool:
        """Check whether a cached FAISS index is present on disk"""
        index_dir = index_dir or FAISS_INDEX_DIR
        return os.path.exists(os.path.join(index_dir, "index.faiss")) and \
            os.path.exists(os.path.join(index_dir, "index.pkl"))
    
    def build_retriever(
        self,
        documents: list[Document] = None,
        index_dir: str = None,
        force_rebuild: bool = False,
    ) -> BaseRetriever:
        """
        Get the retriever, loading a cached FAISS index from disk when
        available instead of re-embedding all documents from scratch.
        
        Args:
            documents: List of document chunks to index (needed if no cache exists)
            index_dir: Directory to read/write the FAISS index (defaults to config value)
            force_rebuild: If True, ignore any cached index and rebuild from documents
            
        Returns:
            BaseRetriever: Configured retriever
        """
        if self._retriever is not None and not force_rebuild:
            return self._retriever
        
        index_dir = index_dir or FAISS_INDEX_DIR
        embeddings = self._get_embeddings()
        
        if not force_rebuild and self._index_exists(index_dir):
            self._vectorstore = FAISS.load_local(
                index_dir,
                embeddings,
                allow_dangerous_deserialization=True,
            )
        else:
            if not documents:
                raise ValueError(
                    "No cached FAISS index found and no documents were provided to build one."
                )
            self._vectorstore = FAISS.from_documents(documents, embeddings)
            
            os.makedirs(index_dir, exist_ok=True)
            self._vectorstore.save_local(index_dir)
        
        self._retriever = self._vectorstore.as_retriever(
            search_type=SEARCH_TYPE,
            search_kwargs={"k": TOP_K_RESULTS},
        )

        return self._retriever
    
    def get_vectorstore(self):
        """Get the vectorstore for saving/loading"""
        return self._vectorstore
    
    def clear(self, delete_cache: bool = False, index_dir: str = None):
        """
        Clear the retriever instance from memory
        
        Args:
            delete_cache: If True, also delete the on-disk FAISS index
            index_dir: Directory of the cached index to delete
        """
        self._retriever = None
        self._vectorstore = None
        
        if delete_cache:
            import shutil
            index_dir = index_dir or FAISS_INDEX_DIR
            if os.path.exists(index_dir):
                shutil.rmtree(index_dir)


# Convenience function
def build_retriever(documents: list[Document] = None, force_rebuild: bool = False) -> BaseRetriever:
    """Build and return the retriever, using a cached FAISS index when available"""
    return RetrieverManager().build_retriever(documents, force_rebuild=force_rebuild)