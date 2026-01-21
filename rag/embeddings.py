#!/usr/bin/env python3
"""
向量化模块
将文本转换成向量（embeddings）
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np


class EmbeddingModel:
    """向量化模型"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化模型

        Args:
            model_name: 模型名称
                - all-MiniLM-L6-v2: 轻量级，快速（推荐）
                - all-mpnet-base-v2: 更准确，但稍慢
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")

    def embed_text(self, text: str) -> List[float]:
        """
        将单个文本转换成向量

        Args:
            text: 输入文本

        Returns:
            向量（列表）
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文本转换成向量

        Args:
            texts: 输入文本列表

        Returns:
            向量列表
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_documents(self, documents: List[dict]) -> List[List[float]]:
        """
        将文档列表转换成向量

        Args:
            documents: 文档列表，每个文档包含 'text' 字段

        Returns:
            向量列表
        """
        texts = [doc['text'] for doc in documents]
        return self.embed_texts(texts)


# 便捷函数
def get_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingModel:
    """获取向量化模型实例"""
    return EmbeddingModel(model_name)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("Embedding Model Test")
    print("=" * 60)

    # 创建模型
    model = get_embedding_model()

    # 测试单个文本
    print("\n1. Test single text:")
    text = "巴菲特是价值投资的代表人物"
    embedding = model.embed_text(text)
    print(f"Text: {text}")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # 测试批量文本
    print("\n2. Test batch texts:")
    texts = [
        "巴菲特是伟大的投资者",
        "价值投资是长期策略",
        "今天天气不错",  # 不相关
    ]
    embeddings = model.embed_texts(texts)

    # 计算相似度
    print("\n3. Similarity calculation:")
    for i, text1 in enumerate(texts):
        for j, text2 in enumerate(texts):
            if i < j:
                vec1 = np.array(embeddings[i])
                vec2 = np.array(embeddings[j])
                # 计算余弦相似度
                similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                print(f"'{text1}' vs '{text2}': {similarity:.4f}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
