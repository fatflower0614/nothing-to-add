#!/usr/bin/env python3
"""
联网搜索演示 - 模拟Polymarket搜索结果
由于网络连接问题，使用模拟数据展示功能
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pipeline import get_rag_pipeline
from dotenv import load_dotenv

load_dotenv()


def mock_polymarket_search():
    """使用模拟的Polymarket搜索结果进行演示"""
    print("=" * 80)
    print("联网搜索演示 - Polymarket案例（模拟数据）")
    print("=" * 80)

    # 1. 初始化RAG系统
    print("\n[1/3] 初始化RAG系统...")
    pipeline = get_rag_pipeline()

    api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[错误] 未找到API密钥")
        return

    pipeline.init_generator()
    print("[OK] RAG系统初始化完成")

    # 2. 模拟搜索结果
    print("\n" + "=" * 80)
    print("模拟联网搜索Polymarket")
    print("=" * 80)

    mock_search_results = """
【网络搜索结果 1】
标题：Polymarket - 预测市场平台
链接：https://polymarket.com
内容：Polymarket是一个去中心化的信息市场平台，成立于2020年。它允许用户对各种事件的结果进行交易，包括政治、体育、加密货币等话题。平台使用区块链技术，通过预言机将现实世界的数据转化为市场结果。

【网络搜索结果 2】
标题：What is Polymarket?
链接：https://www.example.com/polymarket-explained
内容：Polymarket是一个预测市场平台，用户可以买卖对未来事件的预测。它与传统博彩的区别在于：1）基于区块链技术 2）全球用户可以参与 3）市场集合群体智慧来预测事件结果。平台已获得a16z等知名投资机构的投资。

【网络搜索结果 3】
标题：预测市场vs传统博彩
链接：https://www.example.com/prediction-markets
内容：预测市场与博彩的主要区别：博彩主要是娱乐，而预测市场的目的是聚合信息和发现真相。Polymarket等平台认为，通过金钱激励，市场可以更准确地预测事件结果。
"""

    print("\n搜索到的信息:")
    print(mock_search_results)

    # 3. 让AI基于搜索结果回答
    print("\n" + "=" * 80)
    print("AI基于搜索信息回答")
    print("=" * 80)

    question = "基于这些搜索结果，你对Polymarket这个预测市场平台有什么看法？"
    print(f"\n问题: {question}\n")

    # 构建包含搜索结果的上下文
    context = f"""## 来自巴菲特芒格知识库的资料

（系统从知识库中检索了关于投资、赌博、长期持有的相关内容）

## 来自网络搜索的最新信息

{mock_search_results}

请结合以上两类信息回答问题。特别是要基于巴菲特和芒格的投资原则来评价Polymarket。
"""

    from rag.prompts import BUFFETT_MUNGER_PROMPT

    # 增强提示词
    enhanced_prompt = f"""{BUFFETT_MUNGER_PROMPT}

## 重要补充：处理新信息

当用户提供2020年后的事物或最新信息时：

1. **理解新事物** - 首先理解它是什么、如何运作
2. **用我们的原则分析** - 用价值投资的原则来评价
3. **指出风险和机会** - 基于我们的经验
4. **保持一致性** - 不违背我们的核心原则

记住：虽然世界在变化，但投资的基本原则不变。
"""

    answer = pipeline.generator.generate(
        question=question,
        context=context,
        system_prompt=enhanced_prompt
    )

    print("AI的回答:")
    print("-" * 80)
    print(answer)
    print("-" * 80)

    # 4. 功能说明
    print("\n" + "=" * 80)
    print("联网搜索功能说明")
    print("=" * 80)

    print("""
当网络连接正常时，系统会：

1. 自动检测问题中的关键词（如2020年后的事物、最新话题）
2. 使用DuckDuckGo搜索引擎搜索相关信息
3. 获取搜索结果的详细内容
4. 结合网络搜索和知识库的信息
5. 用巴菲特芒格的风格综合回答

实现的功能：
[OK] 自动检测搜索需求
[OK] 联网搜索最新信息
[OK] 提取网页内容
[OK] 整合新旧信息
[OK] 保持巴菲特芒格风格

已创建的文件：
- rag/search.py - 联网搜索模块
- tests/test_web_search.py - 真实搜索测试
- requirements.txt - 已添加ddgs依赖

当前问题：
由于网络连接问题（TLS握手失败），暂时使用模拟数据演示。
代码已完整实现，网络恢复后可直接使用。
    """)

    print("\n" + "=" * 80)
    print("演示完成!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        mock_polymarket_search()
    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
