"""
RAG Orchestrator Module
=======================
The main orchestrator that connects all components:
- LLM
- Retriever
- Prompts
- Chat History
"""

import os
from typing import Optional
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

from src.llm import LLMManager
from src.retriever import RetrieverManager
from src.preprocessing import DataPreprocessor
from src.prompts import get_contextualize_prompt, get_qa_prompt
from src.analytics import PatientAnalytics
from src.config import DEVICE, PATIENT_CSV_PATH


class RAGOrchestrator:
    """
    Main orchestrator for the RAG system
    Connects LLM, Retriever, and Prompts together
    """
    
    def __init__(
        self,
        llm: Optional[ChatGroq] = None,
        retriever: Optional[BaseRetriever] = None,
        documents: Optional[list[Document]] = None,
        analytics: Optional[PatientAnalytics] = None,
    ):
        """
        Initialize the RAG Orchestrator
        
        Args:
            llm: Pre-loaded LLM instance (will create one if None)
            retriever: Pre-built retriever (will create one if None)
            documents: Documents to index (required if retriever is None)
            analytics: Optional PatientAnalytics instance for structured
                (text-to-pandas) answers to statistical questions
        """
        self.llm = llm or LLMManager().get_llm()
        self.retriever = retriever
        self.analytics = analytics
        self.conversational_chain = None
        self._session_store: dict[str, InMemoryChatMessageHistory] = {}
        
        # Build retriever if documents provided and no retriever
        if self.retriever is None and documents is not None:
            self.retriever = RetrieverManager().build_retriever(documents)
        
        # Build the chain if retriever is available
        if self.retriever is not None:
            self._build_chain()
    
    def _build_chain(self):
        """Build the complete RAG chain with conversation history"""
        
        print("🔗 Building RAG chain...")
        
        # Step 1: Create history-aware retriever
        # This rewrites questions using chat history for better retrieval
        history_aware_retriever = create_history_aware_retriever(
            llm=self.llm,
            retriever=self.retriever,
            prompt=get_contextualize_prompt(),
        )
        
        # Step 2: Create QA chain
        # This answers questions using retrieved documents
        question_answer_chain = create_stuff_documents_chain(
            llm=self.llm,
            prompt=get_qa_prompt(),
        )
        
        # Step 3: Combine into retrieval chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain,
        )
        
        # Step 4: Add conversation history support
        self.conversational_chain = RunnableWithMessageHistory(
            rag_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        
        print("✅ RAG chain built successfully!")
    
    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create chat history for a session"""
        if session_id not in self._session_store:
            self._session_store[session_id] = InMemoryChatMessageHistory()
        return self._session_store[session_id]
    
    def run(
        self,
        question: str,
        session_id: str = "default",
    ) -> str:
        """
        Run the RAG system with a question
        
        Statistical / structured-data questions (e.g. "how many patients have
        diabetes?") are routed to the analytics layer first for an exact,
        directly-computed answer. If that layer can't confidently answer
        (or the question isn't a match), it falls back to the normal RAG chain.
        
        Args:
            question: User's question
            session_id: Session ID for chat history
            
        Returns:
            str: Generated answer
        """
        if self.conversational_chain is None:
            raise ValueError("RAG chain not built! Provide retriever or documents.")
        
        # Try the structured analytics layer first for statistical questions
        if self.analytics is not None and self.analytics.is_statistical_query(question):
            analytics_answer = self.analytics.answer(question, self.llm)
            if analytics_answer is not None:
                # Keep chat history in sync so follow-up questions have context
                history = self._get_session_history(session_id)
                history.add_user_message(question)
                history.add_ai_message(analytics_answer)
                return analytics_answer
            print("↩️ Analytics layer couldn't answer confidently — falling back to RAG")
        
        # Invoke the RAG chain
        response = self.conversational_chain.invoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}},
        )
        
        return response.get("answer", "No answer generated.")
    
    def clear_session(self, session_id: str = "default"):
        """Clear chat history for a specific session"""
        if session_id in self._session_store:
            del self._session_store[session_id]
            print(f"🧹 Cleared session: {session_id}")
    
    def clear_all_sessions(self):
        """Clear all chat histories"""
        self._session_store.clear()
        print("🧹 Cleared all sessions")
    
    @classmethod
    def from_data_directory(
        cls,
        data_dir: str = None,
        llm: Optional[ChatGroq] = None,
        force_rebuild: bool = False,
    ) -> "RAGOrchestrator":
        """
        Factory method to create RAGOrchestrator from data directory.
        
        If a cached FAISS index already exists on disk, documents are NOT
        re-loaded/re-split/re-embedded — the cached index is loaded directly,
        which is much faster on repeat startups.
        
        Args:
            data_dir: Path to data directory
            llm: Optional pre-loaded LLM
            force_rebuild: If True, ignore any cached index and reprocess data_dir
            
        Returns:
            RAGOrchestrator: Configured instance
        """
        retriever_manager = RetrieverManager()
        analytics = cls._load_analytics()
        
        if not force_rebuild and retriever_manager._index_exists():
            # Fast path: skip loading/splitting documents entirely
            print("⚡ Cached FAISS index detected — skipping data preprocessing")
            retriever = retriever_manager.build_retriever()
            return cls(llm=llm, retriever=retriever, analytics=analytics)
        
        # Slow path: no cache (or forced) — preprocess data and build a fresh index
        preprocessor = DataPreprocessor(data_dir)
        documents = preprocessor.process()
        retriever = retriever_manager.build_retriever(documents, force_rebuild=force_rebuild)
        
        return cls(llm=llm, retriever=retriever, analytics=analytics)
    
    @staticmethod
    def _load_analytics() -> Optional[PatientAnalytics]:
        """Load the patient analytics layer if the CSV is present on disk"""
        if not os.path.exists(PATIENT_CSV_PATH):
            print(f"ℹ️ No patient CSV found at '{PATIENT_CSV_PATH}' — analytics layer disabled")
            return None
        try:
            analytics = PatientAnalytics(PATIENT_CSV_PATH)
            print(f"📊 Analytics layer ready ({len(analytics.df):,} patient records)")
            return analytics
        except Exception as e:
            print(f"⚠️ Could not load analytics layer: {e}")
            return None


# Convenience function
def create_rag_system(
    documents: list[Document] = None,
    data_dir: str = None,
    llm: ChatGroq = None,
) -> RAGOrchestrator:
    """
    Create a complete RAG system
    
    Args:
        documents: Pre-processed documents
        data_dir: Directory to load data from (if no documents)
        llm: Pre-loaded LLM (will create one if None)
        
    Returns:
        RAGOrchestrator: Ready-to-use RAG system
    """
    if documents is None and data_dir is not None:
        preprocessor = DataPreprocessor(data_dir)
        documents = preprocessor.process()
    
    if documents is None:
        raise ValueError("Either documents or data_dir must be provided")
    
    return RAGOrchestrator(llm=llm, documents=documents)