# Backend - 企业背调智能体

v0.0.2 Services 分层架构后端服务。

## 快速开始

### 环境要求

- Python 3.10+
- uv（Python 包管理器）

### 安装依赖

```bash
cd backend
uv sync
```

### 启动服务

```bash
uv run uvicorn app.main:app --reload
```

服务启动后访问 http://localhost:8000 查看 API 文档。

## 架构概览

### Services 分层架构

```
backend/app/services/
├── orchestrator/          # 流程编排层
│   ├── analysis_orchestrator.py   # 主编排器
│   └── pipeline_state.py          # 统一状态容器
├── context/               # 上下文构建
│   └── context_builder.py
├── resolution/            # 实体解析
│   └── entity_resolver.py
├── collection/            # 数据采集
│   ├── base.py                    # 采集器基类
│   ├── source_router.py           # 数据源路由
│   ├── website_collector.py       # 官网采集
│   └── news_collector.py          # 新闻采集
├── preprocessing/         # 证据预处理
│   ├── evidence_cleaner.py
│   ├── evidence_deduplicator.py
│   ├── evidence_normalizer.py
│   └── evidence_ranker.py
├── extraction/            # 事实抽取
│   ├── company_profile_extractor.py
│   └── development_extractor.py
├── analysis/              # 业务分析
│   ├── company_profile_analyzer.py
│   └── recent_development_analyzer.py
├── scoring/               # 评分计算（待实现）
├── generation/            # 内容生成（待实现）
├── assembly/              # 结果组装
│   ├── output_assembler.py
│   └── output_validator.py
├── llm/                   # LLM 适配层
│   ├── llm_client.py
│   ├── prompt_renderer.py
│   └── structured_generation.py
└── mock/                  # Mock 数据
    └── mock_analyzer.py
```

### 分析流程

```
API Request
    │
    ▼
┌─────────────────────────────────────────────────────┐
│              AnalysisOrchestrator                    │
│  ┌─────────────────────────────────────────────┐    │
│  │            PipelineState                     │    │
│  │     (统一运行时状态容器)                      │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  1. Context Build    →   AnalysisContext            │
│  2. Entity Resolution →   ResolvedCompany           │
│  3. Collection       →   RawEvidence[]              │
│  4. Preprocessing    →   ProcessedEvidence[]        │
│  5. Extraction       →   CandidateFact[]            │
│  6. Analysis         →   AnalysisResult[]           │
│  7. Scoring          →   ScoringResult              │
│  8. Generation       →   GeneratedContent           │
│  9. Assembly         →   DueDiligenceOutput         │
└─────────────────────────────────────────────────────┘
    │
    ▼
API Response
```

## 运行模式

系统支持三种运行模式，通过环境变量 `RUN_MODE` 配置：

### 1. full_mock（默认）

全流程 Mock 模式，所有分析结果由 mock_analyzer 生成。

**适用场景**：
- 前端联调
- 功能演示
- 测试验证

**配置**：
```bash
export RUN_MODE=full_mock
```

### 2. hybrid

混合模式，部分模块使用真实实现，未实现模块自动降级到 mock。

**适用场景**：
- 逐步接入真实数据源
- 功能验证

**配置**：
```bash
export RUN_MODE=hybrid
```

### 3. full_pipeline

全流程真实模式，所有模块使用真实实现。

**适用场景**：
- 生产环境
- 完整功能链路

**配置**：
```bash
export RUN_MODE=full_pipeline
```

> **注意**：full_pipeline 模式要求所有必需模块已实现，否则会自动降级。

## 模块实现状态

### 已实现

| 模块 | 状态 | 说明 |
|------|------|------|
| orchestrator | ✅ 已实现 | 主流程编排器 |
| pipeline_state | ✅ 已实现 | 统一状态容器 |
| context_builder | ✅ 已实现 | 分析上下文构建 |
| entity_resolver | ✅ 已实现 | 企业实体标准化 |
| mock_analyzer | ✅ 已实现 | Mock 数据生成 |
| output_assembler | ✅ 已实现 | 输出组装 |
| output_validator | ✅ 已实现 | 输出校验 |
| llm 骨架 | ✅ 已实现 | LLM 客户端接口 |

### 未实现

| 模块 | 状态 | 说明 |
|------|------|------|
| website_collector | ❌ 未实现 | 官网数据采集 |
| news_collector | ❌ 未实现 | 新闻数据采集 |
| preprocessing | ❌ 未实现 | 证据预处理链路 |
| extraction | ❌ 未实现 | 事实抽取 |
| analysis | ❌ 未实现 | 业务分析 |
| scoring | ❌ 未实现 | 评分计算 |
| generation | ❌ 未实现 | 内容生成 |

## 核心数据结构

### PipelineState

统一运行时状态容器，记录分析链路中的所有中间产物：

```python
class PipelineState(BaseModel):
    # 基础信息
    pipeline_id: str
    run_mode: RunMode
    current_stage: PipelineStage

    # 输入数据
    request: Dict[str, Any]
    context: Dict[str, Any]

    # 中间产物
    resolved_company: ResolvedCompany
    raw_evidence: List[RawEvidence]
    processed_evidence: List[ProcessedEvidence]
    candidate_facts: List[CandidateFact]
    analysis_results: Dict[str, AnalysisResult]

    # 输出
    final_output: Dict[str, Any]

    # 错误与警告
    errors: List[StageError]
    warnings: List[StageWarning]
```

### DueDiligenceOutput

最终输出结构：

```python
class DueDiligenceOutput(BaseModel):
    meta: Meta                      # 报告元数据
    input: Input                    # 输入参数
    company_profile: CompanyProfile # 企业画像
    recent_developments: List       # 近期动态
    demand_signals: List            # 需求信号
    organization_insights: ...      # 组织洞察
    risk_signals: List              # 风险信号
    sales_assessment: ...           # 商务判断
    communication_strategy: ...     # 沟通策略
    evidence_references: List       # 证据引用
```

## API 接口

### 分析接口

```http
POST /api/analyze
Content-Type: application/json

{
  "company_name": "示例科技有限公司",
  "company_website": "https://example.com",
  "user_company_product": "CRM系统",
  "sales_goal": "first_touch",
  "target_role": "销售负责人",
  "extra_context": "补充背景信息"
}
```

### 响应示例

```json
{
  "meta": {
    "report_id": "dd_20260313_abc123",
    "generated_at": "2026-03-13T10:30:00",
    "language": "zh-CN",
    "version": "mvp_v1"
  },
  "company_profile": {
    "company_name": "示例科技有限公司",
    "industry": ["企业服务", "软件"],
    "profile_summary": "..."
  },
  "recent_developments": [...],
  "demand_signals": [...],
  "sales_assessment": {...},
  "communication_strategy": {...}
}
```

## 开发指南

### 添加新模块

1. 在对应目录下创建模块文件
2. 更新 `run_mode.py` 中的模块状态
3. 在 `orchestrator` 中集成调用逻辑

### 运行测试

```bash
uv run pytest
```

### 代码风格

- 使用 Python 3.10+ 类型注解
- 遵循 PEP 8 编码规范
- 使用 Pydantic v2 定义数据模型

## 后续规划

### v0.0.3 目标

- 实现真实数据采集器（官网、新闻）
- 完成证据预处理链路
- 接入 LLM 进行事实抽取

### v0.0.4 目标

- 实现完整分析链路
- 添加评分计算模块
- 完善内容生成功能

## 相关文档

- [产品规划](../../think_log/)
- [任务清单](../../task.json)
- [API 文档](http://localhost:8000/docs)