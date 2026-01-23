"""
RAG系统核心模块
Retrieval-Augmented Generation for Buffett and Munger AI
"""

__version__ = "0.1.0"

from .embeddings import EmbeddingModel, get_embedding_model
from .vector_store import VectorStore
from .retriever import DocumentRetriever, get_retriever
from .generator import AnswerGenerator, get_generator
from .pipeline import RAGPipeline, get_rag_pipeline
from .conversation import Conversation, ConversationManager, get_conversation_manager
from .search import WebSearcher, EnhancedRAGWithSearch, get_web_searcher, get_enhanced_rag
