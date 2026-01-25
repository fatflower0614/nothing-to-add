#!/usr/bin/env python3
"""
从股东信和其他文档中提取问题，建立问题库和案例库
用于AI Agent主动引导对话
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


def extract_questions_from_letters() -> List[Dict[str, Any]]:
    """从股东信中提取问题"""
    print("=" * 70)
    print("从股东信中提取问题")
    print("=" * 70)

    letters_dir = Path('data/letters/shareholder_letters')
    letter_files = sorted(letters_dir.glob('*.md'))

    all_questions = []

    # 股东信中的问题模式（虽然不是Q&A格式，但有反问句、疑问句）
    question_patterns = [
        # 疑问词开头
        r'[?\s](What|Which|Who|When|Where|Why|How)[^\.?\n]{10,200}[??]',
        r'[?\s](什么|哪些|谁|何时|何地|为何|如何|怎么)[^？？\n]{10,200}[??]',

        # 反问句
        r'[^\.?\n]{10,200}[??](?:\s+|$)',

        # 特定模式
        r'(Is|Are|Will|Would|Could|Should|Can|Do|Does)[^\.?\n]{10,200}[??]',
        r'(是|是否|会|能否|可以|是否)[^？？\n]{10,200}[??]',

        # 包含特定词汇的问句
        r'[^\.?\n]{15,200}(?:question|wonder|ask|问题)[^\.?\n]{5,100}[??]',
    ]

    print(f"\n[PROCESSING] 分析 {len(letter_files)} 封股东信...")

    for i, letter_file in enumerate(letter_files, 1):
        try:
            with open(letter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            year = letter_file.stem.split('_')[0]
            match = re.search(r'(\d{4})', year)
            if not match:
                continue
            year = match.group(1)

            # 使用所有模式匹配
            for pattern in question_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    question = match.group(0).strip()

                    # 清理
                    question = re.sub(r'^[\s\W]+', '', question)
                    question = question.strip()

                    # 过滤长度
                    if 10 < len(question) < 200:
                        all_questions.append({
                            'question': question,
                            'source': f"Berkshire_{year}",
                            'year': year,
                            'type': 'shareholder_letter',
                            'language': 'en' if re.match(r'^[A-Za-z]', question) else 'cn'
                        })

            if i % 10 == 0:
                print(f"  已处理 {i}/{len(letter_files)}...")

        except Exception as e:
            print(f"  [WARNING] {letter_file.name}: {e}")

    print(f"\n[OK] 从股东信中提取 {len(all_questions)} 个问题")
    return all_questions


def load_existing_questions() -> List[Dict[str, Any]]:
    """加载已提取的问题"""
    print(f"\n" + "=" * 70)
    print("加载已提取的问题")
    print("=" * 70)

    # 从之前的分析结果加载
    analysis_file = Path('data/qa_database/all_questions_analysis.json')

    if not analysis_file.exists():
        print(f"[WARNING] 未找到问题分析文件")
        return []

    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('all_questions', [])
    print(f"\n[OK] 加载 {len(questions)} 个已提取的问题")

    return questions


def categorize_questions(questions: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """对问题进行分类"""
    print(f"\n" + "=" * 70)
    print("问题分类")
    print("=" * 70)

    categories = {
        'investment_strategy': {
            'name': '投资策略',
            'keywords': ['投资', 'invest', 'strategy', '策略', 'portfolio', '组合', 'allocation', '配置'],
            'questions': []
        },
        'company_analysis': {
            'name': '公司分析',
            'keywords': ['公司', 'company', 'business', '企业', '护城河', 'moat', '竞争优势', 'competitive'],
            'questions': []
        },
        'market_view': {
            'name': '市场观点',
            'keywords': ['市场', 'market', '股市', 'stock market', '经济', 'economy', '泡沫', 'bubble'],
            'questions': []
        },
        'risk_management': {
            'name': '风险管理',
            'keywords': ['风险', 'risk', '保险', 'insurance', '衍生品', 'derivative', '杠杆', 'leverage'],
            'questions': []
        },
        'value_concepts': {
            'name': '价值投资理念',
            'keywords': ['内在价值', 'intrinsic value', '价值投资', 'value investing', '安全边际', 'margin of safety',
                       '能力圈', 'circle of competence', '复利', 'compound'],
            'questions': []
        },
        'gambling_speculation': {
            'name': '赌博与投机',
            'keywords': ['赌博', 'gambling', '投机', 'speculation', '赌场', 'casino', '衍生品', 'derivative'],
            'questions': []
        },
        'life_wisdom': {
            'name': '人生智慧',
            'keywords': ['人生', 'life', '智慧', 'wisdom', '思维', 'thinking', '学习', 'learn'],
            'questions': []
        },
        'management': {
            'name': '企业管理',
            'keywords': ['管理', 'management', 'manager', 'ceo', '企业文化', 'culture', '经理人'],
            'questions': []
        },
        'mistakes': {
            'name': '错误与教训',
            'keywords': ['错误', 'mistake', '失败', 'fail', '教训', 'lesson'],
            'questions': []
        },
        'other': {
            'name': '其他',
            'keywords': [],
            'questions': []
        }
    }

    for q in questions:
        question_text = q['question'].lower()
        categorized = False

        for cat_key, cat_data in categories.items():
            if cat_key == 'other':
                continue

            for kw in cat_data['keywords']:
                if kw.lower() in question_text:
                    cat_data['questions'].append(q)
                    categorized = True
                    break

            if categorized:
                break

        if not categorized:
            categories['other']['questions'].append(q)

    # 打印统计
    print(f"\n问题分类统计:")
    for cat_key, cat_data in categories.items():
        count = len(cat_data['questions'])
        print(f"  {cat_data['name']:20s}: {count:4d}个")

    return categories


def build_conversation_guide_library(categories: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """构建对话引导库"""
    print(f"\n" + "=" * 70)
    print("构建对话引导库")
    print("=" * 70)

    guide_library = {
        'version': '1.0',
        'created': '2025-01-24',
        'categories': {},
        'conversation_starters': [],
        'deep_dive_questions': {}
    }

    # 为每个类别创建引导性问题
    for cat_key, cat_data in categories.items():
        if cat_key == 'other' or len(cat_data['questions']) == 0:
            continue

        # 选择最具代表性的问题（去重）
        unique_questions = list({q['question']: q for q in cat_data['questions']}.values())

        # 随机选择一些作为对话开场
        if len(unique_questions) >= 3:
            conversation_starters = unique_questions[:min(5, len(unique_questions))]
        else:
            conversation_starters = unique_questions

        # 选择深入探讨的问题（较长的问题）
        deep_dive = [q for q in unique_questions if len(q['question']) > 30][:10]

        guide_library['categories'][cat_key] = {
            'name': cat_data['name'],
            'total_questions': len(cat_data['questions']),
            'unique_questions': len(unique_questions),
            'conversation_starters': [q['question'] for q in conversation_starters],
            'deep_dive_questions': [q['question'] for q in deep_dive]
        }

        # 添加到总的对话开场
        for q in conversation_starters:
            guide_library['conversation_starters'].append({
                'category': cat_data['name'],
                'question': q['question'],
                'source': q.get('source', ''),
            })

        guide_library['deep_dive_questions'][cat_key] = [q['question'] for q in deep_dive]

    print(f"\n[OK] 对话引导库构建完成")
    print(f"  - 类别数: {len(guide_library['categories'])}")
    print(f"  - 对话开场: {len(guide_library['conversation_starters'])}个")

    return guide_library


def extract_case_studies() -> List[Dict[str, Any]]:
    """提取投资案例"""
    print(f"\n" + "=" * 70)
    print("提取投资案例")
    print("=" * 70)

    # 已知的著名投资案例
    known_cases = [
        {
            'name': '可口可乐 Coca-Cola',
            'year': '1988',
            'category': 'great_investment',
            'keywords': ['coca-cola', '可口可乐', 'ko'],
            'description': '1988年开始大量买入，成为最成功的投资之一'
        },
        {
            'name': '美国运通 American Express',
            'year': '1964',
            'category': 'turnaround',
            'keywords': ['american express', '美国运通', 'axp'],
            'description': '色拉油事件后的抄底投资'
        },
        {
            'name': '盖可保险 GEICO',
            'year': '1951',
            'category': 'great_investment',
            'keywords': ['geico', '盖可', '政府雇员保险公司'],
            'description': '巴菲特第一次投资，后来全资收购'
        },
        {
            'name': '华盛顿邮报 Washington Post',
            'year': '1973',
            'category': 'great_investment',
            'keywords': ['washington post', '华盛顿邮报', 'wpo'],
            'description': '在市场低迷时买入，获得巨大回报'
        },
        {
            'name': '比亚迪 BYD',
            'year': '2008',
            'category': 'value_investment',
            'keywords': ['byd', '比亚迪'],
            'description': '芒格主导的投资，获得巨大成功'
        },
        {
            'name': '富国银行 Wells Fargo',
            'year': '1989',
            'category': 'banking',
            'keywords': ['wells fargo', '富国银行', 'wfc'],
            'description': '在房地产危机后买入银行股'
        },
        {
            'name': 'IBM',
            'year': '2011',
            'category': 'mistake',
            'keywords': ['ibm'],
            'description': '承认是错误的投资'
        },
        {
            'name': '德克斯特鞋业 Dexter Shoe',
            'year': '1993',
            'category': 'mistake',
            'keywords': ['dexter', '德克斯特'],
            'description': '巴菲特称之为"最糟糕的投资之一"'
        },
        {
            'name': '全美航空 US Air',
            'year': '1989',
            'category': 'mistake',
            'keywords': ['us air', '全美航空', 'usair'],
            'description': '优先股投资差点亏光'
        },
        {
            'name': '能源公司 Energy Companies',
            'year': '2020',
            'category': 'value_investment',
            'keywords': ['energy', '能源', 'chevron', 'occidental'],
            'description': '2020年大量买入能源股'
        }
    ]

    # 从文档中搜索这些案例
    letters_dir = Path('data/letters/shareholder_letters')
    letter_files = list(letters_dir.glob('*.md'))[:20]  # 先分析前20封

    case_studies = []

    for case in known_cases:
        print(f"\n  搜索: {case['name']}...")

        for letter_file in letter_files:
            try:
                with open(letter_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 搜索关键词
                content_lower = content.lower()
                found = False
                for kw in case['keywords']:
                    if kw.lower() in content_lower:
                        found = True
                        break

                if found:
                    # 提取相关段落
                    paragraphs = content.split('\n\n')
                    relevant_paras = []

                    for para in paragraphs:
                        if len(para) < 50 or len(para) > 800:
                            continue

                        para_lower = para.lower()
                        for kw in case['keywords']:
                            if kw.lower() in para_lower:
                                relevant_paras.append(para[:500])
                                break

                        if len(relevant_paras) >= 3:
                            break

                    if relevant_paras:
                        year = letter_file.stem.split('_')[0]
                        match = re.search(r'(\d{4})', year)
                        if match:
                            case_studies.append({
                                'name': case['name'],
                                'category': case['category'],
                                'year': match.group(1),
                                'source': letter_file.name,
                                'keywords': case['keywords'],
                                'description': case['description'],
                                'segments': relevant_paras[:3]
                            })
                            print(f"    找到相关内容 in {match.group(1)}")
                            break

            except Exception as e:
                pass

    print(f"\n[OK] 提取 {len(case_studies)} 个投资案例")
    return case_studies


def main():
    """主函数"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "   问题库与案例库构建工具".center(54) + "   █")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    output_dir = Path('data/qa_database')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 从股东信中提取问题
    letter_questions = extract_questions_from_letters()

    # 2. 加载已提取的问题
    existing_questions = load_existing_questions()

    # 3. 合并所有问题
    all_questions = existing_questions + letter_questions
    print(f"\n[INFO] 总问题数: {len(all_questions)}")

    # 4. 分类
    categories = categorize_questions(all_questions)

    # 5. 构建对话引导库
    guide_library = build_conversation_guide_library(categories)

    # 保存对话引导库
    guide_file = output_dir / 'conversation_guide_library.json'
    with open(guide_file, 'w', encoding='utf-8') as f:
        json.dump(guide_library, f, ensure_ascii=False, indent=2)
    print(f"\n[SAVE] 对话引导库: {guide_file}")

    # 6. 提取投资案例
    case_studies = extract_case_studies()

    # 保存案例库
    cases_file = output_dir / 'investment_case_library.json'
    with open(cases_file, 'w', encoding='utf-8') as f:
        json.dump(case_studies, f, ensure_ascii=False, indent=2)
    print(f"[SAVE] 投资案例库: {cases_file}")

    # 总结
    print(f"\n" + "=" * 70)
    print("总结")
    print("=" * 70)

    print(f"\n问题库:")
    print(f"  - 总问题数: {len(all_questions)}")
    print(f"  - 股东信问题: {len(letter_questions)}")
    print(f"  - 已有问题: {len(existing_questions)}")
    print(f"  - 分类数: {len(guide_library['categories'])}")
    print(f"  - 对话开场: {len(guide_library['conversation_starters'])}个")

    print(f"\n案例库:")
    print(f"  - 投资案例: {len(case_studies)}个")

    # 按类别统计
    case_by_category = defaultdict(int)
    for case in case_studies:
        case_by_category[case['category']] += 1

    print(f"\n  案例分类:")
    for cat, count in case_by_category.items():
        print(f"    - {cat}: {count}个")

    print(f"\n" + "=" * 70)
    print("构建完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
