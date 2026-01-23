#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rag.pipeline import get_rag_pipeline

load_dotenv()

print("=" * 70)
print("Nothing to Add - Career Advice from Buffett and Munger")
print("=" * 70)
print()

pipeline = get_rag_pipeline()
print("Connecting to GLM API...")
pipeline.init_generator()

question = "我现在处于就业迷茫状态，不知道该选择什么工作，巴菲特和芒格会给我什么建议？"

print(f"\n{'='*70}")
print(f"Question: {question}")
print(f"{'='*70}\n")

print("Searching for relevant advice in documents...")
result = pipeline.ask(question, top_k=5)

print("\n" + "="*70)
print("Buffett and Munger's Advice:")
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
    print(f"   {title}")

print("\n" + "="*70)
print("End of Advice")
print("="*70)
