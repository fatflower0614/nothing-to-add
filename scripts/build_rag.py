#!/usr/bin/env python3
"""
构建RAG向量数据库
读取清洗后的数据，向量化，存储到ChromaDB
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import re

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.embeddings import get_embedding_model
from rag.vector_store import VectorStore


def load_documents_from_directory(directory: str) -> List[Dict[str, Any]]:
    """
    从目录加载所有markdown文档

    Args:
        directory: 目录路径

    Returns:
        文档列表
    """
    documents = []
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"[WARNING] Directory not found: {directory}")
        return documents

    # 递归查找所有.md文件
    md_files = list(dir_path.rglob("*.md"))

    print(f"Found {len(md_files)} markdown files in {directory}")

    for md_file in md_files:
        # 读取文件
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取元数据（如果存在）
            metadata = extract_metadata(content, md_file)

            # 如果有元数据头部，去掉它
            content = remove_metadata_header(content)

            # 分块
            chunks = split_text_into_chunks(content, chunk_size=500, overlap=50)

            # 为每个块创建文档
            for i, chunk in enumerate(chunks):
                documents.append({
                    'text': chunk,
                    'metadata': {
                        **metadata,
                        'chunk_id': f"{md_file.stem}_chunk_{i}",
                        'file_path': str(md_file)
                    }
                })

            print(f"  [OK] {md_file.name}: {len(chunks)} chunks")

        except Exception as e:
            print(f"  [ERROR] {md_file.name}: {e}")

    return documents


def extract_metadata(content: str, file_path: Path) -> Dict[str, Any]:
    """
    从文档中提取元数据

    Args:
        content: 文档内容
        file_path: 文件路径

    Returns:
        元数据字典
    """
    metadata = {
        'source': 'Unknown',
        'type': 'Document',
        'year': 'Unknown',
        'title': file_path.stem
    }

    # 检查是否有YAML头部
    yaml_pattern = r'^---\n(.*?)\n---\n'
    match = re.match(yaml_pattern, content, re.DOTALL)

    if match:
        yaml_content = match.group(1)
        # 解析YAML
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                metadata[key] = value

    # 从文件路径推断信息
    path_parts = file_path.parts

    if 'letters' in path_parts:
        metadata['type'] = 'Shareholder Letter'
    elif 'core' in path_parts:
        metadata['type'] = 'Core Book'
    elif 'recommended' in path_parts:
        metadata['type'] = 'Recommended Book'

    if 'shareholder_letters' in path_parts:
        # 巴菲特股东信
        match = re.search(r'(\d{4})', file_path.stem)
        if match:
            metadata['source'] = 'Berkshire Hathaway Letter'
            metadata['year'] = match.group(1)
            metadata['title'] = f"{metadata['year']} Letter to Shareholders"

    return metadata


def remove_metadata_header(content: str) -> str:
    """
    删除YAML元数据头部

    Args:
        content: 文档内容

    Returns:
        删除头部后的内容
    """
    yaml_pattern = r'^---\n.*?\n---\n'
    content = re.sub(yaml_pattern, '', content, flags=re.DOTALL)
    return content


def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    将文本切分成块

    Args:
        text: 输入文本
        chunk_size: 每块字符数
        overlap: 块之间重叠字符数

    Returns:
        文本块列表
    """
    # 首先按段落分割
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # 如果当前块加上新段落超过限制
        if len(current_chunk) + len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())

            # 开始新块，包含重叠部分
            if overlap > 0 and chunks:
                # 获取上一个块的末尾作为重叠
                last_chunk = chunks[-1]
                overlap_text = last_chunk[-overlap:] if len(last_chunk) > overlap else last_chunk
                current_chunk = overlap_text + "\n\n" + paragraph
            else:
                current_chunk = paragraph
        else:
            # 添加到当前块
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

    # 添加最后一个块
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def build_vector_database(
    data_dir: str = "./data/cleaned",
    persist_dir: str = "./data/chroma",
    collection_name: str = "buffett_munger_docs"
):
    """
    构建向量数据库

    Args:
        data_dir: 数据目录
        persist_dir: 向量数据库存储目录
        collection_name: 集合名称
    """
    print("=" * 70)
    print("Building RAG Vector Database")
    print("=" * 70)
    print()

    # 1. 加载文档
    print("Step 1: Loading documents...")
    print(f"Data directory: {data_dir}")
    print()

    documents = load_documents_from_directory(data_dir)

    if not documents:
        print("[ERROR] No documents found!")
        return False

    print(f"\nLoaded {len(documents)} chunks from {len(set(d['metadata']['file_path'] for d in documents))} files")
    print()

    # 2. 初始化向量化模型
    print("Step 2: Initializing embedding model...")
    embedding_model = get_embedding_model()
    print()

    # 3. 初始化向量数据库
    print("Step 3: Initializing vector store...")
    vector_store = VectorStore(
        persist_directory=persist_dir,
        collection_name=collection_name
    )

    # 创建新集合（删除旧的）
    vector_store.create_collection()
    print()

    # 4. 向量化文档
    print("Step 4: Generating embeddings...")
    print("This may take a while...")

    texts = [doc['text'] for doc in documents]
    embeddings = embedding_model.embed_texts(texts)

    print(f"Generated {len(embeddings)} embeddings")
    print()

    # 5. 存储到向量数据库
    print("Step 5: Storing in vector database...")

    metadatas = [doc['metadata'] for doc in documents]
    ids = [doc['metadata']['chunk_id'] for doc in documents]

    vector_store.add_documents(
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print()

    # 6. 总结
    print("=" * 70)
    print("Build Summary")
    print("=" * 70)
    print(f"Documents processed: {len(documents)} chunks")
    print(f"Source files: {len(set(d['metadata']['file_path'] for d in documents))}")
    print(f"Embedding dimension: {len(embeddings[0])}")
    print(f"Vector database: {persist_dir}")
    print(f"Collection: {collection_name}")
    print()
    print("✅ Vector database built successfully!")
    print()
    print("You can now use the RAG system:")
    print("  python -m rag.pipeline")
    print("  or")
    print("  python scripts/build_rag.py")

    return True


def main():
    """主函数"""
    print()
    print("This script will build the vector database for the RAG system.")
    print()
    print("It will:")
    print("1. Load all markdown files from data/cleaned/")
    print("2. Split them into chunks")
    print("3. Generate embeddings (vectors)")
    print("4. Store in ChromaDB")
    print()

    # 询问是否继续
    response = input("Continue? (y/n): ")

    if response.lower() != 'y':
        print("Cancelled.")
        return 0

    print()

    # 构建向量数据库
    success = build_vector_database()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
