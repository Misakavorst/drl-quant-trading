# Documentation Guide
# 文档指南

## 📂 文档结构

```
drl-quant-trading/
├── README.md                           # 项目主页（中英双语）
├── QUICKSTART.md                       # 快速开始指南
├── PROJECT_SUMMARY.md                  # 项目架构总结
│
├── docs/
│   ├── README.md                       # 本文档（文档导航）
│   ├── CHANGELOG.md                    # 版本更新日志
│   ├── ENVIRONMENT_REFACTOR_SUMMARY.md # 最新环境重构文档 ⭐
│   │
│   └── archive/                        # 历史文档归档
│       ├── A2C_ZERO_RETURN_FIX.md
│       ├── FIXES_APPLIED.md
│       ├── HYPERPARAMETER_OPTIMIZATION.md
│       ├── ITERATION_2_RESULTS.md
│       ├── LOSS_REWARD_FIX.md
│       ├── MULTI_STOCK_ENV_ANALYSIS.md
│       ├── MULTI_STOCK_TEST_RESULTS.md
│       ├── PARAMETER_OPTIMIZATION_SUMMARY.md
│       ├── PROGRESS_DISPLAY_FIX.md
│       └── TEST_REPORT.md
│
├── backend/
│   ├── README.md                       # 后端 API 文档
│   ├── SETUP.md                        # 后端配置指南
│   └── DATABASE_SCHEMA.md              # 数据库结构说明
│
└── frontend/
    └── README.md                       # 前端开发文档
```

---

## 📖 阅读指南

### 🚀 新用户入门

如果您是第一次使用本项目，建议按以下顺序阅读：

1. **[README.md](../README.md)** - 了解项目概况和核心功能
2. **[QUICKSTART.md](../QUICKSTART.md)** - 安装和运行项目
3. **[backend/SETUP.md](../backend/SETUP.md)** - 配置数据库连接
4. **[backend/DATABASE_SCHEMA.md](../backend/DATABASE_SCHEMA.md)** - 理解数据结构

### 🔧 开发人员

如果您想了解技术细节或参与开发：

1. **[PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md)** - 项目架构和技术选型
2. **[backend/README.md](../backend/README.md)** - 后端 API 详解
3. **[frontend/README.md](../frontend/README.md)** - 前端组件说明
4. **[ENVIRONMENT_REFACTOR_SUMMARY.md](ENVIRONMENT_REFACTOR_SUMMARY.md)** - 最新 RL 环境设计 ⭐

### 📊 研究人员

如果您关注 DRL 算法和性能优化：

1. **[ENVIRONMENT_REFACTOR_SUMMARY.md](ENVIRONMENT_REFACTOR_SUMMARY.md)** - 状态/动作空间设计
2. **[CHANGELOG.md](CHANGELOG.md)** - 性能改进历史
3. **[archive/HYPERPARAMETER_OPTIMIZATION.md](archive/HYPERPARAMETER_OPTIMIZATION.md)** - 超参数调优细节
4. **[archive/MULTI_STOCK_ENV_ANALYSIS.md](archive/MULTI_STOCK_ENV_ANALYSIS.md)** - 多股票环境分析

### 🐛 故障排查

如果遇到问题，可以参考：

1. **[CHANGELOG.md](CHANGELOG.md)** - 查看已知问题和修复
2. **[archive/FIXES_APPLIED.md](archive/FIXES_APPLIED.md)** - 历史 bug 修复记录
3. **[archive/](archive/)** - 查看具体问题的详细分析

---

## 🔑 核心文档说明

### 📘 主要文档

| 文档 | 说明 | 目标读者 |
|------|------|---------|
| [README.md](../README.md) | 项目主页，包含功能概览、技术栈、性能指标 | 所有用户 |
| [QUICKSTART.md](../QUICKSTART.md) | 安装和运行指南 | 新用户 |
| [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) | 项目架构、目录结构、技术选型 | 开发者 |
| [CHANGELOG.md](CHANGELOG.md) | 版本更新历史、bug 修复、性能改进 | 所有用户 |
| [ENVIRONMENT_REFACTOR_SUMMARY.md](ENVIRONMENT_REFACTOR_SUMMARY.md) | v2.0 最新环境重构详解 ⭐ | 研究者/开发者 |

### 📘 后端文档

| 文档 | 说明 |
|------|------|
| [backend/README.md](../backend/README.md) | API 端点、请求/响应格式、错误处理 |
| [backend/SETUP.md](../backend/SETUP.md) | 环境配置、数据库连接、SSH 隧道设置 |
| [backend/DATABASE_SCHEMA.md](../backend/DATABASE_SCHEMA.md) | 数据库表结构、字段说明、查询示例 |

### 📘 前端文档

| 文档 | 说明 |
|------|------|
| [frontend/README.md](../frontend/README.md) | 组件结构、路由配置、API 调用 |

---

## 🗂️ 归档文档说明

`archive/` 目录包含历史开发过程中的技术分析和问题修复文档，主要用于：
- 追溯特定问题的解决方案
- 了解项目演进历史
- 参考详细的技术分析

### 归档文档列表

| 文档 | 内容摘要 | 价值 |
|------|---------|------|
| **A2C_ZERO_RETURN_FIX.md** | A2C 零收益 bug 的根因和修复 | 理解评估逻辑 |
| **FIXES_APPLIED.md** | v1.0 期间的 bug 修复总结 | 问题排查参考 |
| **HYPERPARAMETER_OPTIMIZATION.md** | 详细的超参数调优过程和理论依据 | 算法调优指南 |
| **ITERATION_2_RESULTS.md** | 第二轮测试的性能数据 | 性能基准参考 |
| **LOSS_REWARD_FIX.md** | SAC/TD3 loss 显示问题修复 | 调试参考 |
| **MULTI_STOCK_ENV_ANALYSIS.md** | 多股票环境的深度分析 | 环境设计参考 |
| **MULTI_STOCK_TEST_RESULTS.md** | 多股票测试的详细结果 | 性能评估参考 |
| **PARAMETER_OPTIMIZATION_SUMMARY.md** | 参数优化总结 | 快速查阅 |
| **PROGRESS_DISPLAY_FIX.md** | 训练进度显示问题修复 | 前端调试参考 |
| **TEST_REPORT.md** | 全面的测试报告 | 测试基准 |

---

## 🆕 最新更新

### v2.0 (2025-11-09) - 重大改进 🎉

**必读文档**: [ENVIRONMENT_REFACTOR_SUMMARY.md](ENVIRONMENT_REFACTOR_SUMMARY.md)

**核心变化**:
- ✅ 状态空间优化（维度减少 55%，信息密度提升）
- ✅ 动作空间重构（softmax 归一化投资组合权重）
- ✅ DQN 动作空间优化（3^N 取代 5^N）
- ✅ A2C 零收益 bug 修复
- ✅ 全面超参数调优

**预期性能提升**:
- 训练稳定性：+50%
- 收益率：+30-50%
- 夏普比率：+40-60%

详见 [CHANGELOG.md](CHANGELOG.md)

---

## 📞 联系和贡献

- **GitHub**: [@Misakavorst](https://github.com/Misakavorst)
- **项目仓库**: [drl-quant-trading](https://github.com/Misakavorst/drl-quant-trading)

如有问题或建议，欢迎提交 Issue 或 Pull Request！

---

## 📝 文档维护

### 文档组织原则

1. **根目录**: 用户快速入门文档（README, QUICKSTART）
2. **docs/**: 核心技术文档和变更日志
3. **docs/archive/**: 历史分析和问题修复记录
4. **backend/**: 后端配置和 API 文档
5. **frontend/**: 前端开发文档

### 文档更新规范

- ✅ 重大功能更新：更新 CHANGELOG.md
- ✅ Bug 修复：在 CHANGELOG.md 记录
- ✅ 架构变更：更新 PROJECT_SUMMARY.md
- ✅ API 变更：更新 backend/README.md
- ✅ 过时文档：移至 archive/ 并在 CHANGELOG 中注明

---

**最后更新**: 2025-11-09  
**文档版本**: 2.0

