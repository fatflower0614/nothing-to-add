#!/usr/bin/env python3
"""
测试Polymarket和预测市场问题
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.pipeline import get_rag_pipeline

load_dotenv()

print("=" * 70)
print("Nothing to Add - Polymarket & Prediction Markets")
print("=" * 70)
print()

pipeline = get_rag_pipeline()
print("Connecting to GLM API with Buffett & Munger style...")
pipeline.init_generator()

# 问题：怎么看待Polymarket和预测市场
question = "怎么看待现在很火的Polymarket和预测市场？巴菲特和芒格会参与吗？"

print(f"\n{'='*70}")
print(f"Question: {question}")
print(f"{'='*70}\n")

print("Searching in Buffett and Munger's wisdom...")
result = pipeline.ask(question, top_k=5)

print("\n" + "="*70)
print("Buffett & Munger's Answer:")
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
    if title != 'Unknown':
        print(f"   {title}")

print("\n" + "="*70)
print("End of Answer")
print("="*70)
