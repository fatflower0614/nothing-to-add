#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rag.pipeline import get_rag_pipeline

load_dotenv()

print("=" * 70)
print("RAG System Test - Economic Moat Question")
print("=" * 70)
print()

pipeline = get_rag_pipeline()
print("Initializing GLM API...")
pipeline.init_generator()

question = "What is an economic moat? How does Buffett view it?"

print(f"\n{'='*70}")
print(f"Question: {question}")
print(f"{'='*70}\n")

print("Retrieving relevant documents...")
result = pipeline.ask(question, top_k=3)

print("\n" + "="*70)
print("Answer:")
print("="*70)
print(result['answer'])

print("\n" + "="*70)
print("Sources:")
print("="*70)
for i, source in enumerate(result['sources'], 1):
    year = source['metadata'].get('year', 'Unknown')
    print(f"\n{i}. {source['metadata']['source']} ({year})")
    print(f"   {source['metadata']['title']}")
    print(f"   Preview: {source['text'][:150]}...")

print("\n" + "="*70)
print("Test completed!")
print("="*70)
