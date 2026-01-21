#!/usr/bin/env python3
"""
RAG管道
整合所有模块：向量化、检索、生成
"""

from typing import List, Dict, Any, Optional
from rag.embeddings import EmbeddingModel, get_embedding_model
from rag.vector_store import VectorStore
from rag.retriever import DocumentRetriever, get_retriever
from rag.generator import AnswerGenerator, get_generator


class RAGPipeline:
    """RAG完整流程"""

    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        vector_store_path: str = "./data/chroma",
        collection_name: str = "buffett_munger_docs",
        generator_model: str = "glm-4-flash",
        top_k: int = 5
    ):
        """
        初始化RAG流程

        Args:
            embedding_model_name: 向量化模型名称
            vector_store_path: 向量数据库路径
            collection_name: 集合名称
            generator_model: 生成器模型名称
                - GLM: glm-4-flash (默认), glm-4-plus, glm-4-air
                - OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
            top_k: 检索文档数量
        """
        print("=" * 60)
        print("Initializing RAG Pipeline")
        print("=" * 60)

        # 1. 初始化向量化模型
        self.embedding_model = get_embedding_model(embedding_model_name)

        # 2. 初始化向量数据库
        self.vector_store = VectorStore(
            persist_directory=vector_store_path,
            collection_name=collection_name
        )

        # 尝试加载已有数据库
        has_collection = self.vector_store.get_collection()

        if not has_collection:
            print("\n[WARNING] No existing vector database found.")
            print("Please run 'python scripts/build_rag.py' to build the database first.")
        else:
            print(f"Loaded {self.vector_store.count()} documents from vector store")

        # 3. 初始化检索器
        self.retriever = get_retriever(
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
            top_k=top_k
        )

        # 4. 初始化生成器（延迟加载，需要API密钥）
        self.generator = None
        self.generator_model = generator_model

        print("=" * 60)
        print("RAG Pipeline initialized successfully")
        print("=" * 60)

    def init_generator(self, api_key: Optional[str] = None):
        """
        初始化生成器

        Args:
            api_key: OpenAI API密钥
        """
        self.generator = get_generator(
            model=self.generator_model,
            api_key=api_key
        )

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        min_score: float = 0.0,
        format_context: bool = True
    ) -> Dict[str, Any]:
        """
        查询（仅检索，不生成答案）

        Args:
            question: 问题
            top_k: 返回文档数量
            min_score: 最小相似度分数
            format_context: 是否格式化上下文

        Returns:
            查询结果
        """
        # 检索
        if min_score > 0:
            results = self.retriever.retrieve_with_scores(
                question,
                min_score=min_score
            )
        else:
            results = self.retriever.retrieve(question, n_results=top_k)

        # 格式化上下文
        context = None
        if format_context and results:
            context = self.retriever.format_context(results)

        return {
            'question': question,
            'results': results,
            'context': context
        }

    def ask(
        self,
        question: str,
        top_k: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        完整问答（检索 + 生成）

        Args:
            question: 问题
            top_k: 返回文档数量
            system_prompt: 系统提示词

        Returns:
            答案和相关信息
        """
        if self.generator is None:
            raise ValueError(
                "Generator not initialized. "
                "Please call init_generator(api_key) first."
            )

        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")

        # 1. 检索
        print("Step 1: Retrieving relevant documents...")
        query_result = self.query(question, top_k=top_k)

        if not query_result['results']:
            return {
                'question': question,
                'answer': '抱歉，我没有找到相关的文档来回答这个问题。',
                'sources': []
            }

        print(f"Found {len(query_result['results'])} relevant documents")

        # 2. 生成
        print("Step 2: Generating answer...")
        answer = self.generator.generate(
            question=question,
            context=query_result['context'],
            system_prompt=system_prompt
        )

        # 3. 返回结果
        sources = [
            {
                'text': r['text'][:100] + '...',
                'metadata': r['metadata'],
                'score': r.get('score', None)
            }
            for r in query_result['results']
        ]

        print("Step 3: Answer generated")

        return {
            'question': question,
            'answer': answer,
            'sources': sources
        }

    def ask_stream(
        self,
        question: str,
        top_k: Optional[int] = None,
        system_prompt: Optional[str] = None
    ):
        """
        流式问答（逐字输出）

        Args:
            question: 问题
            top_k: 返回文档数量
            system_prompt: 系统提示词

        Yields:
            生成的文本片段
        """
        if self.generator is None:
            raise ValueError(
                "Generator not initialized. "
                "Please call init_generator(api_key) first."
            )

        # 1. 检索
        query_result = self.query(question, top_k=top_k)

        if not query_result['results']:
            yield '抱歉，我没有找到相关的文档来回答这个问题。'
            return

        # 2. 生成（流式）
        for chunk in self.generator.generate_stream(
            question=question,
            context=query_result['context'],
            system_prompt=system_prompt
        ):
            yield chunk


# 便捷函数
def get_rag_pipeline(
    embedding_model_name: str = "all-MiniLM-L6-v2",
    vector_store_path: str = "./data/chroma",
    collection_name: str = "buffett_munger_docs",
    generator_model: str = "glm-4-flash",
    top_k: int = 5
) -> RAGPipeline:
    """获取RAG流程实例"""
    return RAGPipeline(
        embedding_model_name=embedding_model_name,
        vector_store_path=vector_store_path,
        collection_name=collection_name,
        generator_model=generator_model,
        top_k=top_k
    )


# 测试代码
if __name__ == "__main__":
    import os

    print("=" * 60)
    print("RAG Pipeline Test")
    print("=" * 60)

    # 创建RAG流程
    pipeline = get_rag_pipeline()

    # 测试查询（不需要API密钥）
    print("\n\nTest 1: Query (retrieval only)")
    print("-" * 60)

    result = pipeline.query("什么是价值投资？", top_k=3)

    print(f"\nFound {len(result['results'])} results:\n")

    for i, res in enumerate(result['results'], 1):
        print(f"{i}. {res['text'][:100]}...")
        print(f"   Source: {res['metadata']}")
        print()

    # 测试完整问答（需要API密钥）
    api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        print("\n\nTest 2: Ask (retrieval + generation)")
        print("-" * 60)

        # 自动检测使用哪个API
        if os.getenv("GLM_API_KEY"):
            print("Using GLM API")
            pipeline.init_generator()  # 使用默认的glm-4-flash模型
        else:
            print("Using OpenAI API")
            pipeline.init_generator()  # 使用OpenAI密钥

        result = pipeline.ask("什么是价值投资？", top_k=3)

        print(f"\n\nAnswer:\n{result['answer']}")

        print(f"\n\nSources used:")
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['metadata']}")
    else:
        print("\n\n[INFO] Skipping generation test (no API key found)")
        print("Set GLM_API_KEY or OPENAI_API_KEY to test generation")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
