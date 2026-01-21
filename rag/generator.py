#!/usr/bin/env python3
"""
生成器模块
使用AI模型生成答案（支持OpenAI和GLM）
"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI


class AnswerGenerator:
    """答案生成器"""

    def __init__(
        self,
        model: str = "glm-4-flash",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        初始化生成器

        Args:
            model: 模型名称
                - GLM: glm-4-flash, glm-4-plus, glm-4-air
                - OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
            api_key: API密钥（如果不提供，从环境变量读取）
            base_url: API base URL（如果不提供，自动检测）
            temperature: 温度参数（0-2，越高越随机）
        """
        self.model = model
        self.temperature = temperature

        # 获取API密钥
        if api_key is None:
            # 优先使用GLM密钥
            api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found. "
                    "Please set GLM_API_KEY or OPENAI_API_KEY in environment variables."
                )

        # 自动检测base_url
        if base_url is None:
            # 如果是GLM模型，使用智谱AI的base_url
            if model.startswith("glm-"):
                base_url = "https://open.bigmodel.cn/api/paas/v4/"
            else:
                # OpenAI使用默认base_url
                base_url = None

        # 创建客户端
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.provider = "GLM"
        else:
            self.client = OpenAI(api_key=api_key)
            self.provider = "OpenAI"

        print(f"AnswerGenerator initialized (provider={self.provider}, model={model})")

    def generate(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        生成答案

        Args:
            question: 用户问题
            context: 检索到的上下文
            system_prompt: 系统提示词

        Returns:
            生成的答案
        """
        # 默认系统提示词
        if system_prompt is None:
            system_prompt = """你是沃伦·巴菲特和查理·芒格的AI助手。你的任务是根据提供的文档回答问题。

请遵循以下原则：
1. 只使用提供的文档中的信息
2. 如果文档中没有相关信息，诚实地说"根据现有文档，我无法回答这个问题"
3. 引用具体的来源（年份、文档名称）
4. 保持巴菲特和芒格的说话风格：简洁、幽默、用比喻
5. 如果可能，用他们常说过的原话"""

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""根据以下文档回答问题：

问题：{question}

相关文档：
{context}

请基于上述文档内容回答问题。"""
            }
        ]

        # 调用API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2000
            )

            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            return f"生成答案时出错：{str(e)}"

    def generate_stream(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None
    ):
        """
        流式生成答案（逐字输出）

        Args:
            question: 用户问题
            context: 检索到的上下文
            system_prompt: 系统提示词

        Yields:
            生成的文本片段
        """
        # 默认系统提示词
        if system_prompt is None:
            system_prompt = """你是沃伦·巴菲特和查理·芒格的AI助手。"""

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""根据以下文档回答问题：

问题：{question}

相关文档：
{context}

请基于上述文档内容回答问题。"""
            }
        ]

        # 调用API（流式）
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2000,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"生成答案时出错：{str(e)}"


# 便捷函数
def get_generator(
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    temperature: float = 0.7
) -> AnswerGenerator:
    """获取生成器实例"""
    return AnswerGenerator(model, api_key, temperature)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("AnswerGenerator Test")
    print("=" * 60)

    # 检查API密钥
    api_key = os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[WARNING] No API key found in environment variables")
        print("To test this module, set your API key:")
        print("  export GLM_API_KEY='your-glm-key'")
        print("  or")
        print("  export OPENAI_API_KEY='your-openai-key'")
        print("\nSkipping test...")
        exit(0)

    # 创建生成器（自动检测使用GLM还是OpenAI）
    if os.getenv("GLM_API_KEY"):
        generator = get_generator(model="glm-4-flash")
        print("\nUsing GLM API")
    else:
        generator = get_generator(model="gpt-4o-mini")
        print("\nUsing OpenAI API")

    # 测试数据
    test_question = "什么是价值投资？"
    test_context = """
[来源: 巴菲特股东信, 1965]
价值投资的核心原则是：以低于内在价值的价格购买优秀的企业，并长期持有。

[来源: 巴菲特股东信, 1984]
价值投资不是找到被人遗忘的便宜货，而是以合理的价格买优秀的企业。

[来源: 芒格讲话, 1994]
我们寻找有护城河的企业，这些企业能够长期保持竞争优势。
"""

    print("\nTest question:", test_question)
    print("\nGenerating answer...\n")

    # 生成答案
    answer = generator.generate(test_question, test_context)

    print("Answer:")
    print("-" * 60)
    print(answer)
    print("-" * 60)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
