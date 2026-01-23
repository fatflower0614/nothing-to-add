#!/usr/bin/env python3
"""
会话管理模块
支持多轮对话和上下文记忆
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from rag.pipeline import RAGPipeline


class Conversation:
    """对话会话类"""

    def __init__(
        self,
        pipeline: RAGPipeline,
        session_id: Optional[str] = None,
        max_history: int = 10
    ):
        """
        初始化对话会话

        Args:
            pipeline: RAG流程实例
            session_id: 会话ID（如果不提供，自动生成）
            max_history: 最大历史记录数量
        """
        self.pipeline = pipeline
        self.session_id = session_id or self._generate_session_id()
        self.max_history = max_history

        # 对话历史
        self.messages: List[Dict[str, str]] = []

        # 会话元数据
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

        print(f"Conversation created: {self.session_id}")

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"

    def add_message(self, role: str, content: str):
        """
        添加消息到历史记录

        Args:
            role: 角色（user/assistant）
            content: 消息内容
        """
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # 限制历史记录数量
        if len(self.messages) > self.max_history * 2:  # 乘以2因为包括问题和答案
            # 保留最近的消息
            self.messages = self.messages[-self.max_history * 2:]

        # 更新最后活动时间
        self.last_activity = datetime.now()

    def get_conversation_context(self) -> str:
        """
        获取对话上下文（用于生成答案）

        Returns:
            格式化的对话历史
        """
        if not self.messages:
            return ""

        context_parts = []
        for msg in self.messages[-6:]:  # 只使用最近3轮对话（6条消息）
            role_name = "用户" if msg["role"] == "user" else "我"
            context_parts.append(f"{role_name}: {msg['content']}")

        return "\n".join(context_parts)

    def ask(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        提问（带记忆）

        Args:
            question: 问题
            top_k: 检索文档数量

        Returns:
            答案和相关信息
        """
        print(f"\n{'='*60}")
        print(f"[Session: {self.session_id}] Question: {question}")
        print(f"{'='*60}\n")

        # 1. 添加用户问题到历史
        self.add_message("user", question)

        # 2. 检索相关文档
        print("Step 1: Retrieving relevant documents...")
        query_result = self.pipeline.query(question, top_k=top_k)

        if not query_result['results']:
            answer = '抱歉，我没有找到相关的文档来回答这个问题。'

            # 添加助手回答到历史
            self.add_message("assistant", answer)

            return {
                'session_id': self.session_id,
                'question': question,
                'answer': answer,
                'sources': [],
                'history_length': len(self.messages)
            }

        print(f"Found {len(query_result['results'])} relevant documents")

        # 3. 构建提示词（包含对话历史）
        print("Step 2: Building context with conversation history...")

        # 获取对话历史上下文
        conversation_context = self.get_conversation_context()

        # 构建系统提示词
        system_prompt = self._build_system_prompt(conversation_context)

        # 4. 生成答案
        print("Step 3: Generating answer...")
        answer = self.pipeline.generator.generate(
            question=question,
            context=query_result['context'],
            system_prompt=system_prompt
        )

        # 5. 添加助手回答到历史
        self.add_message("assistant", answer)

        # 6. 格式化来源
        sources = [
            {
                'text': r['text'][:100] + '...',
                'metadata': r['metadata'],
                'score': r.get('score', None)
            }
            for r in query_result['results']
        ]

        print("Step 4: Answer generated")

        return {
            'session_id': self.session_id,
            'question': question,
            'answer': answer,
            'sources': sources,
            'history_length': len(self.messages)
        }

    def _build_system_prompt(self, conversation_context: str) -> str:
        """
        构建系统提示词（包含对话历史）

        Args:
            conversation_context: 对话上下文

        Returns:
            系统提示词
        """
        from rag.prompts import BUFFETT_MUNGER_PROMPT

        if not conversation_context:
            return BUFFETT_MUNGER_PROMPT

        # 在原有提示词基础上添加对话历史
        enhanced_prompt = f"""{BUFFETT_MUNGER_PROMPT}

## 对话历史
这是我们刚才的对话内容：

{conversation_context}

请结合之前的对话内容，自然地回答当前的问题。如果用户在追问之前的话题，请直接继续；如果是新话题，也可以自然地转换。保持巴菲特和芒格的对话风格。

记住：
- 自然地引用之前的对话内容
- 保持一致的说话风格
- 像真的在连续聊天一样
"""
        return enhanced_prompt

    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史

        Returns:
            消息列表
        """
        return self.messages.copy()

    def clear_history(self):
        """清空对话历史"""
        self.messages = []
        print(f"Conversation history cleared for session: {self.session_id}")

    def summarize(self) -> Dict[str, Any]:
        """
        获取会话摘要

        Returns:
            会话信息
        """
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'message_count': len(self.messages),
            'messages': self.get_history()
        }


class ConversationManager:
    """对话管理器（管理多个会话）"""

    def __init__(self, pipeline: RAGPipeline):
        """
        初始化对话管理器

        Args:
            pipeline: RAG流程实例
        """
        self.pipeline = pipeline
        self.conversations: Dict[str, Conversation] = {}

    def create_conversation(
        self,
        session_id: Optional[str] = None,
        max_history: int = 10
    ) -> Conversation:
        """
        创建新会话

        Args:
            session_id: 会话ID（如果不提供，自动生成）
            max_history: 最大历史记录数量

        Returns:
            会话对象
        """
        conversation = Conversation(
            pipeline=self.pipeline,
            session_id=session_id,
            max_history=max_history
        )

        self.conversations[conversation.session_id] = conversation

        return conversation

    def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话对象（如果存在）
        """
        return self.conversations.get(session_id)

    def delete_conversation(self, session_id: str):
        """
        删除会话

        Args:
            session_id: 会话ID
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            print(f"Conversation deleted: {session_id}")

    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        列出所有会话

        Returns:
            会话列表
        """
        return [conv.summarize() for conv in self.conversations.values()]

    def get_active_conversation(self) -> Optional[Conversation]:
        """
        获取最近活跃的会话

        Returns:
            最近活跃的会话
        """
        if not self.conversations:
            return None

        # 按最后活动时间排序
        sorted_conversations = sorted(
            self.conversations.values(),
            key=lambda c: c.last_activity,
            reverse=True
        )

        return sorted_conversations[0]


# 便捷函数
def get_conversation_manager(pipeline: RAGPipeline) -> ConversationManager:
    """获取对话管理器实例"""
    return ConversationManager(pipeline)


# 测试代码
if __name__ == "__main__":
    import os
    from rag.pipeline import get_rag_pipeline

    print("=" * 60)
    print("Conversation Module Test")
    print("=" * 60)

    # 检查API密钥
    api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[WARNING] No API key found")
        print("Set GLM_API_KEY or OPENAI_API_KEY to test")
        exit(0)

    # 创建RAG流程
    print("\nInitializing RAG pipeline...")
    pipeline = get_rag_pipeline()
    pipeline.init_generator()

    # 创建对话管理器
    manager = get_conversation_manager(pipeline)

    # 创建会话
    print("\n" + "="*60)
    print("Creating new conversation...")
    print("="*60)

    conversation = manager.create_conversation()

    # 模拟多轮对话
    questions = [
        "什么是价值投资？",
        "那如何找到这样的企业呢？",
        "能举个具体的例子吗？"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n\n{'='*60}")
        print(f"Round {i}")
        print(f"{'='*60}")

        result = conversation.ask(question)

        print(f"\nQuestion: {result['question']}")
        print(f"\nAnswer: {result['answer']}")
        print(f"\nHistory length: {result['history_length']} messages")

    # 显示对话历史
    print(f"\n\n{'='*60}")
    print("Conversation History")
    print(f"{'='*60}\n")

    history = conversation.get_history()
    for i, msg in enumerate(history, 1):
        role_name = "User" if msg['role'] == 'user' else 'Assistant'
        print(f"{i}. [{role_name}] {msg['content'][:100]}...")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
