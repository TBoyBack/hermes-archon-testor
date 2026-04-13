# Hermes Agent + Archon 测试提效平台

> 智能化自动化测试解决方案 - 让 AI 成为测试团队的大脑和执行器

## 项目简介

本项目是一个结合 **Hermes Agent**（自我进化AI Agent）和 **Archon**（AI编程工作流引擎）的测试提效平台，旨在帮助测试团队从人工功能测试向智能化自动化测试转型。

### 核心理念

- **Hermes Agent 负责"理解层"**：业务规则学习、测试策略分析、风险识别、缺陷模式记忆
- **Archon 负责"执行层"**：测试流水线编排、代码生成、自动化执行、报告输出

## 架构设计

```
用户需求 → Hermes(理解层) → Archon(执行层) → 测试结果 → Hermes(学习进化)
```

## 项目结构

```
hermes-archon-testor/
├── docs/                    # 文档
│   ├── architecture/        # 架构设计
│   └── plans/              # 落地计划
├── src/                     # 源代码
│   ├── hermes/             # Hermes Agent 模块
│   ├── archon/             # Archon 引擎模块
│   ├── core/               # 核心组件
│   └── api/                # API 接口
├── tests/                   # 测试用例
├── examples/                # 示例代码
├── configs/                 # 配置文件
└── .archon/                 # Archon 工作流定义
    └── workflows/
```

## 快速开始

```bash
# 克隆项目
git clone https://github.com/TBoyBack/hermes-archon-testor.git
cd hermes-archon-testor

# 查看落地计划
cat docs/plans/ROADMAP.md
```

## 阶段规划

| 阶段 | 周期 | 目标 | 自动化率 |
|------|------|------|---------|
| MVP | 1-2周 | 验证价值，1条业务线 | 10% |
| 进阶 | 1个月 | 3条核心业务线 | 40% |
| 成熟 | 3个月 | 全业务线覆盖 | 80% |

## 预期收益

- 自动化覆盖率：0% → 80%
- 回归测试时间：减少 80%
- 人力释放：2-3人
- 团队能力：整体提升 80%

## 相关资源

- [Hermes Agent](https://github.com/calcaware/hermes) - 自我进化AI Agent
- [Archon](https://github.com/ajlabek/archon) - AI编程工作流引擎
- [完整设计方案](./docs/Hermes-Archon测试提效方案.md)

## License

MIT
