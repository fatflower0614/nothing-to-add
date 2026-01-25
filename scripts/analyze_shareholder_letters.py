#!/usr/bin/env python3
"""
分析巴菲特60年股东信（1965-2024）
提取关键内容、投资理念和问题
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any
import sys

sys.path.insert(0, str(Path.cwd()))


def analyze_shareholder_letters():
    """分析所有股东信"""
    letters_dir = Path('data/letters/shareholder_letters')

    if not letters_dir.exists():
        print(f"[ERROR] Directory not found: {letters_dir}")
        return

    # 获取所有股东信
    letter_files = sorted(letters_dir.glob('*.md'))

    print("=" * 70)
    print("巴菲特股东信分析 (1965-2024)")
    print("=" * 70)
    print(f"\n[INFO] 找到 {len(letter_files)} 封股东信\n")

    # 统计信息
    total_chars = 0
    total_words = 0
    letters_by_year = {}

    # 投资理念关键词
    investment_concepts = [
        'intrinsic value', 'intrinsic value of', 'moat', 'competitive advantage',
        'circle of competence', 'margin of safety', 'compound', 'compounding',
        'value investing', 'market price', 'book value',
        '内在价值', '护城河', '竞争优势', '能力圈', '安全边际', '复利',
        '价值投资', '股价', '账面价值', '内在价值'
    ]

    # 赌博/投机相关
    gambling_keywords = [
        'speculation', 'speculator', 'gambling', 'casino', 'leverage', 'derivative',
        '投机', '赌博', '赌场', '杠杆', '衍生品'
    ]

    concept_counts = defaultdict(int)
    gambling_counts = defaultdict(int)
    key_quotes = []

    print("[PROCESSING] 分析股东信内容...\n")

    for i, letter_file in enumerate(letter_files, 1):
        try:
            with open(letter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            year = letter_file.stem.split('_')[0]
            if not year.isdigit():
                # 处理类似 "2024_Letter" 的情况
                match = re.search(r'(\d{4})', letter_file.stem)
                if match:
                    year = match.group(1)
                else:
                    continue

            chars = len(content)
            # 粗略估计字数（中英文混合）
            words = len(content.split())

            total_chars += chars
            total_words += words

            letters_by_year[year] = {
                'file': letter_file.name,
                'chars': chars,
                'words': words
            }

            # 统计关键词出现次数
            content_lower = content.lower()

            for concept in investment_concepts:
                count = content_lower.count(concept.lower())
                if count > 0:
                    concept_counts[concept] += count

            for keyword in gambling_keywords:
                count = content_lower.count(keyword.lower())
                if count > 0:
                    gambling_counts[keyword] += count

            # 提取关键段落（包含重要概念的段落）
            if i % 10 == 0:
                print(f"  已处理 {i}/{len(letter_files)}...")

        except Exception as e:
            print(f"  [WARNING] 处理 {letter_file.name} 时出错: {e}")

    print(f"\n[OK] 分析完成！")
    print(f"\n总字数: {total_words:,} 字")
    print(f"总字符数: {total_chars:,} 字符")
    print(f"平均每封信: {total_words // len(letter_files):,} 字")

    # 显示投资理念统计
    print(f"\n" + "=" * 70)
    print("投资理念关键词出现频率")
    print("=" * 70)

    sorted_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"\n前15个最常出现的投资概念:")
    for concept, count in sorted_concepts[:15]:
        print(f"  {concept:30s} : {count:4d}次")

    # 显示赌博/投机相关统计
    print(f"\n" + "=" * 70)
    print("赌博/投机相关内容统计")
    print("=" * 70)

    total_gambling_mentions = sum(gambling_counts.values())
    print(f"\n赌博/投机相关词总出现次数: {total_gambling_mentions}次")

    if total_gambling_mentions > 0:
        print(f"\n详细分布:")
        for keyword, count in sorted(gambling_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword:20s} : {count:4d}次")
    else:
        print(f"\n  [INFO] 股东信中几乎没有直接提到赌博/投机")
        print(f"  [TIP] 这类内容主要在芒格的作品中")

    # 按年代分析
    print(f"\n" + "=" * 70)
    print("年代分析")
    print("=" * 70)

    decades = defaultdict(int)
    for year in letters_by_year.keys():
        if year.isdigit():
            decade = (int(year) // 10) * 10
            decades[f"{decade}s"] += 1

    print(f"\n各年代信件数量:")
    for decade in sorted(decades.keys()):
        count = decades[decade]
        print(f"  {decade}: {count}封")

    # 保存分析结果
    output_path = Path('data/qa_database/shareholder_letters_analysis.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    analysis_result = {
        'total_letters': len(letter_files),
        'total_words': total_words,
        'total_chars': total_chars,
        'years': list(letters_by_year.keys()),
        'investment_concepts': dict(sorted_concepts),
        'gambling_related': dict(gambling_counts),
        'total_gambling_mentions': total_gambling_mentions,
        'by_decade': dict(decades),
        'letters_detail': letters_by_year
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVE] 详细分析已保存至: {output_path}")

    return analysis_result


def extract_key_segments_from_letters():
    """从股东信中提取关键段落"""
    print(f"\n" + "=" * 70)
    print("提取关键段落")
    print("=" * 70)

    letters_dir = Path('data/letters/shareholder_letters')
    letter_files = sorted(letters_dir.glob('*.md'))

    # 关键主题和对应的关键词
    topics = {
        'intrinsic_value': ['intrinsic value', '内在价值', 'what is it worth'],
        'moat': ['moat', '护城河', 'competitive advantage', '竞争优势'],
        'management': ['management', 'manager', '管理层', 'managerial'],
        'mistakes': ['mistake', 'error', '错误', '失误', 'fail'],
        'market_vs_value': ['market price', 'intrinsic value', '股价', '内在价值'],
        'compounding': ['compound', '复利', 'grow'],
        'insurance': ['insurance', 'float', '保险', '浮存金'],
        'buy_hold': ['hold', 'holding', '持有', 'forever'],
    }

    key_segments = defaultdict(list)

    print(f"\n[PROCESSING] 提取关键段落...")

    for i, letter_file in enumerate(letter_files[:20], 1):  # 先分析前20封
        try:
            with open(letter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            year = letter_file.stem.split('_')[0]
            match = re.search(r'(\d{4})', year)
            if not match:
                continue
            year = match.group(1)

            # 按段落分割
            paragraphs = content.split('\n\n')

            for topic, keywords in topics.items():
                for para in paragraphs:
                    if len(para) < 50 or len(para) > 500:
                        continue

                    # 检查是否包含关键词
                    para_lower = para.lower()
                    if any(kw.lower() in para_lower for kw in keywords):
                        key_segments[topic].append({
                            'year': year,
                            'source': letter_file.name,
                            'text': para[:300],  # 限制长度
                            'topic': topic
                        })
                        break  # 每个主题只取一个段落

            if i % 5 == 0:
                print(f"  已处理 {i}/20...")

        except Exception as e:
            print(f"  [WARNING] {letter_file.name}: {e}")

    print(f"\n[OK] 提取完成！")

    # 显示各主题的段落数量
    print(f"\n提取的关键段落数量:")
    for topic, segments in sorted(key_segments.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {topic:20s}: {len(segments)}个")

    # 保存关键段落
    output_path = Path('data/qa_database/key_segments_from_letters.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dict(key_segments), f, ensure_ascii=False, indent=2)

    print(f"\n[SAVE] 关键段落已保存至: {output_path}")

    return key_segments


def main():
    """主函数"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "     巴菲特股东信深度分析工具".center(50) + "     █")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    # 1. 基础统计分析
    analysis = analyze_shareholder_letters()

    # 2. 提取关键段落
    key_segments = extract_key_segments_from_letters()

    # 总结
    print(f"\n" + "=" * 70)
    print("总结")
    print("=" * 70)

    print(f"\n股东信统计:")
    print(f"  - 总数: {analysis['total_letters']}封")
    print(f"  - 年份范围: {analysis['years'][0]} - {analysis['years'][-1]}")
    print(f"  - 总字数: {analysis['total_words']:,}字")

    print(f"\n关键发现:")
    print(f"  - 投资概念提及最多: {max(analysis['investment_concepts'].items(), key=lambda x: x[1])[0]}")
    print(f"  - 赌博相关提及: {analysis['total_gambling_mentions']}次")

    if analysis['total_gambling_mentions'] < 50:
        print(f"\n[TIP] 股东信中赌博相关内容较少，反赌博论述主要在:")
        print(f"      - 穷查理宝典")
        print(f"      - 芒格之路")
        print(f"      - 芒格股东会问答")

    print(f"\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
