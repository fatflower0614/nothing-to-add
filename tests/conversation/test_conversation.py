#!/usr/bin/env python3
"""
测试多轮对话功能
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


def test_multi_turn_conversation():
    """测试多轮对话"""
    print("=" * 80)
    print("多轮对话测试")
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

    # 创建新会话
    conversation = manager.create_conversation(max_history=10)
    print(f"[OK] 会话创建成功: {conversation.session_id}")

    # 3. 第一轮对话
    print("\n" + "=" * 80)
    print("第一轮对话")
    print("=" * 80)

    question1 = "什么是价值投资？"
    print(f"\n问题: {question1}")

    result1 = conversation.ask(question1, top_k=3)

    print(f"\n回答:")
    print("-" * 80)
    print(result1['answer'])
    print("-" * 80)

    print(f"\n使用来源: {len(result1['sources'])}个文档")
    print(f"历史消息数: {result1['history_length']}")

    # 4. 第二轮对话（追问）
    print("\n" + "=" * 80)
    print("第二轮对话（追问）")
    print("=" * 80)

    question2 = "那如何判断一个企业是否有护城河呢？"
    print(f"\n问题: {question2}")

    result2 = conversation.ask(question2, top_k=3)

    print(f"\n回答:")
    print("-" * 80)
    print(result2['answer'])
    print("-" * 80)

    print(f"\n使用来源: {len(result2['sources'])}个文档")
    print(f"历史消息数: {result2['history_length']}")

    # 5. 第三轮对话（继续追问）
    print("\n" + "=" * 80)
    print("第三轮对话（继续追问）")
    print("=" * 80)

    question3 = "能给我举个具体的例子吗？"
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
        content_preview = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
        print(f"{i}. {role_name}")
        print(f"   {content_preview}\n")

    # 7. 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    summary = conversation.summarize()
    print(f"\n会话ID: {summary['session_id']}")
    print(f"创建时间: {summary['created_at']}")
    print(f"最后活动: {summary['last_activity']}")
    print(f"消息总数: {summary['message_count']}")

    print("\n[OK] 多轮对话测试完成!")
    print("\n说明:")
    print("- AI能够记住之前的对话内容")
    print("- 回答时会结合上下文")
    print("- 保持巴菲特和芒格的说话风格")
    print("- 可以自然地进行多轮对话")


def test_conversation_manager():
    """测试对话管理器"""
    print("\n\n" + "=" * 80)
    print("对话管理器测试")
    print("=" * 80)

    # 初始化
    pipeline = get_rag_pipeline()
    api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[错误] 未找到API密钥")
        return

    pipeline.init_generator()

    # 创建管理器
    manager = get_conversation_manager(pipeline)

    # 创建多个会话
    print("\n创建3个不同的会话...")

    session1 = manager.create_conversation(session_id="session_001")
    session2 = manager.create_conversation(session_id="session_002")
    session3 = manager.create_conversation()

    print(f"[OK] 会话1: {session1.session_id}")
    print(f"[OK] 会话2: {session2.session_id}")
    print(f"[OK] 会话3: {session3.session_id}")

    # 列出所有会话
    print("\n所有会话:")
    conversations = manager.list_conversations()
    for conv in conversations:
        print(f"- {conv['session_id']}: {conv['message_count']} 条消息")

    # 获取活跃会话
    active = manager.get_active_conversation()
    print(f"\n最近活跃的会话: {active.session_id}")

    print("\n[OK] 对话管理器测试完成!")


if __name__ == "__main__":
    try:
        # 运行主要测试
        test_multi_turn_conversation()

        # 可选：测试管理器
        # test_conversation_manager()

    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
