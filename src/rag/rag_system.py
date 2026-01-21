"""
RAG系统核心实现
使用LlamaIndex + ChromaDB
"""

from typing import List, Dict, Optional
from pathlib import Path
import os

# LlamaIndex核心
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

# ChromaDB
import chromadb

# 嵌入模型
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# LLM（通过Ollama）
from llama_index.llms.ollama import Ollama


class NothingToAddRAG:
    """Nothing to Add项目的RAG系统"""

    def __init__(
        self,
        data_dir: str = "./data/processed",
        persist_dir: str = "./chroma_db",
        embed_model_name: str = "BAAI/bge-small-en-v1.5",  # 或用中文模型
        llm_model: str = "llama3.1",  # 或 "qwen2.5"
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        """
        初始化RAG系统

        Args:
            data_dir: 数据目录
            persist_dir: ChromaDB持久化目录
            embed_model_name: 嵌入模型名称
            llm_model: LLM模型名称（Ollama）
            chunk_size: 文本分割大小
            chunk_overlap: 文本重叠大小
        """
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 创建必要的目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # 初始化嵌入模型
        print(f"📦 加载嵌入模型: {embed_model_name}")
        self.embed_model = HuggingFaceEmbedding(
            model_name=embed_model_name,
            device="cpu"  # 或 "cuda" 如果有GPU
        )

        # 初始化LLM
        print(f"🤖 初始化LLM: {llm_model}")
        self.llm = Ollama(
            model=llm_model,
            request_timeout=120.0
        )

        # 初始化或加载向量数据库
        self.index = self._load_or_create_index()

    def _load_or_create_index(self) -> VectorStoreIndex:
        """加载或创建向量索引"""

        # 创建ChromaDB客户端
        chroma_client = chromadb.PersistentClient(
            path=str(self.persist_dir)
        )

        # 创建collection
        collection = chroma_client.get_or_create_collection(
            name="nothing_to_add"
        )

        # 创建vector store
        vector_store = ChromaVectorStore(
            chroma_collection=collection
        )

        # 创建storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store
        )

        # 尝试加载现有数据
        if collection.count() > 0:
            print(f"✅ 加载现有索引 ({collection.count()} 个文档)")
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            return index

        # 如果没有数据，创建新索引
        print("📚 创建新索引...")
        documents = self._load_documents()

        if not documents:
            print("⚠️ 警告：没有找到文档，请先添加数据到 data/processed/")
            return None

        # 分割文档
        splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separator="\n"
        )

        # 创建索引
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=self.embed_model,
            transformations=[splitter],
            show_progress=True
        )

        print(f"✅ 索引创建完成！共 {len(documents)} 个文档")
        return index

    def _load_documents(self) -> List:
        """从目录加载所有文档"""
        if not self.data_dir.exists():
            print(f"⚠️ 数据目录不存在: {self.data_dir}")
            return []

        # 读取所有支持的文件
        reader = SimpleDirectoryReader(
            str(self.data_dir),
            recursive=True,
            required_exts=[".txt", ".md", ".pdf"]
        )

        documents = reader.load_data()
        print(f"📄 加载了 {len(documents)} 个文档")

        return documents

    def query(
        self,
        query_text: str,
        mode: str = "buffett",
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> Dict:
        """
        查询RAG系统

        Args:
            query_text: 查询文本
            mode: 对话模式 ("buffett" | "munger" | "dual")
            top_k: 返回的top文档数
            similarity_threshold: 相似度阈值

        Returns:
            包含回答和来源的字典
        """
        if self.index is None:
            return {
                "answer": "抱歉，系统还没有数据。请先添加文档到 data/processed/ 目录。",
                "sources": []
            }

        # 创建查询引擎
        query_engine = self.index.as_query_engine(
            llm=self.llm,
            similarity_top_k=top_k,
            retrieval_mode="hybrid",  # 混合检索
            response_mode="compact",
        )

        # 根据模式添加系统提示
        from src.prompts.prompts import get_prompt
        system_prompt = get_prompt(mode, context="{context}")

        # 执行查询
        response = query_engine.query(query_text)

        # 提取来源
        sources = []
        if hasattr(response, "source_nodes"):
            for node in response.source_nodes:
                metadata = node.metadata
                sources.append({
                    "file": metadata.get("file_name", "Unknown"),
                    "score": node.score if hasattr(node, "score") else 0,
                    "text": node.text[:200] + "..." if len(node.text) > 200 else node.text
                })

        return {
            "answer": str(response),
            "sources": sources,
            "mode": mode
        }

    def add_documents(self, file_paths: List[str]):
        """
        添加新文档到索引

        Args:
            file_paths: 文件路径列表
        """
        # 这里实现增量添加逻辑
        # 简化版本：重新创建索引
        print("📝 添加新文档...")
        # TODO: 实现增量添加
        pass

    def chat(
        self,
        message: str,
        history: List[Dict],
        mode: str = "buffett"
    ) -> str:
        """
        聊天模式（带对话历史）

        Args:
            message: 用户消息
            history: 对话历史
            mode: 对话模式

        Returns:
            AI回复
        """
        # 简单实现：只查询RAG，暂不使用复杂的历史管理
        # 因为巴菲特和芒格"记性不好"
        result = self.query(message, mode=mode)
        return result["answer"]


# ============= 便捷函数 =============

def create_rag_system(
    data_dir: str = "./data/processed",
    mode: str = "buffett"
) -> NothingToAddRAG:
    """
    创建RAG系统的便捷函数

    Args:
        data_dir: 数据目录
        mode: 默认模式

    Returns:
        RAG系统实例
    """
    rag = NothingToAddRAG(data_dir=data_dir)
    return rag


if __name__ == "__main__":
    # 测试代码
    import sys

    print("🚀 Nothing to Add RAG System")
    print("=" * 50)

    # 初始化
    rag = NothingToAddRAG()

    # 测试查询
    test_queries = [
        "什么是价值投资？",
        "如何评估一家公司？",
        "什么是护城河？"
    ]

    for query in test_queries:
        print(f"\n❓ 问题: {query}")
        result = rag.query(query, mode="buffett")
        print(f"🤖 回答: {result['answer'][:200]}...")
        print(f"📚 来源: {len(result['sources'])} 个文档")


# ============= 使用示例 =============

"""
# 初始化
from src.rag.rag_system import NothingToAddRAG

rag = NothingToAddRAG(
    data_dir="./data/processed",
    llm_model="llama3.1"
)

# 查询
result = rag.query(
    "什么是价值投资？",
    mode="buffett"
)

print(result["answer"])
print("来源:")
for source in result["sources"]:
    print(f"  - {source['file']} (相似度: {source['score']:.2f})")
"""
