#!/usr/bin/env python3
"""
FastAPI后端主文件
Nothing to Add - 巴菲特与芒格AI Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pipeline import get_rag_pipeline
from rag.conversation import get_conversation_manager
from rag.search import get_web_searcher, get_enhanced_rag
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="Nothing to Add API",
    description="巴菲特与芒格AI Agent - 让AI能够理解2020年后的事物",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
pipeline = None
conversation_manager = None
enhanced_rag = None


# 数据模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    session_id: Optional[str] = None
    use_search: bool = False


class ChatResponse(BaseModel):
    """聊天响应模型"""
    session_id: str
    answer: str
    sources: List[dict]
    used_search: bool = False


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    message: str


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    global pipeline, conversation_manager, enhanced_rag

    print("=" * 60)
    print("Initializing Nothing to Add API")
    print("=" * 60)

    try:
        # 初始化RAG流程
        print("\n[1/3] Initializing RAG pipeline...")
        pipeline = get_rag_pipeline()

        # 检查API密钥
        api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[WARNING] No API key found. Chat features will not work.")
        else:
            pipeline.init_generator()
            print("[OK] RAG pipeline initialized")

        # 初始化对话管理器
        print("\n[2/3] Initializing conversation manager...")
        conversation_manager = get_conversation_manager(pipeline)
        print("[OK] Conversation manager initialized")

        # 初始化增强RAG（带搜索）
        print("\n[3/3] Initializing web search...")
        searcher = get_web_searcher()
        enhanced_rag = get_enhanced_rag(pipeline, searcher, enable_search=True)
        print("[OK] Web search initialized")

        print("\n" + "=" * 60)
        print("API ready to serve requests!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Failed to initialize: {str(e)}")
        import traceback
        traceback.print_exc()


# 健康检查
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(
        status="healthy",
        message="Nothing to Add API is running"
    )


# 聊天接口
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口

    Args:
        request: 聊天请求

    Returns:
        聊天响应
    """
    try:
        if not pipeline or not pipeline.generator:
            raise HTTPException(
                status_code=503,
                detail="API not properly initialized. Please check API key."
            )

        # 获取或创建会话
        if request.session_id:
            conversation = conversation_manager.get_conversation(request.session_id)
            if not conversation:
                conversation = conversation_manager.create_conversation(
                    session_id=request.session_id
                )
        else:
            conversation = conversation_manager.create_conversation()

        # 生成回答
        result = conversation.ask(request.message, top_k=3)

        return ChatResponse(
            session_id=result['session_id'],
            answer=result['answer'],
            sources=[
                {
                    'text': s['text'][:100] + '...',
                    'metadata': s['metadata']
                }
                for s in result['sources']
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 带搜索的聊天接口
@app.post("/api/chat/search", response_model=ChatResponse)
async def chat_with_search(request: ChatRequest):
    """
    带联网搜索的聊天接口

    Args:
        request: 聊天请求

    Returns:
        聊天响应（包含搜索结果）
    """
    try:
        if not enhanced_rag:
            raise HTTPException(
                status_code=503,
                detail="Enhanced RAG not initialized"
            )

        # 获取或创建会话
        if request.session_id:
            conversation = conversation_manager.get_conversation(request.session_id)
            if not conversation:
                conversation = conversation_manager.create_conversation(
                    session_id=request.session_id
                )
        else:
            conversation = conversation_manager.create_conversation()

        # 使用增强RAG（带搜索）
        result = enhanced_rag.ask_with_search(
            request.message,
            top_k=3,
            search_keywords=None  # 自动检测
        )

        return ChatResponse(
            session_id=result['session_id'],
            answer=result['answer'],
            sources=[
                {
                    'text': s['text'][:100] + '...',
                    'metadata': s['metadata']
                }
                for s in result['sources']
            ],
            used_search=result.get('used_web_search', False)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 清空会话历史
@app.delete("/api/chat/{session_id}")
async def clear_conversation(session_id: str):
    """
    清空会话历史

    Args:
        session_id: 会话ID

    Returns:
        成功消息
    """
    try:
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Session not found")

        conversation.clear_history()

        return {"message": "Conversation history cleared"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 列出所有会话
@app.get("/api/sessions")
async def list_sessions():
    """
    列出所有活跃会话

    Returns:
        会话列表
    """
    try:
        sessions = conversation_manager.list_conversations()
        return {"sessions": sessions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # 运行服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式，代码改动自动重载
    )
