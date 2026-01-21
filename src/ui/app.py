"""
Gradio界面 - Nothing to Add
基础版本，稍后会添加动画和语音功能
"""

import gradio as gr
from src.rag.rag_system import NothingToAddRAG
from src.prompts.prompts import get_prompt


class NothingToAddUI:
    """Nothing to Add的Gradio界面"""

    def __init__(self):
        """初始化UI"""
        self.rag = None
        self.chat_history = []

    def initialize_rag(self):
        """初始化RAG系统（延迟加载）"""
        if self.rag is None:
            print("🚀 初始化RAG系统...")
            self.rag = NothingToAddRAG()
            print("✅ RAG系统就绪！")

    def chat(
        self,
        message: str,
        history: list,
        mode: str,
        avatar_state: dict
    ):
        """
        聊天处理函数

        Args:
            message: 用户消息
            history: 对话历史
            mode: 对话模式
            avatar_state: 头像状态（用于动画触发）

        Returns:
            (bot_message, history, avatar_update)
        """
        # 初始化RAG
        self.initialize_rag()

        # 查询RAG系统
        result = self.rag.query(message, mode=mode)

        # 获取回答
        bot_message = result["answer"]

        # 检查是否需要触发动画
        avatar_update = self._check_animation_triggers(
            message, bot_message, mode, avatar_state
        )

        # 更新历史
        history.append([message, bot_message])

        return "", history, avatar_update

    def _check_animation_triggers(
        self,
        user_message: str,
        bot_message: str,
        mode: str,
        current_state: dict
    ) -> dict:
        """
        检查是否需要触发特定动画

        触发条件：
        - 巴菲特提到"可口可乐" → 喝可乐
        - 巴菲特提到"冰淇淋/喜诗" → 吃冰淇淋
        - 讲笑话 → 笑脸
        - 芒格说"我没什么可补充的" → 点头
        """
        message_lower = (user_message + bot_message).lower()

        # 巴菲特的触发条件
        if mode == "buffett" or mode == "dual":
            if "coca-cola" in message_lower or "可口可乐" in message_lower:
                return {"action": "drink_coke", "duration": 3}
            elif "ice cream" in message_lower or "冰淇淋" in message_lower or "see's" in message_lower:
                return {"action": "eat_icecream", "duration": 3}
            elif "哈哈" in bot_message or "有趣" in bot_message:
                return {"action": "smile", "duration": 2}

        # 芒格的触发条件
        if mode == "munger" or mode == "dual":
            if "没什么可补充" in bot_message or "nothing to add" in bot_message.lower():
                return {"action": "nod", "duration": 2}
            elif "愚蠢" in bot_message:
                return {"action": "serious", "duration": 2}

        return {"action": "talking", "duration": 1}

    def create_interface(self):
        """创建Gradio界面"""

        # 自定义CSS（稍后添加动画样式）
        custom_css = """
        .avatar-container {
            position: relative;
            width: 300px;
            height: 300px;
            margin: 0 auto;
        }

        .avatar-image {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
        }

        /* 动画效果（占位，稍后实现） */
        @keyframes talking {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        .talking {
            animation: talking 0.5s ease-in-out infinite;
        }
        """

        with gr.Blocks(
            theme=gr.themes.Soft(
                primary_hue="orange",
                secondary_hue="blue",
            ),
            css=custom_css
        ) as app:

            # 标题
            gr.Markdown(
                """
                # 🎯 Nothing to Add
                ## *Nothing to Add, Except Wisdom*

                与沃伦·巴菲特和查理·芒格对话
                """
            )

            # 模式选择
            with gr.Row():
                mode = gr.Radio(
                    choices=["巴菲特", "芒格", "双人对话"],
                    value="巴菲特",
                    label="选择对话模式",
                    interactive=True
                )

            # 头像显示区域（稍后添加动画）
            with gr.Row():
                avatar_display = gr.HTML(
                    value='<div class="avatar-container">👤</div>',
                    label="角色"
                )

            # 对话历史（占位，稍后用Chatbot组件替换）
            with gr.Row():
                chatbot = gr.Chatbot(
                    height=500,
                    label="对话",
                    bubble_full_width=False,
                    avatar_images=(None, "🤖")  # (user_avatar, bot_avatar)
                )

            # 输入区域
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="输入你的问题...",
                    scale=4,
                    label=""
                )
                submit = gr.Button("发送", scale=1, variant="primary")

            # 动画状态（隐藏）
            avatar_state = gr.State({"action": "idle", "duration": 0})

            # 绑定事件
            def submit_message(message, history, mode, avatar_state):
                return self.chat(message, history, mode, avatar_state)

            msg.submit(
                submit_message,
                inputs=[msg, chatbot, mode, avatar_state],
                outputs=[msg, chatbot, avatar_state]
            )

            submit.click(
                submit_message,
                inputs=[msg, chatbot, mode, avatar_state],
                outputs=[msg, chatbot, avatar_state]
            )

        return app


# ============= 启动应用 =============

def launch_app(share: bool = False):
    """
    启动Gradio应用

    Args:
        share: 是否创建公开链接
    """
    ui = NothingToAddUI()
    app = ui.create_interface()

    print("🚀 启动Nothing to Add...")
    print("📝 访问地址: http://localhost:7860")

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=share,
        show_error=True
    )


if __name__ == "__main__":
    import sys

    # 是否创建公开链接
    share = "--share" in sys.argv

    launch_app(share=share)


# ============= 使用说明 =============

"""
# 启动应用（本地）
python src/ui/app.py

# 启动应用（创建公开链接）
python src/ui/app.py --share

# 稍后会添加：
# 1. 完整的动画效果
# 2. 语音输入/输出
# 3. 头像上传功能
# 4. 主题切换
"""
