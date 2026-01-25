# AI角色素材生成指南

**项目**: Nothing to Add - 巴菲特与芒格AI Agent
**日期**: 2026-01-25
**目标**: 使用免费AI工具生成一致性的动画角色素材

---

## 📋 目录

1. [工具推荐](#工具推荐)
2. [生成工作流程](#生成工作流程)
3. [具体操作步骤](#具体操作步骤)
4. [提示词模板](#提示词模板)
5. [一致性保证](#一致性保证)
6. [动画实现方案](#动画实现方案)
7. [质量检查清单](#质量检查清单)

---

## 1️⃣ 工具推荐

### 核心工具组合（免费方案）

| 工具 | 用途 | 免费额度 | 推荐指数 |
|------|------|---------|---------|
| **腾讯混元图片3.0** | 基础角色生成 | 每天66次 | ⭐⭐⭐⭐⭐ |
| **海螺AI (Conch AI)** | 表情变体+一致性 | 每天100次 | ⭐⭐⭐⭐⭐ |
| **即梦AI (iDream)** | 艺术风格优化 | 每天50次 | ⭐⭐⭐⭐ |
| **可灵AI (Kling)** | 视频生成(可选) | 每天10次 | ⭐⭐⭐ |

### 为什么选择这个组合？

```
混元3.0 (#1全球排名)
    ↓ 生成基础角色图
海螺AI (主体参考功能)
    ↓ 保持一致性生成表情变体
即梦AI (艺术优化)
    ↓ 提升细节质量
CSS/JS动画
    ↓ 实现说话、动作效果
```

---

## 2️⃣ 生成工作流程

### 总体流程图

```
Phase 1: 基础角色生成
├─ 巴菲特基础形象 (混元3.0)
└─ 芒格基础形象 (混元3.0)

Phase 2: 表情变体生成
├─ 使用海螺AI"主体参考"功能
├─ 保持基础形象不变
└─ 生成不同表情(开心、严肃、思考)

Phase 3: 动作帧生成
├─ 喝可乐动作 (5-10帧)
├─ 吃冰淇淋动作 (5-10帧)
└─ 说话嘴型 (10-20帧)

Phase 4: 艺术优化
└─ 即梦AI统一风格

Phase 5: 动画实现
├─ CSS关键帧动画
└─ JS控制切换
```

---

## 3️⃣ 具体操作步骤

### Step 1: 生成基础角色（混元3.0）

#### 巴菲特基础形象

**工具**: 腾讯混元图片生成
**网址**: https://hunyuan.tencent.com/

**提示词**:
```
一个卡通风格的沃伦·巴菲特头像，中年白人男性，
戴黑色边框眼镜，穿着简单的西装，打领带，
表情平和友善，风格简洁扁平，
白色背景，适合AI助手头像，
High quality, cartoon style, vector art
```

**参数设置**:
- 尺寸: 1024x1024
- 风格: 卡通扁平
- 数量: 4张，选最好的

**预期结果**: 一张干净的巴菲特基础头像

---

#### 查理·芒格基础形象

**提示词**:
```
一个卡通风格的查理·芒格头像，老年白人男性，
戴眼镜，稀疏的灰白发，穿着西装，
表情严肃但和蔼，风格简洁扁平，
白色背景，适合AI助手头像，
High quality, cartoon style, vector art
```

**保存**: 分别保存为 `buffett_base.png` 和 `munger_base.png`

---

### Step 2: 生成表情变体（海螺AI）

#### 使用"主体参考"功能保持一致性

**工具**: 海螺AI (Conch AI)
**网址**: https://www.conch.ai/

#### 操作流程

1. **上传基础图**:
   - 点击"主体参考"功能
   - 上传 `buffett_base.png` 作为参考图
   - 设置相似度: 85-90%（保持一致性）

2. **生成表情变体**:

**表情1: 开心/微笑**
```
同一个角色的微笑表情，嘴角上扬，
眼神温和，保持完全相同的面部特征和发型，
卡通扁平风格，白色背景
```

**表情2: 严肃/思考**
```
同一个角色的严肃表情，皱眉思考，
保持完全相同的面部特征和发型，
卡通扁平风格，白色背景
```

**表情3: 惊讶/疑问**
```
同一个角色的惊讶表情，眉毛上扬，
嘴巴微张，保持完全相同的面部特征，
卡通扁平风格，白色背景
```

3. **保存命名**:
   - `buffett_happy.png`
   - `buffett_serious.png`
   - `buffett_surprised.png`

4. **重复相同步骤** 为芒格生成表情变体

---

### Step 3: 生成动作帧（逐帧动画）

#### 3.1 喝可乐动作（5帧）

**工具**: 海螺AI + 主体参考

**帧1: 准备**
```
卡通巴菲特拿着一瓶可口可乐，
还未喝，准备动作，保持面部特征一致
```

**帧2: 举起**
```
卡通巴菲特举起可乐瓶到嘴边，
动作自然，保持面部特征一致
```

**帧3: 喝第一口**
```
卡通巴菲特正在喝可乐，瓶子倾斜，
头部微仰，保持面部特征一致
```

**帧4: 喝第二口**
```
卡通巴菲特继续喝可乐，享受的表情，
保持面部特征一致
```

**帧5: 放下**
```
卡通巴菲特放下可乐瓶，满足的表情，
保持面部特征一致
```

**保存**: `buffett_drink_coke_1.png` 到 `buffett_drink_coke_5.png`

---

#### 3.2 吃冰淇淋动作（5帧）

**帧1-5**: 同样的流程，提示词替换为:
```
卡通巴菲特拿着冰淇淋筒，
吃冰淇淋的不同阶段，
保持面部特征和服装一致
```

---

#### 3.3 说话嘴型动画（10-20帧）

**策略**: 生成关键嘴型 + 渐变插值

**关键帧**:

**帧1: 闭嘴**
```
卡通巴菲特闭着嘴的表情，
中性表情，说话开始前
```

**帧3: 微张**
```
卡通巴菲特嘴巴微张，
正在说话，发"啊"音
```

**帧5: 半张**
```
卡通巴菲特嘴巴半张，
说话中，发"哦"音
```

**帧7: 大张**
```
卡通巴菲特嘴巴张大，
说话强调时，发"哇"音
```

**帧9: 回到微张**
```
卡通巴菲特嘴巴微张，
说话即将结束
```

**帧10: 闭嘴**
```
卡通巴菲特闭着嘴的表情，
说话结束，回到中性
```

**技术提示**: 使用CSS animation的 `steps()` 或渐变插值

---

### Step 4: 艺术风格优化（可选）

**工具**: 即梦AI (iDream)

如果某些图片质量不够理想，可以用即梦AI重新生成:

```
卡通风 [复制原提示词]，专业插画师级别，
色彩和谐，线条干净，矢量风格
```

---

## 4️⃣ 提示词模板

### 通用提示词结构

```
[角色] + [动作/表情] + [风格要求] + [技术规格]
```

### 完整模板库

#### 基础角色模板

```
卡通风格的{角色名}，
{年龄}岁{性别}，{外貌特征}，
穿着{服装}，{表情}，
{风格}风格，{背景}，
High quality, {additional_tags}
```

**示例**:
```
卡通风格的沃伦·巴菲特，
70岁男性，白人，戴黑框眼镜，
穿灰色西装打红领带，友善微笑，
简洁扁平风格，白色背景，
High quality, vector art, clean lines
```

#### 表情变体模板（使用主体参考）

```
同一个角色的{表情描述}，
{具体面部变化}，
保持完全相同的{面部特征}、{发型}、{服装}，
{风格}风格，{背景}
```

#### 动作帧模板

```
卡通{角色名}{动作描述}，
{动作阶段}，动作自然流畅，
保持面部特征和服装一致，
{风格}风格，{背景}
```

---

## 5️⃣ 一致性保证

### 5.1 使用海螺AI"主体参考"功能

**步骤**:
1. 上传基础角色图作为"主体参考"
2. 设置相似度阈值: 85-90%
3. 在提示词中强调"保持完全相同"
4. 每次生成后检查一致性

### 5.2 一致性检查清单

生成每张新图片后，检查:

- [ ] 面部轮廓是否一致
- [ ] 眼镜/配饰位置是否相同
- [ ] 发型/发色是否一致
- [ ] 服装款式和颜色是否统一
- [ ] 整体风格是否匹配
- [ ] 光照方向是否一致

### 5.3 不一致时的补救方案

**方案1: 使用Photoshop/GIMP手动调整**
- 复制粘贴面部特征
- 调整颜色和光照
- 统一边缘和线条

**方案2: 重新生成**
- 降低相似度阈值到80%
- 在提示词中更详细描述特征
- 使用更精确的参考图

**方案3: 使用LoRA训练（高级）**
- 用基础图训练小型LoRA
- 用LoRA生成所有变体
- 工具: CivitAI或训练平台

---

## 6️⃣ 动画实现方案

### 6.1 CSS帧动画（最简单）

#### 示例: 说话动画

**HTML结构**:
```html
<div class="character-avatar">
  <img src="buffett_base.png" class="base">
  <div class="mouth-animation"></div>
</div>
```

**CSS动画**:
```css
@keyframes mouth-move {
  0%, 100% { background-position: 0 0; }   /* 闭嘴 */
  20% { background-position: -64px 0; }     /* 微张 */
  40% { background-position: -128px 0; }    /* 半张 */
  60% { background-position: -192px 0; }    /* 大张 */
  80% { background-position: -256px 0; }    /* 回到半张 */
}

.mouth-animation {
  width: 64px;
  height: 64px;
  background-image: url('mouth_spritesheet.png');
  background-size: 640px 64px;  /* 10帧横向排列 */
  animation: mouth-move 0.5s steps(10) infinite;
}

/* 说话时添加class */
.speaking .mouth-animation {
  animation-play-state: running;
}

/* 不说话时暂停 */
:not(.speaking) .mouth-animation {
  animation-play-state: paused;
}
```

#### 示例: 喝可乐动画

```css
@keyframes drink-coke {
  0% { opacity: 0; transform: translateY(10px); }
  20% { opacity: 1; transform: translateY(0); }
  80% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-10px); }
}

.drinking-coke {
  animation: drink-coke 2s ease-in-out forwards;
}
```

---

### 6.2 JavaScript动态切换

```javascript
// 表情管理器
class CharacterExpression {
  constructor(character) {
    this.character = character; // 'buffett' or 'munger'
    this.expressions = {
      neutral: `${character}_base.png`,
      happy: `${character}_happy.png`,
      serious: `${character}_serious.png`,
      surprised: `${character}_surprised.png`
    };
    this.currentExpression = 'neutral';
  }

  // 设置表情
  setExpression(emotion) {
    const img = document.getElementById(`${this.character}-avatar`);
    img.src = this.expressions[emotion];
    this.currentExpression = emotion;
  }

  // 播放动作动画
  playAction(action) {
    if (action === 'drink_coke') {
      this.playSpriteAnimation('drink_coke', 5, 1000);
    } else if (action === 'eat_icecream') {
      this.playSpriteAnimation('eat_icecream', 5, 1000);
    }
  }

  // 播放精灵图动画
  playSpriteAnimation(action, frameCount, duration) {
    const frames = [];
    for (let i = 1; i <= frameCount; i++) {
      frames.push(`${this.character}_${action}_${i}.png`);
    }

    let frameIndex = 0;
    const img = document.getElementById(`${this.character}-avatar`);
    const interval = duration / frameCount;

    const timer = setInterval(() => {
      img.src = frames[frameIndex];
      frameIndex++;

      if (frameIndex >= frames.length) {
        clearInterval(timer);
        img.src = this.expressions[this.currentExpression]; // 恢复原表情
      }
    }, interval);
  }
}

// 使用示例
const buffett = new CharacterExpression('buffett');

// 设置表情
buffett.setExpression('happy');

// 播放喝可乐动画
buffett.playAction('drink_coke');
```

---

### 6.3 说话时自动播放嘴型动画

```javascript
// 与AI对话结合
class AIDialogueManager {
  constructor() {
    this.buffett = new CharacterExpression('buffett');
    this.munger = new CharacterExpression('munger');
    this.speechSynthesis = window.speechSynthesis;
  }

  // AI说话时自动播放嘴型
  async speak(text, character) {
    const utterance = new SpeechSynthesisUtterance(text);
    const char = character === 'buffett' ? this.buffett : this.munger;

    // 开始说话
    utterance.onstart = () => {
      document.getElementById(`${character}-avatar`).classList.add('speaking');
      char.setExpression('happy'); // 说话时微笑
    };

    // 结束说话
    utterance.onend = () => {
      document.getElementById(`${character}-avatar`).classList.remove('speaking');
      char.setExpression('neutral'); // 恢复中性表情
    };

    this.speechSynthesis.speak(utterance);
  }
}
```

---

## 7️⃣ 质量检查清单

### 生成阶段检查

每生成一张图片，确认:

- [ ] **分辨率**: 至少1024x1024
- [ ] **格式**: PNG（支持透明背景）
- [ ] **风格**: 卡通扁平，线条干净
- [ ] **背景**: 白色或透明（便于后期处理）
- [ ] **命名**: 清晰的文件命名（如`buffett_happy.png`）

### 一致性检查

- [ ] **面部特征**: 五官位置和比例一致
- [ ] **服装**: 颜色、款式相同
- [ ] **配饰**: 眼镜、领带等位置一致
- [ ] **风格**: 线条粗细、色彩饱和度统一
- [ ] **光照**: 光源方向相同

### 动画检查

- [ ] **帧数**: 动作至少5帧，嘴型至少10帧
- [ ] **流畅度**: 动作过渡自然
- [ ] **时长**: 动作2秒，嘴型0.5-1秒
- [ ] **循环**: 嘴型动画可无缝循环

### 技术检查

- [ ] **文件大小**: 单个PNG < 500KB
- [ ] **优化**: 可用TinyPNG压缩
- [ ] **备份**: 保留原始高清文件
- [ ] **版本**: 使用Git LFS管理图片文件

---

## 8️⃣ 文件组织结构

```
public/
└── assets/
    └── characters/
        ├── buffett/
        │   ├── base/
        │   │   ├── buffett_base.png
        │   │   └── buffett_base.jpg
        │   ├── expressions/
        │   │   ├── buffett_neutral.png
        │   │   ├── buffett_happy.png
        │   │   ├── buffett_serious.png
        │   │   └── buffett_surprised.png
        │   ├── actions/
        │   │   ├── drink_coke/
        │   │   │   ├── buffett_drink_coke_1.png
        │   │   │   ├── buffett_drink_coke_2.png
        │   │   │   ├── ...
        │   │   │   └── buffett_drink_coke_5.png
        │   │   └── eat_icecream/
        │   │       ├── buffett_eat_icecream_1.png
        │   │       └── ...
        │   └── mouth/
        │       ├── buffett_mouth_1.png
        │       ├── buffett_mouth_2.png
        │       └── ...
        │
        └── munger/
            └── [同样的结构]
```

---

## 9️⃣ 成本估算

### 免费额度对比

| 工具 | 免费次数 | 可完成工作 |
|------|---------|-----------|
| 腾讯混元3.0 | 66次/天 | 基础角色×2 + 表情×6 = 8次（够用） |
| 海螺AI | 100次/天 | 动作帧50张（够用） |
| 即梦AI | 50次/天 | 艺术优化（备用） |
| **总计** | **216次/天** | **可完成所有需求** |

### 实际需求

```
基础角色: 2张
表情变体: 6张 (2角色×3表情)
动作帧: 20张 (2角色×2动作×5帧)
嘴型帧: 20张 (2角色×10帧)
---------------------------------------
总计: 48张图片

在免费额度内完全够用！✅
```

---

## 🔟 实施时间表

### Day 1: 基础角色生成
- [ ] 用混元3.0生成巴菲特基础图（1小时）
- [ ] 用混元3.0生成芒格基础图（1小时）
- [ ] 选择最佳版本，保存为base.png

### Day 2: 表情变体生成
- [ ] 用海螺AI生成巴菲特3种表情（2小时）
- [ ] 用海螺AI生成芒格3种表情（2小时）
- [ ] 一致性检查和调整（1小时）

### Day 3: 动作帧生成
- [ ] 生成喝可乐动作帧（2小时）
- [ ] 生成吃冰淇淋动作帧（2小时）

### Day 4: 嘴型动画
- [ ] 生成嘴型关键帧（2小时）
- [ ] 制作精灵图（sprite sheet）（1小时）

### Day 5: 动画实现
- [ ] CSS动画代码编写（2小时）
- [ ] JS控制逻辑（2小时）
- [ ] 测试和优化（2小时）

**总计**: 约5天可完成全部角色素材

---

## 📞 遇到问题时的资源

### 官方文档
- 腾讯混元: https://hunyuan.tencent.com/docs
- 海螺AI: https://www.conch.ai/docs
- 即梦AI: https://www.jimeng.ai/docs

### 社区资源
- Reddit: r/aiArt
- Discord: AI Art servers
- 国内: 知乎AI绘画话题

### 备用工具
- Stable Diffusion WebUI（本地部署）
- Midjourney（付费但质量高）
- DALL-E 3（ChatGPT Plus）

---

## 🎯 总结

### 推荐方案回顾

**最佳免费组合**:
```
混元3.0 (基础) + 海螺AI (一致性) + CSS动画
```

**核心优势**:
- ✅ 完全免费，额度充足
- ✅ 海螺AI的"主体参考"功能保证一致性
- ✅ 混元3.0质量全球第一
- ✅ 无需复杂设备，浏览器即可操作

**预期效果**:
- 高质量卡通角色
- 完美的表情一致性
- 流畅的动作动画
- 说话时的嘴型同步

---

**开始行动吧！** 🚀

建议从混元3.0开始先生成巴菲特的基础形象，然后用海螺AI生成表情变体。第一天就能看到成果！

有问题随时查阅本文档或询问AI助手。祝你生成顺利！
