#!/usr/bin/env python3
"""
测试RAG系统
"""

import os
from dotenv import load_dotenv
from rag.pipeline import get_rag_pipeline

# 加载环境变量
load_dotenv()

print("=" * 70)
print("Testing RAG System with GLM API")
print("=" * 70)
print()

# 创建RAG流程
pipeline = get_rag_pipeline()

# 初始化生成器
pipeline.init_generator()

# 测试问答
questions = [
    "什么是价值投资？",
    "巴菲特的投资理念是什么？",
    "芒格说过关于分散投资的话吗？"
]

for i, question in enumerate(questions, 1):
    print(f"\n{'='*70}")
    print(f"Question {i}: {question}")
    print(f"{'='*70}\n")

    result = pipeline.ask(question, top_k=3)

    print(f"\nAnswer:\n{result['answer']}")

    print(f"\n\nSources used:")
    for j, source in enumerate(result['sources'], 1):
        print(f"\n{j}. {source['metadata']}")
        print(f"   Preview: {source['text'][:100]}...")

    print("\n")

print("=" * 70)
print("Test completed!")
print("=" * 70)
