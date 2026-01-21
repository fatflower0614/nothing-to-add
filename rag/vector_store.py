#!/usr/bin/env python3
"""
向量数据库模块
使用ChromaDB存储和检索向量
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os


class VectorStore:
    """向量数据库管理"""

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "buffett_munger_docs"
    ):
        """
        初始化向量数据库

        Args:
            persist_directory: 数据存储路径
            collection_name: 集合名称
        """
        # 创建目录
        os.makedirs(persist_directory, exist_ok=True)

        # 创建客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.collection_name = collection_name
        self.collection = None

        print(f"VectorStore initialized at: {persist_directory}")

    def create_collection(self):
        """创建新集合"""
        # 删除已存在的集合（如果需要）
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Deleted existing collection: {self.collection_name}")
        except Exception:
            pass

        # 创建新集合
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        print(f"Created new collection: {self.collection_name}")

    def get_collection(self):
        """获取已存在的集合"""
        try:
            self.collection = self.client.get_collection(self.collection_name)
            count = self.collection.count()
            print(f"Loaded collection '{self.collection_name}' with {count} documents")
            return True
        except Exception as e:
            print(f"Collection '{self.collection_name}' not found: {e}")
            return False

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        添加文档到数据库

        Args:
            texts: 文本列表
            embeddings: 向量列表
            metadatas: 元数据列表
            ids: 文档ID列表
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call create_collection() first.")

        # 自动生成ID
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]

        # 添加文档
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(texts)} documents to collection")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        查询相似文档

        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            where: 过滤条件

        Returns:
            查询结果
        """
        if self.collection is None:
            raise ValueError("Collection not initialized. Call get_collection() first.")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        return results

    def query_by_text(
        self,
        query_text: str,
        embedding_model,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        通过文本查询（自动转换为向量）

        Args:
            query_text: 查询文本
            embedding_model: 向量化模型
            n_results: 返回结果数量

        Returns:
            结果列表
        """
        # 转换成向量
        query_embedding = embedding_model.embed_text(query_text)

        # 查询
        results = self.query(query_embedding, n_results)

        # 格式化结果
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'id': results['ids'][0][i] if 'ids' in results else None
                })

        return formatted_results

    def count(self) -> int:
        """获取文档数量"""
        if self.collection is None:
            return 0
        return self.collection.count()

    def reset(self):
        """重置数据库（删除所有数据）"""
        self.client.reset()
        print("Vector store reset")


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("VectorStore Test")
    print("=" * 60)

    # 导入向量化模型
    from rag.embeddings import get_embedding_model

    # 创建向量数据库
    vector_store = VectorStore()

    # 创建新集合
    vector_store.create_collection()

    # 创建向量化模型
    embedding_model = get_embedding_model()

    # 测试数据
    test_texts = [
        "巴菲特是价值投资的代表人物",
        "芒格强调多学科思维",
        "长期持有优质股票是成功的关键",
        "今天的天气很好"  # 不相关
    ]

    test_embeddings = embedding_model.embed_texts(test_texts)

    # 添加文档
    print("\n1. Adding documents...")
    vector_store.add_documents(
        texts=test_texts,
        embeddings=test_embeddings,
        metadatas=[
            {"source": "test", "category": "investment"},
            {"source": "test", "category": "investment"},
            {"source": "test", "category": "investment"},
            {"source": "test", "category": "weather"}
        ]
    )

    # 查询测试
    print("\n2. Query test:")
    query = "什么是价值投资"
    print(f"Query: {query}")

    results = vector_store.query_by_text(query, embedding_model, n_results=3)

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Text: {result['text']}")
        print(f"  Distance: {result['distance']:.4f}")
        print(f"  Metadata: {result['metadata']}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
