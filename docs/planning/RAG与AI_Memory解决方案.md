# RAG分块策略与AI Memory解决方案

## RAG的标准分块做法

### 主流分块策略对比

| 策略 | 大小 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **固定大小** | 512-1024 tokens | 简单、高效 | 可能切断语义 | 通用场景 |
| **语义分块** | 变长 | 保持语义完整 | 计算复杂 | 需要高质量 |
| **段落分块** | 段落 | 自然边界 | 大小不一 | 结构化文档 |
| **句子分块** | 3-5句 | 精确语义 | 碎片化 | 精确匹配 |
| **递归分块** | 层级 | 多粒度 | 复杂 | 复杂文档 |

### 我们当前的做法

```python
# 固定大小分块（最常用）
chunk_size = 1000字符  # 约400-500 tokens
overlap = 200字符       # 20%重叠

# 为什么这么设置？
# 1. 1000字符 ≈ 1个完整段落/小节
# 2. 20%重叠避免切断重要内容
# 3. 这个大小在大多数LLM的上下文窗口内
```

### 行业标准实践

**OpenAI RAG实践**（ChatGPT企业版）：
```python
chunk_size = 800-1000 tokens
overlap = 10-20%
embedding_model = text-embedding-3-small
```

**LangChain默认配置**：
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
```

**LlamaIndex推荐**：
```python
from llama_index.node_parser import SimpleNodeParser

parser = SimpleNodeParser.from_defaults(
    chunk_size=1024,
    chunk_overlap=20
)
```

---

## 2️⃣ AI Memory的解决方案

### Memory类型全景图

```
AI Memory
├── 短期记忆
│   ├── 会话上下文
│   ├── 滑动窗口
│   └── Token限制内的记忆
│
├── 长期记忆
│   ├── 向量数据库 (RAG) ⭐ 我们在做的
│   ├── 关系数据库
│   └── 图数据库
│
├── 语义记忆
│   ├── 知识图谱
│   ├── 结构化数据
│   └── 规则库
│
└── 情景记忆
    ├── 时序记忆
    ├── 事件记忆
    └── 个性化记忆
```

---

## 3️⃣ 各种Memory方案详解

### 方案1: 滑动窗口（最简单）

**原理**：只保留最近N轮对话

```python
# 实现
memory = {
    'type': 'sliding_window',
    'window_size': 5,  # 只保留最近5轮
    'messages': [
        {'role': 'user', 'content': '问题1'},
        {'role': 'assistant', 'content': '回答1'},
        {'role': 'user', 'content': '问题2'},
        {'role': 'assistant', 'content': '回答2'},
        # ... 只保留最近5轮
    ]
}

# 优点
✅ 简单
✅ 快速
✅ 成本低

# 缺点
❌ 无法记住长期信息
❌ 没有知识库
❌ 不能跨会话
```

**适用场景**：简单客服、临时对话

---

### 方案2: 摘要式记忆（中等复杂度）

**原理**：定期总结对话历史

```python
memory = {
    'type': 'summary',
    'recent_messages': [...],  # 最近5轮
    'summary': '用户对价值投资感兴趣，特别是...',  # 历史摘要
    'key_topics': ['投资', '护城河', '可口可乐'],  # 关键主题
}

# 实现
def update_memory(messages):
    # 每10轮对话总结一次
    if len(messages) >= 10:
        summary = llm.summarize(messages[-10:])
        memory['summary'] += summary
        messages.clear()  # 清空旧消息

# 优点
✅ 可以记住长期信息
✅ 成本可控
✅ 实现简单

# 缺点
❌ 信息压缩有损失
❌ 无法检索细节
❌ 依赖LLM质量
```

**适用场景**：个人助手、长期对话机器人

---

### 方案3: 向量数据库（RAG）⭐ 我们在做的

**原理**：把知识向量化存储

```python
# 我们的实现
memory = {
    'type': 'vector_database',
    'chunks': 14,173,  # 文档片段数
    'embedding_model': 'all-MiniLM-L6-v2',
    'vector_db': 'ChromaDB',
    'retrieval': 'top_k=5',  # 每次检索5个相关片段
}

# 工作流程
user_query = "什么是价值投资？"
↓
# 1. 向量化
query_vector = embed(user_query)
↓
# 2. 检索
results = vector_db.search(query_vector, top_k=5)
# → 找到最相关的5个文档片段
↓
# 3. 生成回答
answer = llm.generate(
    prompt=query,
    context=results  # 用这5个片段作为上下文
)

# 优点
✅ 可以检索大量知识（14,173片段）
✅ 精准匹配语义
✅ 可以追溯到原文
✅ 支持跨会话

# 缺点
❌ 需要预计算（向量化所有文档）
❌ 检索质量依赖embedding模型
❌ 无法记住对话历史（除非额外存储）
```

**适用场景**：知识问答、文档助手、**我们的项目**！

---

### 方案4: 混合记忆（最强大）

**原理**：结合多种记忆方式

```python
memory = {
    # 短期：最近对话
    'short_term': SlidingWindowMemory(k=5),

    # 中期：对话摘要
    'mid_term': SummaryMemory(),

    # 长期：向量知识库
    'long_term': VectorDatabaseMemory(
        chunks=14173,
        retriever=semantic_search
    ),

    # 语义：知识图谱
    'semantic': KnowledgeGraph(
        entities=['巴菲特', '可口可乐', '价值投资'],
        relations=[('巴菲特', '投资', '可口可乐')]
    ),

    # 个性化：用户偏好
    'personal': UserPreferences(
        name='Steve',
        interests=['投资', '价值投资'],
        history={
            'asked_about': ['护城河', '可口可乐', '保险'],
            'preferred_style': '简洁、用比喻'
        }
    )
}
```

**ChatGPT Plus的方案**：
```python
# ChatGPT Plus的memory架构
1. 会话窗口：最近32K tokens（滑动窗口）
2. 向量库：用户上传的文档（RAG）
3. 知识图谱：实体和关系（GPT-4）
4. 长期记忆：用户偏好和历史（Memory feature）
```

---

## 4️⃣ 不同场景的最佳实践

### 场景1: 简单问答机器人

```
方案：滑动窗口 + RAG
├─ 滑动窗口：最近5轮对话
└─ RAG：固定知识库

优点：简单、便宜、够用
缺点：无法个性化
```

### 场景2: 个人AI助手

```
方案：混合记忆
├─ 短期：滑动窗口（10轮）
├─ 中期：摘要记忆
├─ 长期：向量知识库
└─ 个性化：用户偏好

优点：记住用户、持续学习
缺点：复杂、成本高
```

### 场景3: 企业知识库（像我们的）

```
方案：高级RAG
├─ 向量数据库：14,173个文档片段 ⭐
├─ 多路召回：语义+关键词+元数据
├─ 重排序：Rerank（精排结果）
├─ 引用：标注来源
└─ 缓存：常见问题

优点：精准、可追溯、专业
缺点：需要大量预处理
```

### 场景4: 超长期对话伴侣

```
方案：全量记忆
├─ 向量数据库：所有对话历史
├─ 知识图谱：实体和关系
├─ 时序记忆：按时间存储事件
├─ 情感记忆：情绪状态
└─ 个性化：深度用户画像

优点：像真人一样记住一切
缺点：极其复杂、昂贵
```

---

## 5️⃣ RAG的分块策略对比

### 我们当前的分块

```python
# 固定大小分块
chunk_size = 1000字符
overlap = 200字符

# 结果
├─ 14,173个片段
├─ 每个片段独立可检索
└─ 适合：通用问答
```

### 更高级的分块策略

#### 策略1: 语义分块（Semantic Chunking）

```python
from semantic_text_splitter import SemanticTextSplitter

# 按语义边界分块
splitter = SemanticTextSplitter(
    breakpoint_threshold_type='percentile',  # 相似度阈值
    breakpoint_threshold_amount=0.6  # 60%相似度
)

# 优点：保持语义完整
# 缺点：计算慢2-3倍

# 结果
├─ 每块大小不一（500-2000字符）
├─ 但每个块是完整的语义单元
└─ 适合：需要高质量的场景
```

#### 策略2: 父子文档索引（Parent Document Index）

```python
from langchain.retrievers import ParentDocumentRetriever

# 存储两种粒度
child_chunks = small_chunks(500字符)    # 子文档（精细）
parent_docs = large_chunks(2000字符)    # 父文档（完整）

# 检索时
1. 在子文档中检索（精准）
2. 返回父文档（完整上下文）

# 优点：既有精准度，又有完整上下文
# 缺点：存储空间×2
```

#### 策略3: 层级分块（Hierarchical Chunking）

```python
# 三级分块
level1 = chunk(text, size=4000)   # 章节级
level2 = chunk(level1, size=1000)  # 段落级
level3 = chunk(level2, size=500)   # 句子级

# 检索时根据需要选择粒度
if query很具体:
    return search(level3)  # 精细
elif query很宽泛:
    return search(level1)  # 宏观

# 优点：多粒度，灵活
# 缺点：实现复杂
```

---

## 6️⃣ 行业最佳实践对比

### 公司

**OpenAI ChatGPT**：
```
分块：固定大小（~800 tokens）
重叠：10-20%
向量模型：text-embedding-3-small
向量DB：内部系统（类似Pinecone）
Memory：滑动窗口（32K tokens）+ RAG
```

**Anthropic Claude**：
```
分块：自适应大小
向量模型：自己训练的
向量DB：内部系统
Memory：200K tokens上下文窗口
```

**Google Gemini**：
```
分块：语义分块
向量DB：基于搜索索引
Memory：1M tokens上下文窗口
```

**开源项目**：
```
LlamaIndex:
- 分块：固定大小（默认1024 tokens）
- 向量DB：支持20+种
- 重排序：可选Reranker

LangChain:
- 分块：多种策略
- 向量DB：支持30+种
- Memory：多类型记忆组件
```

---

## 7️⃣ 我们的项目处于什么水平？

### 当前实现（基础RAG）

```python
✅ 向量数据库
✅ 固定大小分块（1000字符）
✅ 基础语义检索
✅ 元数据过滤
✅ 来源追溯

📊 性能指标
- 文档数：14,173个片段
- 检索速度：~100ms
- 准确率：70-80%（估算）
```

### 可升级方向（高级RAG）

```python
🚧 多路召回
├─ 语义检索
├─ 关键词检索（BM25）
└─ 元数据过滤

🚧 重排序
├─ Cross-Encoder
└─ Reranker模型

🚧 混合记忆
├─ 对话历史记忆
├─ 用户偏好记忆
└─ 知识图谱

🚧 高级分块
├─ 父子文档索引
├─ 语义分块
└─ 层级分块
```

---

## 8️⃣ 推荐方案

### 对于我们的项目

**当前阶段（MVP）**：
```
✅ 固定大小分块（1000字符）✓ 够用
✅ 基础RAG检索 ✓ 成本低
✅ 元数据过滤 ✓ 灵活
✅ 问题库引导 ✓ 主动引导
```

**下一阶段（优化）**：
```
🚧 添加对话记忆
   - 记住用户问过什么
   - 记住用户感兴趣的话题

🚧 优化检索质量
   - 混合检索（语义+关键词）
   - 结果重排序

🚧 个性化推荐
   - 基于历史推荐相关问题
   - 基于偏好推荐案例
```

---

## 9️⃣ 总结

### RAG都是这么做的吗？

**是的，分块是标准做法！**

| 公司 | 分块大小 | 重叠 | 向量模型 |
|------|---------|------|---------|
| OpenAI | ~800 tokens | 10-20% | text-embedding-3 |
| 我们 | 1000字符 | 20% | all-MiniLM-L6-v2 |

**我们的方案是标准的！** ✅

### AI解决Memory的各种方案

1. **滑动窗口**（最简单）→ 短期记忆
2. **摘要记忆**（中等）→ 中期记忆
3. **向量数据库**（标准）→ **长期知识记忆** ⭐ 我们在做的
4. **混合方案**（最强大）→ 全能记忆

### 选择建议

| 场景 | 推荐方案 | 复杂度 |
|------|---------|--------|
| 简单问答 | 滑动窗口 + RAG | ⭐ |
| 个人助手 | 混合记忆 | ⭐⭐⭐ |
| **企业知识库** | **高级RAG** | **⭐⭐** ⭐ 我们 |
| 长期伴侣 | 全量记忆 | ⭐⭐⭐⭐⭐ |

---

## 结论

**我们的做法完全符合行业标准！**

14,173个RAG文档 = 把97个完整文件切碎后的结果，这是标准做法。

如果要升级，可以考虑：
1. 添加对话记忆（记住用户）
2. 混合检索（更精准）
3. 重排序（质量更高）

但当前方案已经够用了！✅
