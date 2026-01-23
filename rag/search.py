#!/usr/bin/env python3
"""
联网搜索模块
让AI能够获取2020年后的最新信息
"""

import os
import requests
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS


class WebSearcher:
    """网络搜索器"""

    def __init__(self, max_results: int = 5):
        """
        初始化网络搜索器

        Args:
            max_results: 最大结果数量
        """
        self.max_results = max_results
        print("WebSearcher initialized (DuckDuckGo)")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索网络

        Args:
            query: 搜索查询

        Returns:
            搜索结果列表
        """
        try:
            # 使用DuckDuckGo搜索（免费，无需API密钥）
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            results = ddgs.text(
                query,
                max_results=self.max_results
            )

            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'snippet': result.get('body', ''),
                    'source': 'DuckDuckGo'
                })

            return formatted_results

        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []

    def get_page_content(self, url: str) -> Optional[str]:
        """
        获取网页内容

        Args:
            url: 网页URL

        Returns:
            网页文本内容
        """
        try:
            # 发送HTTP请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 简单提取文本（实际项目中应该用BeautifulSoup）
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()

            # 清理空行
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # 限制长度
            if len(text) > 5000:
                text = text[:5000] + "..."

            return text

        except Exception as e:
            print(f"获取网页内容出错: {str(e)}")
            return None


class EnhancedRAGWithSearch:
    """增强的RAG系统（带联网搜索）"""

    def __init__(
        self,
        pipeline,
        searcher: Optional[WebSearcher] = None,
        enable_search: bool = True
    ):
        """
        初始化增强RAG系统

        Args:
            pipeline: RAG流程实例
            searcher: 网络搜索器
            enable_search: 是否启用联网搜索
        """
        self.pipeline = pipeline
        self.searcher = searcher or WebSearcher()
        self.enable_search = enable_search

        print("EnhancedRAGWithSearch initialized")

    def ask_with_search(
        self,
        question: str,
        top_k: Optional[int] = None,
        search_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        带联网搜索的问答

        Args:
            question: 用户问题
            top_k: 检索文档数量
            search_keywords: 搜索关键词（如果不提供，自动从问题提取）

        Returns:
            答案和相关信息
        """
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")

        # 1. 检测是否需要联网搜索
        needs_search = self._detect_search_need(question, search_keywords)

        web_context = ""
        search_results = []

        if needs_search and self.enable_search:
            print("Step 1: Searching the web...")

            # 确定搜索关键词
            if search_keywords:
                search_query = " ".join(search_keywords)
            else:
                search_query = self._extract_search_query(question)

            print(f"Search query: {search_query}")

            # 执行搜索
            search_results = self.searcher.search(search_query)

            if search_results:
                print(f"Found {len(search_results)} web results")

                # 获取前2个结果的详细内容
                for i, result in enumerate(search_results[:2], 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     {result['url']}")

                    # 获取页面内容
                    content = self.searcher.get_page_content(result['url'])
                    if content:
                        web_context += f"\n【网络搜索结果 {i}】\n"
                        web_context += f"标题：{result['title']}\n"
                        web_context += f"链接：{result['url']}\n"
                        web_context += f"内容：{content[:1000]}\n"

            else:
                print("No web results found")

        # 2. 从RAG系统检索
        print("\nStep 2: Retrieving from knowledge base...")
        query_result = self.pipeline.query(question, top_k=top_k)

        if not query_result['results']:
            # 只有网络搜索结果
            if web_context:
                answer = self._generate_answer_with_web_only(
                    question,
                    web_context
                )
                return {
                    'question': question,
                    'answer': answer,
                    'sources': [],
                    'web_results': search_results
                }
            else:
                return {
                    'question': question,
                    'answer': '抱歉，我没有找到相关信息。',
                    'sources': [],
                    'web_results': []
                }

        print(f"Found {len(query_result['results'])} documents from knowledge base")

        # 3. 结合网络搜索和RAG结果生成答案
        print("\nStep 3: Generating answer with all context...")

        # 合并上下文
        combined_context = query_result['context']

        if web_context:
            combined_context = f"""## 来自知识库的资料

{query_result['context']}

## 来自网络搜索的最新信息

{web_context}

请结合以上两类信息回答问题。对于网络搜索的新信息，要用巴菲特或芒格的思维方式来分析和评价。
"""

        answer = self.pipeline.generator.generate(
            question=question,
            context=combined_context,
            system_prompt=self._get_enhanced_prompt()
        )

        print("Step 4: Answer generated")

        return {
            'question': question,
            'answer': answer,
            'sources': query_result['results'],
            'web_results': search_results,
            'used_web_search': bool(search_results)
        }

    def _detect_search_need(
        self,
        question: str,
        search_keywords: Optional[List[str]]
    ) -> bool:
        """
        检测是否需要联网搜索

        Args:
            question: 用户问题
            search_keywords: 搜索关键词

        Returns:
            是否需要搜索
        """
        # 如果提供了搜索关键词，说明需要搜索
        if search_keywords:
            return True

        # 检测问题中的特定关键词
        search_triggers = [
            "2020", "2021", "2022", "2023", "2024", "2025",  # 年份
            "最新", "现在", "当前", "最近",  # 时间词
            "polymarket", "chatgpt", "openai",  # 已知的新事物
        ]

        question_lower = question.lower()
        return any(trigger in question_lower for trigger in search_triggers)

    def _extract_search_query(self, question: str) -> str:
        """
        从问题中提取搜索查询

        Args:
            question: 用户问题

        Returns:
            搜索查询
        """
        # 简单策略：直接使用问题作为搜索查询
        # 实际中可以更智能，比如提取关键实体
        return question

    def _get_enhanced_prompt(self) -> str:
        """
        获取增强的系统提示词

        Returns:
            系统提示词
        """
        from rag.prompts import BUFFETT_MUNGER_PROMPT

        return f"""{BUFFETT_MUNGER_PROMPT}

## 重要补充：处理新信息

当用户提供2020年后的事物或最新信息时：

1. **理解新事物** - 首先理解它是什么、如何运作
2. **用我们的原则分析** - 用价值投资的原则来评价
3. **指出风险和机会** - 基于我们的经验
4. **保持一致性** - 不违背我们的核心原则

例如，如果问到加密货币或预测市场：
- 理解其运作机制
- 用"护城河"、"安全边际"等框架分析
- 指出是否符合价值投资理念
- 给出基于我们经验的建议

记住：虽然世界在变化，但投资的基本原则不变。
"""

    def _generate_answer_with_web_only(
        self,
        question: str,
        web_context: str
    ) -> str:
        """
        仅基于网络搜索生成答案

        Args:
            question: 问题
            web_context: 网络搜索上下文

        Returns:
            答案
        """
        prompt = f"""基于以下网络搜索信息回答问题：

{web_context}

问题：{question}

请用巴菲特或芒格的思维方式来分析这些信息。"""
        return self.pipeline.generator.generate(
            question=question,
            context=web_context,
            system_prompt=self._get_enhanced_prompt()
        )


# 便捷函数
def get_web_searcher(max_results: int = 5) -> WebSearcher:
    """获取网络搜索器实例"""
    return WebSearcher(max_results=max_results)


def get_enhanced_rag(
    pipeline,
    searcher: Optional[WebSearcher] = None,
    enable_search: bool = True
) -> EnhancedRAGWithSearch:
    """获取增强RAG系统实例"""
    return EnhancedRAGWithSearch(
        pipeline=pipeline,
        searcher=searcher,
        enable_search=enable_search
    )


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("Web Search Module Test")
    print("=" * 60)

    # 测试搜索功能
    searcher = get_web_searcher(max_results=3)

    test_query = "Polymarket prediction market"
    print(f"\n测试搜索: {test_query}\n")

    results = searcher.search(test_query)

    print(f"找到 {len(results)} 个结果:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   摘要: {result['snippet'][:100]}...")
        print()

    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
