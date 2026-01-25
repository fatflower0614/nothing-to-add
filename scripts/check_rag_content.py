#!/usr/bin/env python3
"""
检查RAG库中的内容，特别关注股东信
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from rag.vector_store import VectorStore


def check_rag_for_letters():
    """检查RAG库中是否有股东信"""
    print("=" * 70)
    print("检查RAG库中的股东信")
    print("=" * 70)

    store = VectorStore('./data/chroma')
    has_collection = store.get_collection()

    if not has_collection or store.collection is None:
        print("[ERROR] RAG库为空")
        return

    # 获取所有文档的metadata
    all_data = store.collection.get(include=['metadatas', 'documents'])

    if not all_data or not all_data['metadatas']:
        print("[ERROR] RAG库没有数据")
        return

    total_docs = len(all_data['metadatas'])
    print(f"\n[INFO] RAG库总文档数: {total_docs}")

    # 统计来源
    sources = {}
    letter_sources = {}

    for i, meta in enumerate(all_data['metadatas']):
        source = meta.get('source', 'Unknown')

        if source in sources:
            sources[source] += 1
        else:
            sources[source] = 1

        # 检查是否是股东信
        if 'letter' in source.lower() or 'shareholder' in source.lower():
            if source in letter_sources:
                letter_sources[source] += 1
            else:
                letter_sources[source] = 1

    print(f"\n[STATS] 来源统计 (Top 15):")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {source}: {count}个文档片段")

    print(f"\n" + "=" * 70)
    print("股东信检查")
    print("=" * 70)

    if letter_sources:
        print(f"\n[OK] 找到 {len(letter_sources)} 个股东信来源:")
        total_letter_docs = sum(letter_sources.values())
        print(f"    总计: {total_letter_docs}个文档片段")

        for source, count in sorted(letter_sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {source}: {count}个片段")
    else:
        print(f"\n[WARNING] RAG库中没有股东信内容！")
        print(f"\n需要添加股东信到RAG库")

    return letter_sources


if __name__ == '__main__':
    check_rag_for_letters()
