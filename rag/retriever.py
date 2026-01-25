#!/usr/bin/env python3
"""
检索器模块
负责从向量数据库中检索相关文档
"""

from typing import List, Dict, Any, Optional
from rag.embeddings import EmbeddingModel
from rag.vector_store import VectorStore


class DocumentRetriever:
    """文档检索器"""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        top_k: int = 5
    ):
        """
        初始化检索器

        Args:
            embedding_model: 向量化模型
            vector_store: 向量数据库
            top_k: 返回最相关的K个文档
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.top_k = top_k

        print(f"DocumentRetriever initialized (top_k={top_k})")

    def retrieve(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        检索相关文档

        Args:
            query: 查询文本
            **kwargs: 其他参数（如过滤条件）

        Returns:
            检索结果列表
        """
        # 查询扩展：如果检测到特定话题，扩展查询词
        expanded_query = self._expand_query(query)

        # 转换查询为向量
        query_embedding = self.embedding_model.embed_text(expanded_query)

        # 查询
        n_results = kwargs.get('n_results', self.top_k)
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
            where=kwargs.get('where')
        )

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

    def _expand_query(self, query: str) -> str:
        """
        查询扩展：当检测到特定话题时，添加相关关键词
        这样可以提高检索准确度
        """
        # 定义关键词映射
        keyword_mappings = {
            # 预测市场相关
            'polymarket': ['预测市场', '赌博', '博彩', '二元期权', '投注'],
            '预测市场': ['赌博', '博彩', '赌场', '投机'],
            '二元期权': ['赌博', '博彩', '投机'],
            '事件交易': ['赌博', '博彩', '投注'],

            # 衍生品相关
            '衍生品': ['赌博', '投机', '期货', '期权'],
            '期权': ['投机', '赌博'],
            '期货': ['投机', '杠杆'],

            # 投机相关
            '投机': ['赌博', '短期交易'],
        }

        # 检查是否需要扩展
        query_lower = query.lower()
        added_keywords = []

        for key, expansions in keyword_mappings.items():
            if key in query_lower:
                # 添加扩展关键词
                added_keywords.extend(expansions)

        # 如果有添加的关键词，构建新查询
        if added_keywords:
            # 去重
            unique_keywords = list(set(added_keywords))
            # 添加到原查询
            expanded_query = f"{query} {' '.join(unique_keywords)}"
            return expanded_query

        return query

    def retrieve_with_scores(
        self,
        query: str,
        min_score: float = 0.5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档，并过滤低分结果

        Args:
            query: 查询文本
            min_score: 最小相似度分数（0-1）
            **kwargs: 其他参数

        Returns:
            检索结果列表（已过滤）
        """
        results = self.retrieve(query, **kwargs)

        # 将距离转换为相似度分数（余弦距离 → 相似度）
        for result in results:
            if result['distance'] is not None:
                # 余弦距离：0表示完全相同，2表示完全相反
                # 相似度 = 1 - 距离/2
                result['score'] = 1 - result['distance'] / 2
            else:
                result['score'] = 0.0

        # 过滤低分结果
        filtered_results = [
            r for r in results
            if r['score'] >= min_score
        ]

        return filtered_results

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        将检索结果格式化为上下文文本

        Args:
            results: 检索结果

        Returns:
            格式化的上下文
        """
        context_parts = []

        for i, result in enumerate(results, 1):
            # 添加来源信息
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            year = metadata.get('year', '')
            title = metadata.get('title', '')

            # 格式化来源
            if year:
                source_line = f"[来源: {source}, {year}]"
            else:
                source_line = f"[来源: {source}]"

            # 添加文本
            text = result['text']

            # 组合
            context_parts.append(f"{source_line}\n{text}")

        return "\n\n---\n\n".join(context_parts)


# 便捷函数
def get_retriever(
    embedding_model: EmbeddingModel,
    vector_store: VectorStore,
    top_k: int = 5
) -> DocumentRetriever:
    """获取检索器实例"""
    return DocumentRetriever(embedding_model, vector_store, top_k)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("DocumentRetriever Test")
    print("=" * 60)

    # 导入模块
    from rag.embeddings import get_embedding_model
    from rag.vector_store import VectorStore

    # 创建模型和数据库
    embedding_model = get_embedding_model()
    vector_store = VectorStore()

    # 加载已有数据库
    if not vector_store.get_collection():
        print("No existing collection found. Creating test data...")
        vector_store.create_collection()

        # 添加测试数据
        test_texts = [
            "巴菲特是价值投资的代表人物，强调长期持有优质企业",
            "芒格主张多学科思维，使用普世智慧解决问题",
            "护城河是企业保持竞争优势的关键",
            "投资要在别人贪婪时恐惧，在别人恐惧时贪婪"
        ]

        test_embeddings = embedding_model.embed_texts(test_texts)

        vector_store.add_documents(
            texts=test_texts,
            embeddings=test_embeddings,
            metadatas=[
                {"source": "巴菲特股东信", "year": "1965"},
                {"source": "芒格讲话", "year": "1994"},
                {"source": "巴菲特股东信", "year": "1985"},
                {"source": "巴菲特股东信", "year": "1986"}
            ]
        )

    # 创建检索器
    retriever = get_retriever(embedding_model, vector_store, top_k=3)

    # 测试检索
    print("\n1. Test retrieve:")
    query = "什么是价值投资？"
    print(f"Query: {query}\n")

    results = retriever.retrieve(query)

    print(f"Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Text: {result['text'][:80]}...")
        print(f"  Distance: {result['distance']:.4f}")
        print(f"  Metadata: {result['metadata']}")
        print()

    # 测试带分数的检索
    print("\n2. Test retrieve with scores:")
    results_with_scores = retriever.retrieve_with_scores(query, min_score=0.3)

    print(f"Found {len(results_with_scores)} results (score >= 0.3):\n")
    for i, result in enumerate(results_with_scores, 1):
        print(f"Result {i}:")
        print(f"  Text: {result['text'][:80]}...")
        print(f"  Score: {result['score']:.4f}")
        print()

    # 测试格式化上下文
    print("\n3. Test format context:")
    context = retriever.format_context(results[:2])
    print("Formatted context:")
    print("-" * 60)
    print(context[:500] + "...")
    print("-" * 60)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
