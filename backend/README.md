# Backend - 企业背调智能体

v0.0.2 全链路后端服务，集成企查查 API 数据采集和 POE LLM 分析。

## 快速开始

### 环境要求

- Python 3.10+
- uv（Python 包管理器）

### 安装依赖

```bash
uv sync
```

### 配置环境变量

在项目根目录创建 `.env` 文件：

```env
QICHACHA_KEY=你的appKey
QICHACHA_SECRETKEY=你的secretKey
POE_API_KEY=你的poe_api_key
```

### 启动服务

```bash
uv run uvicorn backend.app.main:app --reload --port 8008
```

服务启动后访问 http://127.0.0.1:8008/docs 查看 API 文档。

## 架构概览

### Services 分层架构

```
backend/app/services/
├── orchestrator/          # 流程编排层
│   ├── analysis_orchestrator.py   # 主编排器（4 阶段全链路）
│   └── pipeline_state.py          # 统一状态容器
├── context/               # 上下文构建
│   └── context_builder.py
├── collection/            # 数据采集
│   └── qichacha_client.py         # 企查查 API（模糊搜索 + 核验 + 缓存）
├── llm/                   # LLM 适配层
│   ├── llm_client.py              # LLM 客户端（POE API）
│   └── llm_analysis.py            # LLM 分析（7 维度一次生成）
├── assembly/              # 结果组装
│   ├── output_assembler.py
│   └── output_validator.py
├── logging/               # 流水线日志
│   └── pipeline_logger.py         # 每请求独立日志文件
├── mock/                  # Mock 数据
│   └── mock_analyzer.py
├── resolution/            # 实体解析（骨架）
├── preprocessing/         # 证据预处理（骨架，当前跳过）
├── extraction/            # 事实抽取（骨架，LLM 统一处理）
├── analysis/              # 业务分析（骨架，LLM 统一处理）
├── scoring/               # 评分计算（待实现）
└── generation/            # 内容生成（待实现）
```

### 全链路流程

```
API Request
    │
    ▼
┌────────────────────────────────────────────────────┐
│            AnalysisOrchestrator                     │
│                                                     │
│  阶段1: Context Build                              │
│    └── context_builder.build() → AnalysisContext    │
│                                                     │
│  阶段2: Collection（企查查数据采集）                  │
│    └── qichacha_client.get_company_info()           │
│        ├── fuzzy_search()    → 模糊搜索匹配企业名    │
│        └── enterprise_info_verify() → 工商详情       │
│                                                     │
│  阶段3: LLM Analysis（大模型分析）                   │
│    └── run_llm_analysis() → 7 个分析维度             │
│        POE API / gpt-5.4，单次调用生成：              │
│        company_profile, recent_developments,         │
│        demand_signals, risk_signals,                 │
│        organization_insights, sales_assessment,      │
│        communication_strategy                        │
│                                                     │
│  阶段4: Assembly（输出组装）                         │
│    └── output_assembler.assemble()                  │
│        → DueDiligenceOutput                         │
└────────────────────────────────────────────────────┘
    │
    ▼
API Response
```

## 运行模式

系统支持三种运行模式，通过环境变量 `RUN_MODE` 配置（默认 `full_pipeline`）：

### 1. full_pipeline（默认）

全流程真实模式，企查查 API 采集 + LLM 分析。

```bash
export RUN_MODE=full_pipeline
```

### 2. hybrid

混合模式，真实链路失败时自动降级到 mock。

```bash
export RUN_MODE=hybrid
```

### 3. full_mock

全流程 Mock 模式，所有分析结果由 mock_analyzer 生成。适用于前端联调和演示。

```bash
export RUN_MODE=full_mock
```

## 流水线日志

每次 `/analyze` 请求自动在 `backend/logs/` 下生成独立日志文件：

- **命名规则**：`{调用时间}_{企业名}.log`，如 `20260316_103452_华为技术有限公司.log`
- **记录内容**：
  - 用户输入的完整参数
  - 各阶段每个函数的入参和返回结果
  - 每个函数的完成用时
  - 异常和错误信息

## 企查查 API 缓存

`qichacha_client` 自动缓存 API 返回结果到 `api_qichacha/test_result/`：

- `[企业模糊搜索]关键词.json` — 模糊搜索结果
- `[企业信息核验]企业名.json` — 企业核验结果

相同查询会直接读取缓存，避免重复消耗 API 次数。

## 模块实现状态

| 模块 | 状态 | 说明 |
|------|------|------|
| orchestrator | ✅ 已实现 | 主流程编排器，4 阶段全链路 |
| pipeline_state | ✅ 已实现 | 统一运行时状态容器 |
| context_builder | ✅ 已实现 | 分析上下文构建 |
| qichacha_client | ✅ 已实现 | 企查查 API 客户端（模糊搜索 + 核验 + 本地缓存） |
| llm_analysis | ✅ 已实现 | LLM 分析模块（POE/gpt-5.4，7 维度一次生成） |
| llm_client | ✅ 已实现 | LLM 客户端（POE API，含代理和 .env 支持） |
| output_assembler | ✅ 已实现 | 输出组装 |
| output_validator | ✅ 已实现 | 输出校验 |
| pipeline_logger | ✅ 已实现 | 流水线日志（每请求独立文件） |
| mock_analyzer | ✅ 已实现 | Mock 数据生成（降级兜底） |
| news_collector | ⏳ 跳过 | 新闻采集（后续版本实现） |
| preprocessing | ⏳ 跳过 | 证据预处理（LLM 直接处理） |
| scoring | ⏳ 待实现 | 评分计算 |

## API 接口

### POST /analyze

```http
POST /analyze
Content-Type: application/json

{
  "company_name": "某科技有限公司",
  "user_company_product": "CRM系统",
  "sales_goal": "first_touch"
}
```

### GET /health

```bash
curl http://127.0.0.1:8008/health
```

## 开发指南

### 添加新模块

1. 在对应目录下创建模块文件
2. 更新 `run_mode.py` 中的模块状态
3. 在 `orchestrator` 中集成调用逻辑

### 代码风格

- 使用 Python 3.10+ 类型注解
- 遵循 PEP 8 编码规范
- 使用 Pydantic v2 定义数据模型

## 相关文档

- [产品规划](../think_log/)
- [API 文档](http://127.0.0.1:8008/docs)（服务启动后访问）
