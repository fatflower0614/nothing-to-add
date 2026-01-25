#!/usr/bin/env python3
"""
从巴菲特芒格的资料中提取问答对
建立QA数据库，提高检索准确度
"""

import re
from pathlib import Path
from typing import List, Dict, Any
import json


def extract_qa_from_text(content: str, source: str) -> List[Dict[str, Any]]:
    """
    从文本中提取问答对

    Args:
        content: 文本内容
        source: 来源文件名

    Returns:
        问答列表
    """
    qa_pairs = []

    # 模式1: 股东年会问答
    # 格式: 股东：问题？\n芒格/巴菲特：回答
    pattern1 = r'股东.{5,300}？.{0,100}?[芒格巴菲特].{20,1000}'
    matches1 = re.findall(pattern1, content, re.DOTALL)

    for match in matches1:
        # 分离问题和回答
        parts = match.split('？', 1)
        if len(parts) == 2:
            question = '股东：' + parts[0].replace('股东', '', 1).strip()
            answer = parts[1].strip()

            # 清理
            question = re.sub(r'\s+', ' ', question)
            answer = re.sub(r'\s+', ' ', answer)

            if len(question) > 10 and len(answer) > 20:
                qa_pairs.append({
                    'question': question,
                    'answer': answer[:500],  # 限制长度
                    'source': source,
                    'type': 'shareholder_qa'
                })

    # 模式2: 提到投资理念的具体问题
    # 格式包含关键词: 如何, 怎么, 为什么, 是否, 能否
    investment_keywords = [
        '护城河', '能力圈', '安全边际', '复利', '长期持有',
        '价值投资', '选股', '公司分析'
    ]

    for keyword in investment_keywords:
        # 查找包含这些关键词的问题
        pattern = rf'.{{10,200}}{keyword}.{{5,200}}？'
        matches = re.findall(pattern, content)

        for match in matches[:3]:  # 每个关键词只取前3个
            question = match + '？'
            # 查找对应的回答（在同一个段落或下一段）
            answer_start = content.find(match)
            answer_segment = content[answer_start:answer_start+1000]

            # 提取回答部分
            answer_match = re.search(r'[：,]\s*(.{100,500})', answer_segment)
            if answer_match:
                answer = answer_match.group(1)

                qa_pairs.append({
                    'question': question,
                    'answer': answer,
                    'source': source,
                    'type': 'investment_concept'
                })

    return qa_pairs


def extract_qa_from_mungers_way() -> List[Dict[str, Any]]:
    """从《芒格之路》中提取问答"""

    file_path = Path('data/cleaned/core/Mungers_Way_1987-2022.md')

    if not file_path.exists():
        print(f"[WARNING] File not found: {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Processing: Mungers_Way_1987-2022.md ({len(content)} chars)")

    # 提取问答
    qa_pairs = extract_qa_from_text(content, 'Mungers_Way_1987-2022')

    print(f"  Found {len(qa_pairs)} Q&A pairs")

    return qa_pairs


def extract_qa_from_shareholder_letters() -> List[Dict[str, Any]]:
    """从股东信中提取问答"""

    qa_pairs = []
    letters_dir = Path('data/cleaned/letters')

    if not letters_dir.exists():
        print(f"[WARNING] Directory not found: {letters_dir}")
        return qa_pairs

    # 获取所有股东信文件
    letter_files = list(letters_dir.glob('*.md'))

    print(f"\nProcessing {len(letter_files)} shareholder letters...")

    for letter_file in letter_files[:10]:  # 先处理前10封
        with open(letter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取问答
        pairs = extract_qa_from_text(content, letter_file.name)
        qa_pairs.extend(pairs)

    print(f"  Total Q&A from letters: {len(qa_pairs)}")

    return qa_pairs


def create_qa_database(qa_pairs: List[Dict[str, Any]], output_path: str):
    """
    创建QA数据库（JSON格式）

    Args:
        qa_pairs: 问答列表
        output_path: 输出文件路径
    """

    # 按类别分组
    categorized = {}
    for qa in qa_pairs:
        category = qa.get('type', 'other')
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(qa)

    # 保存
    output_data = {
        'total': len(qa_pairs),
        'categories': {k: len(v) for k, v in categorized.items()},
        'qa_pairs': categorized
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] QA database saved to: {output_path}")
    print(f"   Total Q&A pairs: {len(qa_pairs)}")
    print(f"   Categories: {list(categorized.keys())}")


def create_question_tags(qa_pairs: List[Dict[str, Any]], output_path: str):
    """
    为问题创建标签

    Args:
        qa_pairs: 问答列表
        output_path: 输出文件路径
    """

    # 提取关键词作为标签
    tagged_questions = []

    for qa in qa_pairs:
        question = qa['question']

        # 提取关键词
        keywords = []

        # 投资概念
        concepts = ['护城河', '能力圈', '复利', '价值投资', '安全边际', '长期',
                   '持有', '买入', '卖出', '选股', '分析']
        for concept in concepts:
            if concept in question:
                keywords.append(concept)

        # 问题类型
        if '如何' in question or '怎么' in question:
            keywords.append('方法类')
        elif '为什么' in question:
            keywords.append('原因类')
        elif '是否' in question or '能否' in question:
            keywords.append('判断类')
        elif '什么' in question:
            keywords.append('定义类')

        tagged_questions.append({
            'question': question,
            'answer': qa['answer'],
            'source': qa['source'],
            'tags': list(set(keywords))
        })

    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tagged_questions, f, ensure_ascii=False, indent=2)

    print(f"[OK] Tagged questions saved to: {output_path}")

    return tagged_questions


def main():
    """主函数"""
    print("="*60)
    print("QA Extraction - Buffett & Munger")
    print("="*60)

    all_qa_pairs = []

    # 1. 从《芒格之路》提取
    print("\n[1/3] Extracting from Mungers Way...")
    qa_pairs = extract_qa_from_mungers_way()
    all_qa_pairs.extend(qa_pairs)

    # 2. 从股东信提取
    print("\n[2/3] Extracting from Shareholder Letters...")
    qa_pairs = extract_qa_from_shareholder_letters()
    all_qa_pairs.extend(qa_pairs)

    # 3. 创建数据库
    print("\n[3/3] Creating QA databases...")

    output_dir = Path('data/qa_database')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存完整QA库
    create_qa_database(
        all_qa_pairs,
        output_dir / 'qa_database.json'
    )

    # 保存带标签的问题
    create_question_tags(
        all_qa_pairs,
        output_dir / 'tagged_questions.json'
    )

    print("\n" + "="*60)
    print("Extraction Complete!")
    print("="*60)
    print(f"\nNext steps:")
    print(f"1. Review the extracted Q&A in data/qa_database/")
    print(f"2. Add to RAG system for better matching")
    print(f"3. Test with user questions")


if __name__ == '__main__':
    main()
