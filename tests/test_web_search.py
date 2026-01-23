#!/usr/bin/env python3
"""
测试联网搜索功能 - Polymarket案例
验证AI能否搜索并理解2020年后的事物
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pipeline import get_rag_pipeline
from rag.search import get_web_searcher, get_enhanced_rag
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_web_search_polymarket():
    """测试Polymarket联网搜索"""
    print("=" * 80)
    print("联网搜索测试 - Polymarket案例")
    print("=" * 80)

    # 1. 初始化RAG系统
    print("\n[1/4] 初始化RAG系统...")
    pipeline = get_rag_pipeline()

    api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[错误] 未找到API密钥")
        print("请在.env文件中设置 GLM_API_KEY 或 OPENAI_API_KEY")
        return

    pipeline.init_generator()
    print("[OK] RAG系统初始化完成")

    # 2. 初始化联网搜索
    print("\n[2/4] 初始化联网搜索...")
    searcher = get_web_searcher(max_results=3)
    print("[OK] 搜索器初始化完成")

    # 3. 测试搜索功能
    print("\n" + "=" * 80)
    print("第一步：搜索Polymarket信息")
    print("=" * 80)

    search_query = "Polymarket prediction market platform"
    print(f"\n搜索查询: {search_query}\n")

    search_results = searcher.search(search_query)

    print(f"找到 {len(search_results)} 个结果:\n")
    for i, result in enumerate(search_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   摘要: {result['snippet'][:150]}...")
        print()

    if not search_results:
        print("[警告] 未找到搜索结果，可能网络有问题")
        return

    # 4. 获取详细内容
    print("\n" + "=" * 80)
    print("第二步：获取页面详细内容")
    print("=" * 80)

    # 获取第一个结果的内容
    if search_results:
        first_result = search_results[0]
        print(f"\n正在获取: {first_result['title']}\n")

        page_content = searcher.get_page_content(first_result['url'])

        if page_content:
            print(f"页面内容（前500字符）:\n")
            print(page_content[:500])
            print("...")
        else:
            print("[警告] 无法获取页面内容")

    # 5. 使用增强RAG回答
    print("\n" + "=" * 80)
    print("第三步：让AI基于搜索信息回答")
    print("=" * 80)

    enhanced_rag = get_enhanced_rag(pipeline, searcher, enable_search=True)

    question = "你对Polymarket这个预测市场平台有什么看法？"
    print(f"\n问题: {question}")

    result = enhanced_rag.ask_with_search(
        question,
        top_k=3,
        search_keywords=["Polymarket", "prediction market"]
    )

    print(f"\n回答:")
    print("-" * 80)
    print(result['answer'])
    print("-" * 80)

    print(f"\n是否使用了联网搜索: {'是' if result.get('used_web_search') else '否'}")
    print(f"检索到的文档数: {len(result['sources'])}")
    print(f"网络搜索结果数: {len(result.get('web_results', []))}")

    # 6. 测试结果分析
    print("\n" + "=" * 80)
    print("测试结果分析")
    print("=" * 80)

    print("\n联网搜索能力验证:")
    if result.get('used_web_search'):
        print("✓ 成功联网搜索")
        print(f"✓ 找到 {len(result.get('web_results', []))} 个相关结果")

        print("\n搜索结果:")
        for i, web_result in enumerate(result.get('web_results', [])[:3], 1):
            print(f"{i}. {web_result['title']}")
            print(f"   {web_result['url']}")
    else:
        print("✗ 未使用联网搜索")

    print("\nAI理解能力验证:")
    print("- AI能否理解Polymarket是什么")
    print("- AI能否用巴菲特芒格的风格评价")
    print("- AI能否结合新旧信息")

    print("\n" + "=" * 80)
    print("[OK] 测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_web_search_polymarket()
    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
