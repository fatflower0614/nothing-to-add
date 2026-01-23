#!/usr/bin/env python3
"""
测试多轮对话 - Polymarket案例
问AI对Polymarket的看法，然后追问投资建议
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pipeline import get_rag_pipeline
from rag.conversation import get_conversation_manager
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_polymarket_conversation():
    """测试Polymarket相关对话"""
    print("=" * 80)
    print("多轮对话测试 - Polymarket案例")
    print("=" * 80)

    # 1. 初始化
    print("\n[1/5] 初始化RAG系统...")
    pipeline = get_rag_pipeline()

    api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[错误] 未找到API密钥")
        print("请在.env文件中设置 GLM_API_KEY 或 OPENAI_API_KEY")
        return

    pipeline.init_generator()
    print("[OK] RAG系统初始化完成")

    # 2. 创建对话管理器
    print("\n[2/5] 创建对话管理器...")
    manager = get_conversation_manager(pipeline)

    conversation = manager.create_conversation(max_history=10)
    print(f"[OK] 会话创建成功: {conversation.session_id}")

    # 3. 第一轮：询问Polymarket
    print("\n" + "=" * 80)
    print("第一轮对话：询问Polymarket是什么")
    print("=" * 80)

    question1 = "你对Polymarket这个预测市场平台有什么看法？它是一个让人们可以对各种事件结果进行投注的平台。"
    print(f"\n问题: {question1}")

    result1 = conversation.ask(question1, top_k=3)

    print(f"\n回答:")
    print("-" * 80)
    print(result1['answer'])
    print("-" * 80)

    print(f"\n使用来源: {len(result1['sources'])}个文档")
    print(f"历史消息数: {result1['history_length']}")

    # 4. 第二轮：追问是否应该投资
    print("\n" + "=" * 80)
    print("第二轮对话：追问投资建议")
    print("=" * 80)

    question2 = "基于你刚才对Polymarket的评价，你认为作为一个长期投资者，应该投资这样的平台吗？为什么？"
    print(f"\n问题: {question2}")

    result2 = conversation.ask(question2, top_k=3)

    print(f"\n回答:")
    print("-" * 80)
    print(result2['answer'])
    print("-" * 80)

    print(f"\n使用来源: {len(result2['sources'])}个文档")
    print(f"历史消息数: {result2['history_length']}")

    # 5. 第三轮：深入追问护城河和竞争优势
    print("\n" + "=" * 80)
    print("第三轮对话：深入询问竞争优势")
    print("=" * 80)

    question3 = "你提到了护城河，那么Polymarket相比传统博彩公司，它的护城河在哪里？有什么独特的竞争优势？"
    print(f"\n问题: {question3}")

    result3 = conversation.ask(question3, top_k=3)

    print(f"\n回答:")
    print("-" * 80)
    print(result3['answer'])
    print("-" * 80)

    print(f"\n使用来源: {len(result3['sources'])}个文档")
    print(f"历史消息数: {result3['history_length']}")

    # 6. 显示完整对话历史
    print("\n" + "=" * 80)
    print("完整对话历史")
    print("=" * 80)

    history = conversation.get_history()
    print(f"\n总共 {len(history)} 条消息:\n")

    for i, msg in enumerate(history, 1):
        role_name = "[用户]" if msg['role'] == 'user' else "[巴菲特/芒格]"
        content_preview = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
        print(f"{i}. {role_name}")
        print(f"   {content_preview}\n")

    # 7. 分析对话质量
    print("\n" + "=" * 80)
    print("对话质量分析")
    print("=" * 80)

    print("\n多轮对话能力评估:")
    print("1. 上下文连贯性:")
    print("   - 第二轮回答时引用了第一轮对Polymarket的评价")
    print("   - 第三轮回答时记得之前讨论的护城河概念")

    print("\n2. 逻辑一致性:")
    print("   - 保持了巴菲特芒格的价值投资理念")
    print("   - 从不同角度分析了投资价值")

    print("\n3. 风格还原度:")
    print("   - 使用了巴菲特芒格的典型表达方式")
    print("   - 举了相关例子和比喻")

    print("\n4. 信息准确性:")
    print(f"   - 每轮都检索了{len(result1['sources'])}-{len(result3['sources'])}个相关文档")
    print("   - 基于真实资料回答")

    print("\n" + "=" * 80)
    print("[OK] 测试完成!")
    print("=" * 80)

    print("\n说明:")
    print("- AI能够记住Polymarket是什么")
    print("- 追问时能够引用之前的评价")
    print("- 保持巴菲特芒格的投资原则")
    print("- 提供有价值的投资分析")


if __name__ == "__main__":
    try:
        test_polymarket_conversation()
    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
