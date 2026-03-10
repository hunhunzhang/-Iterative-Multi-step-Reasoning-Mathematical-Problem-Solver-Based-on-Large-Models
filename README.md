# 基于大语言模型的迭代多步推理数学题求解器

<p align="center">
  <b>Iterative Multi-step Reasoning Mathematical Problem Solver Based on Large Language Models</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Model-DeepSeek--Chat-blue" />
  <img src="https://img.shields.io/badge/Language-Python-green" />
  <img src="https://img.shields.io/badge/Dataset-MATH-orange" />
  <img src="https://img.shields.io/badge/Method-Multi--Agent%20Iterative%20Reasoning-purple" />
</p>

---

## 📋 项目简介

本项目提出了一种**基于大语言模型（LLM）的多智能体迭代推理-摘要框架**，专门用于解决高难度数学问题。

传统的单次调用方式让 LLM 一步给出答案，在复杂数学题上常常力不从心。本项目的核心思路是：**将完整的推理过程拆分为多个独立的迭代步骤**，每一步由同一个 LLM 扮演不同角色（思考智能体 / 摘要智能体 / 答案智能体）完成单一操作，并通过**摘要（Summary）机制压缩上下文**，使得每一步的推理都能在有限的上下文窗口内高效进行。

> 详细介绍可参阅项目中的 `总结报告.pdf` 和 `实验记录.docx`。

---

## 🔍 研究背景与动机

- 大语言模型在复杂、多步骤数学推理任务中存在**上下文长度限制**与**单次推理深度不足**的问题。
- 现有 Chain-of-Thought（CoT）方法虽有改进，但在极难题目（如 MATH 数据集难度 5 级）上仍有较大提升空间。
- 本项目借鉴多智能体协作思想，通过**迭代思考 → 摘要压缩 → 继续推理**的循环，让模型在不超出上下文限制的前提下完成深度多步推理。

---

## 🏗️ 系统架构与研究思路

### 核心流程

```
用户问题
   │
   ▼
┌──────────────────────────────────────────────────────┐
│                   多智能体迭代推理循环                  │
│                                                      │
│  ① 初始思考（<think>）                                │
│     └─ 无历史上下文，针对原始问题进行初始推理           │
│                                                      │
│  ② 生成摘要（<summary>）                              │
│     └─ 压缩已有思考，提炼关键信息和当前推理状态         │
│                                                      │
│  ③ 继续推理（<think>）                                │
│     └─ 仅凭摘要+原问题继续推进，不保留完整历史          │
│                                                      │
│  重复 ②③ 直到推理完整                                 │
│                                                      │
│  ④ 最终答案（<answer>）                               │
│     └─ 确认推理完整后输出最简洁的最终答案               │
└──────────────────────────────────────────────────────┘
   │
   ▼
最终答案
```

### 关键设计原则

| 设计要点 | 说明 |
|---------|------|
| **单一操作规则** | 每次 LLM 调用只执行一个操作（思考/摘要/答案），避免混乱 |
| **摘要压缩机制** | 下一步只接收摘要+原问题，而非完整推理历史，控制上下文增长 |
| **结构化标签输出** | 使用 `<think>` / `<summary>` / `<answer>` 标签区分操作类型 |
| **最大迭代限制** | 设置最大迭代次数防止无限循环 |
| **AI 辅助评判** | 使用 LLM 辅助判断模型答案与标准答案的等价性 |

### 答案评估方法

由于数学答案可能有多种等价表达形式（如 `1/2 = 0.5 = 50%`），项目采用了 **AI 辅助等价性判断**：将模型答案和标准答案同时提交给 LLM，由其判断两者是否在数学上等价，输出 `[[YES]]` 或 `[[NO]]`。

---

## 🛠️ 技术栈

| 类别 | 技术/工具 |
|------|----------|
| **大语言模型** | DeepSeek-Chat（通过 API 调用） |
| **编程语言** | Python 3 |
| **HTTP 请求** | `requests` |
| **数据处理** | `json`, `regex` |
| **可视化分析** | `matplotlib`, `numpy` |
| **GUI 原型** | `tkinter` |
| **数据集** | MATH 竞赛数学数据集（按难度 1-5 分级） |
| **计算成本** | DeepSeek 定价：输入 $2/1M tokens，输出 $8/1M tokens |

---

## 📂 项目结构

```
.
├── math/                          # 核心实验代码目录
│   ├── process.py                 # 多智能体迭代推理主程序（基础版）
│   ├── process2.py                # 改进版（新增 FLOPs 统计）
│   ├── process3.py                # 完整版（AI 辅助答案评估）
│   ├── test1.py / test1 copy*.py  # 早期探索性脚本
│   ├── systemprompt.txt           # 多智能体系统提示词
│   ├── s_prompt.txt               # 单步求解系统提示词
│   ├── mainview.py                # GUI 原型界面
│   ├── find_max_problem.py        # 查找最大迭代问题工具
│   ├── data/                      # MATH 数据集（按难度分级）
│   │   ├── difficulty_1.json      # 难度1（90题）
│   │   ├── difficulty_2.json      # 难度2（102题）
│   │   ├── difficulty_3.json      # 难度3（138题）
│   │   ├── difficulty_4.json      # 难度4（137题）
│   │   └── difficulty_5.json      # 难度5（146题，主要评测集）
│   └── result/                    # 实验结果（JSON 格式）
├── completion_tokens_analysis.py  # Token 使用量分析脚本
├── getdata.py                     # 迭代步数直方图生成脚本
├── multi_metrics_*.json           # 多智能体实验结果
├── multi_metrics22_2.json         # 最大迭代=22 的实验结果
├── multi_metrics30_2.json         # 最大迭代=30 的实验结果
├── multi_metrics50_1.json         # 最大迭代=50 的实验结果
├── multi_metrics5_4.json          # token 限制=5 的实验结果
├── iteration_steps_histogram.png  # 迭代步数分布直方图
├── completion_tokens_histogram*.png # Token 使用量分布直方图
├── ittrue.png                     # 实验结果图
├── 实验记录.docx                   # 详细实验记录
├── 总结报告.pdf                    # 项目总结报告
└── poster (1).pptx                # 项目展示海报
```

---

## 📊 实验结果

### 评测数据集

所有实验主要在 **MATH 数据集难度 5 级**（146 道题，最高难度）上进行评测。

### 多智能体 vs 单智能体对比

| 方法 | 问题数 | 正确数 | 准确率 | 平均 Tokens/题 |
|------|--------|--------|--------|----------------|
| 单步直接回答（Single-step） | 146 | 112 | **76.71%** | 1,698 |
| 多智能体迭代推理（本方法） | 146 | 111 | 76.03% | 3,371 |
| 多智能体迭代推理（本方法，100题测试） | 100 | 84 | **84.00%** | 3,127 |

> 在 100 题子集上，多智能体迭代方法达到 **84%** 准确率，相比单步方法有显著提升。

### 不同最大迭代次数的影响（难度5级，146题）

| 最大迭代次数 | 正确数 | 准确率 | 平均迭代步数 | 平均 Tokens/题 |
|------------|--------|--------|------------|----------------|
| 5 步 | 76 | 52.05% | 3.72 | 2,595 |
| 22 步 | 90 | 61.64% | N/A | 4,751 |
| 30 步 | 95 | 65.07% | 7.53 | 5,012 |
| 50 步 | 89 | 60.96% | 8.75 | 5,984 |
| 不限（自然收敛） | 111 | **76.03%** | 3.77 | 3,371 |

> **结论**：过少（5步token限制）或过多（50步上限）的迭代次数都会降低性能；在自然收敛（平均约3-4步）时效果最佳。

### 迭代步数分布

下图展示了正确回答问题的迭代步数分布（仅统计正确答案）：

![迭代步数分布](iteration_steps_histogram.png)

### Completion Tokens 分布分析

通过对每次迭代中 `completion_tokens` 的分析，可以了解模型在思考（thinking）和摘要（summary）阶段的输出长度分布：

| 分析维度 | 直方图 |
|---------|--------|
| 全部类型（排除 answer） | ![所有类型](completion_tokens_histogram_all_excluding_answer.png) |
| 思考阶段（thinking） | ![思考阶段](completion_tokens_histogram_thinking.png) |
| 摘要阶段（summary） | ![摘要阶段](completion_tokens_histogram_summary.png) |

---

## 🚀 快速开始

### 环境要求

```bash
pip install requests regex matplotlib numpy
```

### 运行多智能体求解器

```python
# 以 process3.py 为例（完整版，含 AI 答案评估）
cd math
python process3.py
```

脚本会自动读取 `data/difficulty_5.json` 中的题目，逐题进行迭代推理，并将结果保存至 `result/multi_metrics_N.json`。

### 数据分析与可视化

```bash
# 分析迭代步数分布
python getdata.py

# 分析 Token 使用量
python completion_tokens_analysis.py
```

### 系统提示词格式

多智能体系统提示词定义了 LLM 在每次迭代中的行为规则：

```
流程：初始思考 → 生成摘要 → 继续推理 → 生成摘要 → ... → 最终答案

每次响应只能选择一个操作：
- <think>...</think>     : 初始思考或继续推理
- <summary>...</summary> : 压缩当前推理状态
- <answer>...</answer>   : 提供最终答案（仅在推理完整时使用）
```

---

## 📈 主要发现与结论

1. **多步迭代推理在高难度题目上有效**：在 MATH 难度5级 100题子集上，多智能体方法达到 84% 准确率。

2. **摘要机制是关键**：通过摘要压缩上下文，避免了上下文长度爆炸，使得模型可以进行更深层的多步推理。

3. **迭代次数存在最优区间**：过少的迭代限制（如 token 上限为 5）使得推理不充分（52%）；过多的迭代（最大 50 步）并不能持续提升性能（61%），反而增加计算成本。自然收敛（平均约 3-4 步）时效果最优（76-84%）。

4. **AI 辅助答案评估提升评测精度**：数学答案的多样化表达（分数/小数/等价式等）使得简单字符串匹配存在误差，使用 LLM 进行等价性判断更为准确。

5. **计算成本可控**：多智能体方法每题平均花费约 $0.013，与单步方法相近，但推理质量有明显提升。

---

## 📁 实验数据说明

| 文件名 | 说明 |
|--------|------|
| `multi_metrics_5.json` | 无限制tokens，100题，**准确率84%** |
| `multi_metrics_6.json` | 无限制tokens，146题，**准确率76.03%** |
| `multi_metrics30_2.json` | 最大30步迭代，146题，准确率65.07% |
| `multi_metrics50_1.json` | 最大50步迭代，146题，准确率60.96% |
| `multi_metrics22_2.json` | 最大22步迭代，146题，准确率61.64% |
| `multi_metrics5_4.json` | 最大5步迭代，146题，准确率52.05% |
| `math/single_metrics_4.json` | 单步基线，146题，**准确率76.71%** |

---

## 📄 参考资料

- [DeepSeek API 文档](https://platform.deepseek.com/)
- [MATH 数据集](https://arxiv.org/abs/2103.03874)（Hendrycks et al., 2021）
- Chain-of-Thought Prompting（Wei et al., 2022）

---

<p align="center">
  如需详细了解实验设计与分析，请参阅 <code>总结报告.pdf</code> 和 <code>实验记录.docx</code>
</p>
