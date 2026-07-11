"""
Medical RAG System
==================
A professional Retrieval Augmented Generation system for medical Q&A
"""

from src.rag import RAGOrchestrator, create_rag_system
from src.llm import LLMManager, get_llm
from src.retriever import RetrieverManager, build_retriever
from src.preprocessing import DataPreprocessor, preprocess_data
from src.prompts import get_contextualize_prompt, get_qa_prompt
from src.analytics import PatientAnalytics

__version__ = "1.0.0"
__all__ = [
    "RAGOrchestrator",
    "create_rag_system",
    "LLMManager",
    "get_llm",
    "RetrieverManager",
    "build_retriever",
    "DataPreprocessor",
    "preprocess_data",
    "get_contextualize_prompt",
    "get_qa_prompt",
    "PatientAnalytics",
]