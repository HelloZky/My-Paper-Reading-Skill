# Paper Marp Skill — Marp 演示文稿生成

为论文生成一份 **简体中文** Marp Markdown 演示稿。

**Filename**: `[File Stem]-marp.md`  
**Folder**: 与其他笔记相同

## 主题与环境

- 默认使用 `theme: blue`
- 当前工作区通过 `.vscode/settings.json` 注册主题文件：`.vscode/marp_themes/blue.css`
- 如果主题文件不可用或未被 Marp 正确识别，可临时退回 `theme: default`
- 模板应尽量避免依赖外部图片资源；若没有现成图片，不要写会导致断链的本地图路径

## 要求

- 全部内容使用**简体中文**
- 每页使用 `---` 分隔
- **12–18 页**，覆盖背景、问题、方法、实验、总结，可使用 `section-divider` 分隔主要章节
- 以要点、表格、公式、图示说明为主，不要写成长段正文
- 优先放入论文中实际出现的实验数字；若某项未报告，可写 `论文未报告`
- 有图可用时再插图；没有图就用结构化要点代替

## Frontmatter

```yaml
---
marp: true
theme: blue
paginate: true
math: katex
---
```

## 可用页面类型

通过 `<!-- _class: xxx -->` 在页面**开头**（`---` 之后的第一行）设置。

| Class | 效果 | 适用场景 |
|-------|------|----------|
| `title` | 红色背景居中大标题 + 副标题 + 作者/日期/单位 | 封面 |
| `toc` | 列表自动编号，左侧蓝色边框 | 目录页 |
| `section-divider` | 深蓝渐变全屏背景，白色大标题，红色下划线 | 章节分隔 |
| `quote` | 大字体居中引用，底部自动显示作者 | 名言 / 核心观点 |
| `thanks` | 与首页风格一致的结尾页 | Q&A / 感谢页 |
| `small-text` | 正文 18pt | 内容较多的结果页 |
| `tinytext` | 正文 16pt | 参考文献、密集表格 |

## 可用布局组件

这些组件用 `<div class="xxx">` 在普通内容页中使用。

### 多栏布局

| Class | 用法 | 适用场景 |
|-------|------|----------|
| `columns-2` | 两列卡片（蓝/绿顶色条） | 两种方法、两个模块对比 |
| `columns-3` | 三列卡片（蓝/绿/橙） | 三个创新点或三阶段流程 |
| `columns-4` | 四列卡片（蓝/绿/橙/紫） | 四个模块、四组结果 |
| `columns-2-colors` | 两列彩色渐变背景 | 问题 vs 方案、Before/After |
| `columns-3-colors` | 三列彩色渐变背景 | 输入 / 处理 / 输出 |
| `columns-2x2` | 2×2 网格 | 消融四项对比 |

### 图文混排

| Class | 用法 | 适用场景 |
|-------|------|----------|
| `img-left` | 左图右文（图 45% / 文 55%） | 框架图 + 文字说明 |
| `img-right` | 左文右图（文 55% / 图 45%） | 结果分析 + 结果图 |

### 时间轴

| Class | 用法 | 适用场景 |
|-------|------|----------|
| `timeline` | 垂直时间轴，左侧连线 + 圆点 | 技术演进、项目里程碑 |
| `timeline-horizontal` | 水平时间轴 | 流程阶段、方法发展 |

### 数字展示

| Class | 用法 | 适用场景 |
|-------|------|----------|
| `big-number` | 大号数字 + 单位 + 标签 | 突出关键指标（准确率、加速比） |
| `big-number cards` | 带边框卡片的大数字 | 多组关键数字并排 |

### 强调框与标签

| Class | 用法 |
|-------|------|
| `highlight` | 黄色高亮框 |
| `info-box` | 蓝色信息框 |
| `warning-box` | 红色警告框 |
| `success-box` | 绿色成功框 |
| `tag tag-primary` | 蓝色标签 |
| `tag tag-accent` | 红色标签 |
| `tag tag-success` | 绿色标签 |

### 工具类

| Class | 用法 |
|-------|------|
| `text-center` / `text-right` | 文本对齐 |
| `text-sm` / `text-lg` / `text-xl` | 字体大小调整 |
| `mt-0` / `mt-2` / `mb-2` | 上下间距微调 |

## 分栏 HTML 语法

**重要**：`<div>` 标签后和 `</div>` 标签前必须有空行，否则 Markdown 内容不会被解析。

```html
<div class="columns-3">
<div>

### 标题一
- 内容...

</div>
<div>

### 标题二
- 内容...

</div>
<div>

### 标题三
- 内容...

</div>
</div>
```

## 图文混排语法

```html
<div class="img-left">
<div>

![](image.png)

</div>
<div>

### 说明标题

- 要点 1
- 要点 2

</div>
</div>
```

## 时间轴语法

```html
<div class="timeline">
<div>
<span class="year">2020</span>

### 里程碑标题

简短描述

</div>
<div>
<span class="year">2023</span>

### 里程碑标题

简短描述

</div>
</div>
```

## 大数字语法

```html
<div class="big-number">
<div>
<span class="number accent">96.2<span class="unit">%</span></span>
<div class="label">准确率</div>
</div>
<div>
<span class="number">3.5<span class="unit">x</span></span>
<div class="label">速度提升</div>
</div>
</div>
```

- `.accent` 使数字变为红色强调
- `.cards` 加在 `big-number` 上显示带边框卡片

## 字数限制参考

由于各布局列宽不同，注意内容量控制（基于 16:9 + 中文）：

| 布局 | h3 标题 | 正文每行 | 建议列表项 |
|------|---------|----------|------------|
| columns-2 | 8–10 字 | 18–20 字 | 4–6 项 |
| columns-3 | 6–8 字 | 12–14 字 | 3–4 项 |
| columns-4 | 4–6 字 | 8–10 字 | 2–3 项 |
| columns-2x2 | 8–10 字 | 16–18 字 | 3–4 项 |
| img-left/right 文字区 | 10–12 字 | 20–22 字 | 4–5 项 |
| timeline-horizontal | 4–6 字 | 8–10 字 | 2–3 项 |

**超限处理**：拆分为多页、换用更少列数的布局、使用 `small-text` 或 `tinytext`、简化表述。

## 推荐页序

根据 `paper-kind` 选择对应模板。封面页和结尾页通用，中间页不同。

### 常规论文页序

```markdown
---
marp: true
theme: blue
paginate: true
math: katex
---

<!-- _class: title -->

# [论文中文标题或中文概括标题]

## [Display Title]

[第一作者] · [年份]

[会议/期刊]

---

<!-- _class: toc -->

# 目录

- 研究背景与动机
- 核心贡献
- 方法详解
- 实验结果
- 结论与启发

---

<!-- _class: section-divider -->

# 研究背景

## Research Background

---

# 问题与挑战

<div class="columns-2-colors">
<div>

### 现有方法局限
- ...
- ...

</div>
<div>

### 本文目标
- ...
- ...

</div>
</div>

---

# 核心贡献

<div class="columns-3-colors">
<div>

### 创新点一
...

</div>
<div>

### 创新点二
...

</div>
<div>

### 创新点三
...

</div>
</div>

---

<!-- _class: section-divider -->

# 方法详解

## Methodology

---

# 方法框架

## 整体流程

- 输入是什么
- 关键模块有哪些
- 输出是什么

---

# 核心方法

## [模块名称]

<div class="columns-2">
<div>

### 设计原理
- ...

</div>
<div>

### 关键公式

$$
[LaTeX]
$$

</div>
</div>

---

<!-- _class: section-divider -->

# 实验结果

## Experiments

---

# 实验设置

| 项目 | 内容 |
|------|------|
| 数据集 | ... |
| 基线 | ... |
| 指标 | ... |
| 环境 | ... |

---

# 主实验结果

<!-- _class: small-text -->

| 方法 | 设置 1 | 设置 2 |
|------|--------|--------|
| Baseline 1 | xx | xx |
| 本文方法 | xx | xx |

> 用一句话解释最关键的结果。

---

# 关键指标

<div class="big-number">
<div>
<span class="number accent">[主指标值]<span class="unit">[单位]</span></span>
<div class="label">[指标名]</div>
</div>
<div>
<span class="number">[次指标值]<span class="unit">[单位]</span></span>
<div class="label">[指标名]</div>
</div>
</div>

---

# 消融与分析

<div class="columns-2x2">
<div>

### 完整模型
...

</div>
<div>

### 去除模块 A
...

</div>
<div>

### 去除模块 B
...

</div>
<div>

### 结论
...

</div>
</div>

---

# 总结

<div class="columns-2-colors">
<div>

### 贡献
- ...
- ...

</div>
<div>

### 局限与启发
- ...
- ...

</div>
</div>

---

<!-- _class: thanks -->

# Q & A

感谢聆听
```

### 综述论文页序

综述论文不套用"方法框架→消融"结构，改用以下页序：

```markdown
---
marp: true
theme: blue
paginate: true
math: katex
---

<!-- _class: title -->

# [综述中文标题或中文概括标题]

## [Display Title]

[第一作者] · [年份]

[会议/期刊]

---

<!-- _class: toc -->

# 目录

- 综述范围与动机
- 分类体系
- 各类方法对比
- 技术演进与趋势
- 开放问题与启发

---

<!-- _class: section-divider -->

# 综述范围

## Scope & Motivation

---

# 为什么需要这篇综述

<div class="columns-2-colors">
<div>

### 覆盖范围
- 聚焦领域：...
- 时间跨度：...
- 文献数量：...

</div>
<div>

### 与已有综述的区别
- 差异一：...
- 差异二：...

</div>
</div>

---

<!-- _class: section-divider -->

# 分类体系

## Taxonomy

---

# 顶层分类

<div class="columns-3-colors">
<div>

### 大类 A
- 核心特征：...
- 代表方法：...

</div>
<div>

### 大类 B
- 核心特征：...
- 代表方法：...

</div>
<div>

### 大类 C
- 核心特征：...
- 代表方法：...

</div>
</div>

---

<!-- _class: section-divider -->

# 方法对比与趋势

## Comparison & Trends

---

# 各类方法对比

<!-- _class: small-text -->

| 维度 | 大类 A | 大类 B | 大类 C |
|------|--------|--------|--------|
| 核心假设 | ... | ... | ... |
| [综述比较维度] | ... | ... | ... |

> 只填综述原文明确对比过的维度。

---

# 性能对比

<!-- _class: small-text -->

| 方法 | 类别 | 数据集 1 | 数据集 2 |
|------|------|----------|----------|
| Method 1 | 大类 A | xx | xx |
| Method 2 | 大类 B | xx | xx |

> 若综述未提供统一对比表，写 `综述未提供统一性能对比表`。

---

# 技术演进

<div class="timeline">
<div>
<span class="year">~YYYY</span>

### 早期阶段

描述...

</div>
<div>
<span class="year">~YYYY</span>

### 转折点

描述...

</div>
<div>
<span class="year">~YYYY–今</span>

### 当前主流

描述...

</div>
</div>

---

# 开放问题

<div class="columns-2-colors">
<div>

### 未解决的问题
- ...
- ...
- ...

</div>
<div>

### 未来方向
- ...
- ...
- ...

</div>
</div>

---

# 总结

<div class="columns-2-colors">
<div>

### 综述价值
- ...
- ...

</div>
<div>

### 局限与启发
- ...
- ...

</div>
</div>

---

<!-- _class: thanks -->

# Q & A

感谢聆听
```

## Rules

- 根据 `paper-kind` 选择常规或综述页序，不要混用
- `<!-- _class: xxx -->` 必须放在页面开头（`---` 之后的第一行），否则可能不被识别
- `<div>` 标签后和 `</div>` 标签前必须有空行，否则 Markdown 不渲染
- 标题页与结尾页可以使用 `title` / `thanks` 类，但不要依赖额外本地图像资源
- 若没有可插入的论文图，直接删除图片占位，不要保留伪路径
- 结果页中的数字必须来自论文原文
- 综述 Marp 中的对比表只保留综述原文明确比较过的维度
- 综述的"技术演进"优先使用 `timeline` 布局；若综述未给出时间线，可回退到列表
- 有 2–3 个关键数字值得突出时，使用 `big-number` 布局；不要为没有数字的场景硬造
- 每页内容控制在字数限制范围内；内容过多时拆页或降字号，不要挤在一页
