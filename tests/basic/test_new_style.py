#!/usr/bin/env python3
"""
测试新的巴菲特芒格风格提示词
"""
import os
from dotenv import load_dotenv
from rag.pipeline import get_rag_pipeline

load_dotenv()

print("=" * 70)
print("Testing New Buffett & Munger Style Prompt")
print("=" * 70)
print()

pipeline = get_rag_pipeline()
print("Initializing GLM API with new prompt...")
pipeline.init_generator()

# 测试问题
question = "我现在处于就业迷茫状态，不知道该选择什么工作，你有什么建议？"

print(f"\n{'='*70}")
print(f"Question: {question}")
print(f"{'='*70}\n")

print("Thinking and retrieving relevant documents...")
result = pipeline.ask(question, top_k=5)

print("\n" + "="*70)
print("Buffett & Munger's Answer (New Style):")
print("="*70)
print(result['answer'])

print("\n" + "="*70)
print("Sources:")
print("="*70)
for i, source in enumerate(result['sources'], 1):
    year = source['metadata'].get('year', 'Unknown')
    src = source['metadata'].get('source', 'Unknown')
    title = source['metadata'].get('title', 'Unknown')
    print(f"\n{i}. {src} ({year})")

print("\n" + "="*70)
print("Test completed!")
print("="*70)
print("\nNotice: The answer should now be more conversational and sound more")
print("like Buffett and Munger themselves - using metaphors, humor, and their")
print("natural speaking style!")
