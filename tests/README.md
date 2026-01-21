# 测试文件说明

本目录包含Nothing to Add项目的测试脚本。

## 测试文件

### test_rag.py
基础RAG系统测试，测试3个问题：
1. 什么是价值投资？
2. 巴菲特的投资理念是什么？
3. 芒格说过关于分散投资的话吗？

### test_new_style.py ⭐
测试新的巴菲特芒格风格提示词。
问题：我现在处于就业迷茫状态，不知道该选择什么工作，你有什么建议？

### test_career_advice.py
职业建议专项测试。
问题：我现在处于就业迷茫状态...

### test_moat.py
护城河问题测试（英文）。
问题：What is an economic moat? How does Buffett view it?

### test_moat_cn.py
护城河问题测试（中文）。
问题：什么是护城河？巴菲特怎么看待企业护城河？

### test_polymarket.py ⭐
Polymarket预测市场问题测试（验证知识盲区处理）。
问题：怎么看待现在很火的Polymarket和预测市场？巴菲特和芒格会参与吗？
目的：测试AI如何处理训练数据之外的新兴平台（2020年后）

## 运行测试

### 运行所有测试
```bash
cd "C:\Users\steve\nothing to add project"
python tests/test_rag.py
python tests/test_new_style.py
python tests/test_career_advice.py
python tests/test_moat.py
python tests/test_moat_cn.py
```

### 单个测试
```bash
python tests/test_new_style.py
```

## 测试结果说明

所有测试都会：
1. 初始化RAG系统
2. 加载向量数据库
3. 检索相关文档（top 3-5）
4. 调用GLM API生成答案
5. 显示答案和来源

注意：控制台可能显示中文乱码（Windows编码问题），但功能正常。
