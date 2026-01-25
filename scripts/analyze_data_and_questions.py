#!/usr/bin/env python3
"""
分析数据完整性和提取高频问题
"""
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path.cwd()))

from rag.vector_store import VectorStore


def check_data_completeness():
    """检查数据完整性"""
    print("=" * 70)
    print("数据完整性检查")
    print("=" * 70)

    books_dir = Path('data/books')
    cleaned_dir = Path('data/cleaned')

    # 获取所有PDF文件
    pdf_files = []
    for pdf_path in books_dir.rglob('*.pdf'):
        pdf_files.append(pdf_path)

    # 获取所有清洗文件
    cleaned_files = []
    for cleaned_path in cleaned_dir.rglob('*.md'):
        cleaned_files.append(cleaned_path)

    print(f"\n[PDF] PDF files: {len(pdf_files)}")
    print(f"[CLEANED] Cleaned files: {len(cleaned_files)}")

    # 分类清洗文件
    cleaned_by_category = defaultdict(list)
    for f in cleaned_files:
        rel_path = f.relative_to(cleaned_dir)
        if len(rel_path.parts) >= 2:
            category = rel_path.parts[0]
            cleaned_by_category[category].append(f)

    print(f"\n[DIR] Cleaned files by category:")
    for category, files in sorted(cleaned_by_category.items()):
        print(f"  - {category}: {len(files)} files")

    # 检查哪些PDF没有对应的清洗文件
    print(f"\n[STATUS] PDF cleaning status:")
    for pdf in pdf_files:
        rel_path = pdf.relative_to(books_dir)
        expected_cleaned = cleaned_dir / rel_path.with_suffix('.md')

        # 检查可能的命名差异
        possible_names = [
            expected_cleaned,
            cleaned_dir / 'core' / 'Poor_Charlies_Almanack.md',  # 穷查理宝典
            cleaned_dir / 'core' / 'Poor_Richards_Almanack.md',  # 富兰克林年鉴
        ]

        is_cleaned = any(f.exists() for f in possible_names)
        status = "[OK]" if is_cleaned else "[MISSING]"
        print(f"  {status} {pdf.name}")

    return cleaned_files


def check_rag_database():
    """检查RAG数据库"""
    print(f"\n" + "=" * 70)
    print("RAG数据库检查")
    print("=" * 70)

    try:
        store = VectorStore('./data/chroma')
        collection = store.get_collection()

        if collection is None:
            print("[X] RAG数据库为空，需要构建")
            return None

        # 获取所有文档的metadata
        all_data = collection.get(include=['metadatas'])

        if all_data and all_data['metadatas']:
            total_docs = len(all_data['metadatas'])

            # 统计来源
            sources = Counter()
            for meta in all_data['metadatas']:
                source = meta.get('source', 'Unknown')
                sources[source] += 1

            print(f"\n[STATS] RAG数据库总文档数: {total_docs}")
            print(f"\n[SOURCE] 来源分布:")
            for source, count in sources.most_common():
                print(f"  - {source}: {count}个文档片段")

            return total_docs, sources
        else:
            print("[X] RAG数据库没有数据")
            return None

    except Exception as e:
        print(f"[X] 检查RAG数据库时出错: {e}")
        return None


def extract_questions_from_text(content: str, source: str) -> List[Dict[str, Any]]:
    """从文本中提取问题"""
    questions = []

    # 模式1: 股东问答 (中文)
    pattern_cn = r'股东[：:][^？？\n]{5,300}[？?]'
    matches_cn = re.findall(pattern_cn, content)

    for match in matches_cn:
        # 清理问题
        question = match.strip()
        question = re.sub(r'\s+', ' ', question)
        question = question.replace('股东：', '').replace('股东:', '').strip()

        if len(question) > 8:
            questions.append({
                'question': question,
                'source': source,
                'type': 'shareholder_qa',
                'language': 'cn'
            })

    # 模式2: 问号结尾的问题 (英文和中文)
    # 更宽松的模式，寻找包含关键词的问句
    question_patterns = [
        r'(?:^|\n)[^？\n]{10,200}[？?]',  # 任何问号结尾的句子
        r'(?:问题|Question|Q[:\s])[^？\n]{5,200}[？?]',  # 明确标记的问题
    ]

    for pattern in question_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            question = match.strip()
            question = re.sub(r'^(问题|Question|Q[:\s])', '', question).strip()

            if len(question) > 8 and len(question) < 200:
                questions.append({
                    'question': question,
                    'source': source,
                    'type': 'general_question',
                    'language': 'cn' if re.search(r'[\u4e00-\u9fff]', question) else 'en'
                })

    return questions


def analyze_all_questions(cleaned_files: List[Path]):
    """分析所有文件中的问题"""
    print(f"\n" + "=" * 70)
    print("问题分析")
    print("=" * 70)

    all_questions = []
    questions_by_source = defaultdict(list)

    print(f"\n[PROCESSING] 正在分析 {len(cleaned_files)} 个文件...")

    for i, file_path in enumerate(cleaned_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取问题
            questions = extract_questions_from_text(content, file_path.name)

            if questions:
                all_questions.extend(questions)
                questions_by_source[file_path.name] = questions

            if i % 5 == 0:
                print(f"  已处理 {i}/{len(cleaned_files)}...")

        except Exception as e:
            print(f"  [WARNING] 处理 {file_path.name} 时出错: {e}")

    print(f"\n[OK] 共提取到 {len(all_questions)} 个问题")

    # 分析高频问题
    print(f"\n" + "-" * 70)
    print("高频问题分析")
    print("-" * 70)

    # 按来源统计
    print(f"\n[STATS] 各文件问题数量:")
    for source, questions in sorted(questions_by_source.items(),
                                    key=lambda x: len(x[1]),
                                    reverse=True):
        print(f"  {source}: {len(questions)}个问题")

    # 提取问题关键词用于聚类相似问题
    question_keywords = defaultdict(list)

    for q in all_questions:
        text = q['question'].lower()

        # 投资相关关键词
        if any(kw in text for kw in ['投资', 'invest', '持有', 'hold', '买入', 'buy', '卖出', 'sell']):
            question_keywords['投资决策'].append(q['question'][:60])

        # 公司分析相关
        elif any(kw in text for kw in ['公司', 'company', '企业', 'business', '护城河', 'moat']):
            question_keywords['公司分析'].append(q['question'][:60])

        # 市场相关
        elif any(kw in text for kw in ['市场', 'market', '股市', 'stock']):
            question_keywords['市场看法'].append(q['question'][:60])

        # 风险相关
        elif any(kw in text for kw in ['风险', 'risk', '保险', 'insurance', '衍生品', 'derivative']):
            question_keywords['风险管理'].append(q['question'][:60])

        # 人生/哲学相关
        elif any(kw in text for kw in ['人生', 'life', '智慧', 'wisdom', '思维', 'thinking']):
            question_keywords['人生智慧'].append(q['question'][:60])

        # 赌博相关
        elif any(kw in text for kw in ['赌博', 'gambling', '赌场', 'casino', '博彩']):
            question_keywords['赌博投机'].append(q['question'][:60])

        # 其他
        else:
            question_keywords['其他'].append(q['question'][:60])

    print(f"\n[KEY] 按主题分类的问题数量:")
    for category, questions in sorted(question_keywords.items(),
                                      key=lambda x: len(x[1]),
                                      reverse=True):
        print(f"  - {category}: {len(questions)}个")

    # 显示每个主题的样例问题
    print(f"\n" + "-" * 70)
    print("各主题样例问题")
    print("-" * 70)

    for category, questions in question_keywords.items():
        if questions:
            print(f"\n【{category}】(共{len(questions)}个)")
            # 去重并显示前3个
            unique_questions = list(set(questions))[:3]
            for q in unique_questions:
                print(f"  - {q}...")

    # 保存完整问题列表
    output_path = Path('data/qa_database/all_questions_analysis.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    analysis_result = {
        'total_questions': len(all_questions),
        'by_source': {k: len(v) for k, v in questions_by_source.items()},
        'by_category': {k: len(v) for k, v in question_keywords.items()},
        'sample_questions_by_category': {
            k: list(set(v))[:5] for k, v in question_keywords.items()
        },
        'all_questions': [
            {
                'question': q['question'],
                'source': q['source'],
                'type': q['type'],
                'language': q['language']
            }
            for q in all_questions
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVE] 完整分析已保存至: {output_path}")

    return all_questions, question_keywords


def find_duplicate_questions(all_questions: List[Dict[str, Any]]):
    """找出重复或高度相似的问题"""
    print(f"\n" + "=" * 70)
    print("重复问题分析")
    print("=" * 70)

    # 简单的相似度检测：提取关键词并分组
    question_groups = defaultdict(list)

    for q in all_questions:
        # 提取问题中的关键词（去除标点和停用词）
        text = q['question']

        # 提取关键概念作为分组依据
        keywords = []

        # 常见投资概念
        concepts = [
            '护城河', '能力圈', '安全边际', '复利', '价值投资',
            '长期持有', '选股', '现金流', '管理层', '竞争优势',
            'moat', 'circle of competence', 'margin of safety',
            'compound', 'value investing', 'hold', 'management'
        ]

        for concept in concepts:
            if concept.lower() in text.lower():
                keywords.append(concept)

        if keywords:
            key = '_'.join(sorted(keywords))
        else:
            # 如果没有关键词，使用前10个字符
            key = text[:10]

        question_groups[key].append({
            'question': text,
            'source': q['source']
        })

    # 找出有重复的组
    duplicates = {k: v for k, v in question_groups.items() if len(v) > 1}

    print(f"\n[REPEAT] 发现 {len(duplicates)} 组相似问题")

    # 显示重复最多的问题
    print(f"\n[STATS] 重复次数最多的问题类型:")
    sorted_duplicates = sorted(duplicates.items(),
                               key=lambda x: len(x[1]),
                               reverse=True)

    for i, (key, questions) in enumerate(sorted_duplicates[:10], 1):
        print(f"\n{i}. 关键词: [{key}] (出现{len(questions)}次)")
        # 显示前2个例子
        for q in questions[:2]:
            print(f"   - {q['question'][:80]}...")
            print(f"     来源: {q['source']}")

    return duplicates


def main():
    """主函数"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "     数据完整性与问题分析工具".center(56) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    # 1. 检查数据完整性
    cleaned_files = check_data_completeness()

    # 2. 检查RAG数据库
    rag_info = check_rag_database()

    # 3. 分析所有问题
    all_questions, question_keywords = analyze_all_questions(cleaned_files)

    # 4. 找出重复问题
    duplicates = find_duplicate_questions(all_questions)

    # 总结报告
    print(f"\n" + "=" * 70)
    print("总结报告")
    print("=" * 70)

    print(f"\n[STATS] 数据统计:")
    print(f"  - 清洗文件: {len(cleaned_files)}个")
    if rag_info:
        print(f"  - RAG文档: {rag_info[0]}个")
    print(f"  - 提取问题: {len(all_questions)}个")

    print(f"\n[FINDING] 主要发现:")
    print(f"  - 问题最多的主题: {max(question_keywords.items(), key=lambda x: len(x[1]))[0]}")
    print(f"  - 相似问题组数: {len(duplicates)}组")

    print(f"\n[TIP] 建议:")
    if len(duplicates) > 50:
        print(f"  1. 有较多重复问题，可以考虑聚类合并")

    investment_questions = question_keywords.get('投资决策', [])
    if len(investment_questions) > 50:
        print(f"  2. 投资决策类问题最多，可以优先处理")

    print(f"\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
