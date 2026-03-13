# 企业背调智能体 MVP

面向企业商务岗位的企业背调智能体，对企业进行公开信息背调，输出企业画像、需求信号、风险提示、联系人建议和沟通话术。

**当前版本**：v0.0.2（Services 分层架构，已完成）

---

## 项目目标

帮助商务人员快速了解目标企业，回答以下核心问题：
1. 这家公司是谁？
2. 最近有没有值得关注的动态？
3. 它可能有没有需求？
4. 我应该优先找谁？
5. 我第一次该怎么开口？

---

## 功能范围

### 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| company_name | 是 | 目标企业名称 |
| company_website | 否 | 目标企业官网 |
| user_company_product | 否 | 我方产品/服务描述，默认 "CRM系统" |
| user_target_customer_profile | 否 | 我方理想客户画像 |
| sales_goal | 否 | 跟进目标，枚举值见下方 |
| target_role | 否 | 希望接触的角色 |
| extra_context | 否 | 补充背景 |

**sales_goal 枚举值**：
- `lead_generation` - 线索挖掘
- `first_touch` - 首次触达
- `meeting_prep` - 会前准备
- `solution_pitch` - 方案推进
- `account_planning` - 客户经营
- `other` - 其他

### 输出

- **企业概览**：名称、行业、类型、规模、主营业务等
- **近期动态**：新闻、招聘、扩张、融资等事件
- **需求信号**：招聘信号、扩张信号、数字化信号等
- **组织洞察**：推荐联系角色、部门、优先级、理由
- **风险提示**：法律风险、合规风险、财务风险等
- **商务判断**：客户匹配度、商机等级、跟进优先级
- **沟通策略**：推荐切入点、微信话术、电话话术、邮件话术
- **证据来源**：所有结论的数据来源

---

## 技术栈

- Python 3.10+
- FastAPI
- Pydantic v2
- uv（环境管理）

---

## 快速开始

### 安装 uv

```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 安装依赖

```bash
uv sync
```

### 启动服务

```bash
uv run uvicorn backend.app.main:app --reload --port 8008
```

### 访问地址

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:8008/ | 前端页面 |
| http://127.0.0.1:8008/health | 健康检查 |
| http://127.0.0.1:8008/docs | API 文档（Swagger） |
| http://127.0.0.1:8008/analyze | POST 分析接口 |

### 运行模式配置

通过环境变量 `RUN_MODE` 控制运行模式（默认 `full_mock`）：

```bash
# 全量 Mock 模式（默认，用于前端联调和演示）
export RUN_MODE=full_mock

# 混合模式（部分真实实现，未实现模块自动降级到 mock）
export RUN_MODE=hybrid

# 全流程真实模式（生产环境，要求所有模块已实现）
export RUN_MODE=full_pipeline
```

---

## 项目结构

```
qitan/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 应用入口
│   │   ├── schemas/                 # Pydantic 数据模型
│   │   │   ├── common.py            # 通用基础模型
│   │   │   ├── company.py           # 企业相关模型
│   │   │   ├── analysis.py          # 分析过程模型
│   │   │   ├── assessment.py        # 判断与评估模型
│   │   │   ├── output.py            # 最终输出模型
│   │   │   └── enums.py             # 枚举定义
│   │   ├── prompts/                 # Prompt 模板
│   │   │   ├── extraction.py        # 信息抽取类 Prompt
│   │   │   ├── analysis.py          # 商务分析类 Prompt
│   │   │   └── communication.py     # 话术生成类 Prompt
│   │   ├── config/
│   │   │   ├── run_mode.py          # 运行模式配置
│   │   │   └── scoring.py           # 评分规则配置
│   │   └── services/                # 业务逻辑分层
│   │       ├── orchestrator/        # 流程编排层
│   │       ├── context/             # 上下文构建
│   │       ├── resolution/          # 实体解析
│   │       ├── collection/          # 数据采集
│   │       ├── preprocessing/       # 证据预处理
│   │       ├── extraction/          # 信息抽取
│   │       ├── analysis/            # 业务分析
│   │       ├── scoring/             # 评分计算
│   │       ├── generation/          # 内容生成
│   │       ├── assembly/            # 结果组装
│   │       ├── llm/                 # LLM 适配层
│   │       └── mock/                # Mock 数据
│   └── README.md                    # 后端架构说明
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── think_log/                       # 产品设计与架构规划文档
│   ├── v0.0.1/                      # MVP 版本规划（4 个文档）
│   └── v0.0.2/                      # 服务架构重构规划（3 个文档）
├── docs/
├── task001.json                     # v0.0.1 任务清单（已完成）
├── task002.json                     # v0.0.2 任务清单（已完成）
├── pyproject.toml
└── README.md
```

---

## API 接口说明

### GET /health

健康检查接口。

```bash
curl http://127.0.0.1:8008/health
```

```json
{ "status": "ok" }
```

### POST /analyze

企业背调分析接口，接收企业信息，返回完整背调报告。

**请求示例**：

```bash
curl -X POST http://127.0.0.1:8008/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "某科技有限公司",
    "user_company_product": "CRM系统",
    "sales_goal": "first_touch"
  }'
```

**响应结构**：

```json
{
  "meta": {
    "report_id": "string",
    "generated_at": "datetime",
    "language": "zh-CN",
    "version": "string"
  },
  "input": {
    "company_name": "string",
    "company_website": "string | null",
    "user_company_product": "string",
    "sales_goal": "string"
  },
  "company_profile": {
    "company_name": "string",
    "industry": ["string"],
    "profile_summary": "string"
  },
  "recent_developments": [
    {
      "event_type": "string",
      "event_date": "string",
      "title": "string",
      "summary": "string",
      "source_url": "string | null"
    }
  ],
  "demand_signals": [
    {
      "signal_type": "string",
      "strength": "high | medium | low",
      "description": "string",
      "evidence": "string",
      "inference": "string"
    }
  ],
  "organization_insights": {
    "recommended_target_roles": [
      {
        "role": "string",
        "department": "string",
        "priority": "high | medium | low",
        "reason": "string"
      }
    ],
    "organization_structure": "string | null"
  },
  "risk_signals": [
    {
      "risk_type": "string",
      "severity": "high | medium | low",
      "description": "string",
      "impact": "string",
      "source_url": "string | null"
    }
  ],
  "sales_assessment": {
    "customer_fit": {
      "level": "high | medium | low",
      "reason": "string"
    },
    "opportunity_level": "P1 | P2 | P3 | discard",
    "priority_score": "number (0-100)",
    "priority_reason": "string",
    "suggested_next_steps": ["string"]
  },
  "communication_strategy": {
    "entry_point": {
      "angle": "string",
      "reason": "string"
    },
    "wechat_script": "string",
    "phone_script": "string",
    "email_script": "string"
  },
  "evidence_references": [
    {
      "claim": "string",
      "source_name": "string",
      "source_url": "string | null",
      "retrieved_at": "string"
    }
  ]
}
```

---

## 架构说明

v0.0.2 引入 Services 分层架构，将背调流程拆分为 12 个职责独立的层：

```
API Request
    |
    v
AnalysisOrchestrator（主编排器）
    |
    +--> 1. Context Build      → AnalysisContext
    +--> 2. Entity Resolution  → ResolvedCompany
    +--> 3. Collection         → RawEvidence[]
    +--> 4. Preprocessing      → ProcessedEvidence[]
    +--> 5. Extraction         → CandidateFact[]
    +--> 6. Analysis           → AnalysisResult[]
    +--> 7. Scoring            → ScoringResult
    +--> 8. Generation         → GeneratedContent
    +--> 9. Assembly           → DueDiligenceOutput
    |
    v
API Response
```

所有中间状态通过 `PipelineState` 统一容器传递，支持错误记录、阶段追踪和降级处理。

### 模块实现状态（v0.0.2）

| 模块 | 状态 | 说明 |
|------|------|------|
| orchestrator | 已实现 | 主流程编排器 |
| pipeline_state | 已实现 | 统一运行时状态容器 |
| context_builder | 已实现 | 分析上下文构建 |
| entity_resolver | 已实现 | 企业实体标准化 |
| mock_analyzer | 已实现 | Mock 数据生成（降级兜底） |
| output_assembler | 已实现 | 结果组装 |
| output_validator | 已实现 | 输出校验 |
| llm 骨架 | 已实现 | LLM 客户端接口定义 |
| website_collector | 待实现 | 官网数据采集 |
| news_collector | 待实现 | 新闻数据采集 |
| preprocessing | 待实现 | 证据预处理链路 |
| extraction | 待实现 | 事实抽取（LLM 驱动） |
| analysis | 待实现 | 业务分析 |
| scoring | 待实现 | 评分计算 |
| generation | 待实现 | 话术内容生成 |

---

## 数据模型说明

数据模型基于 `think_log/v0.0.1/discuss001_003.md` 定义的 JSON Schema 实现，使用 Pydantic v2。

### 核心模型

- **DueDiligenceOutput**：完整背调输出模型
- **CompanyProfile**：企业画像模型
- **RecentDevelopment**：近期动态模型
- **DemandSignal**：需求信号模型
- **RiskSignal**：风险提示模型
- **SalesAssessment**：商务判断模型
- **CommunicationStrategy**：沟通策略模型

### 枚举定义（`backend/app/schemas/enums.py`）

- `SalesGoalEnum`：跟进目标枚举
- `RecentDevelopmentTypeEnum`：近期动态类型枚举
- `DemandSignalTypeEnum`：需求信号类型枚举
- `RiskTypeEnum`：风险类型枚举
- `StrengthEnum`：强度等级枚举

---

## 评分规则说明

采用多维度评分模型，总分 100 分，详见 `think_log/v0.0.1/discuss001_004.md` 和 `backend/app/config/scoring.py`。

### 评分维度

| 维度 | 满分 | 说明 |
|------|------|------|
| ICP 匹配度 | 35分 | 行业匹配(0-12)、企业规模(0-8)、业务场景(0-10)、企业类型(0-5) |
| 需求信号 | 35分 | 动态新鲜度(0-10)、信号强度(0-15)、多信号一致性(0-10) |
| 可触达可行性 | 15分 | 目标角色清晰度(0-5)、切入场景清晰度(0-5)、组织路径可推断性(0-5) |
| 风险扣分 | 15分 | 按风险等级和类型扣分 |

### 优先级映射

| 总分 | 优先级 | 说明 |
|------|--------|------|
| 75-100 | P1 | 高优先级，建议立即跟进 |
| 55-74 | P2 | 中优先级，建议近期跟进 |
| 35-54 | P3 | 低优先级，可纳入长期观察 |
| 0-34 | discard | 不建议跟进 |

---

## 开发状态

| 版本 | 状态 | 说明 |
|------|------|------|
| v0.0.1 | 已完成 | MVP 骨架：数据模型、API、前端页面、Mock 数据 |
| v0.0.2 | 已完成 | Services 分层架构、PipelineState、运行模式支持 |
| v0.0.3 | 规划中 | 真实数据采集（官网、新闻）、证据预处理、LLM 抽取 |
| v0.0.4 | 规划中 | 完整分析链路、评分计算、内容生成 |

详细任务清单：
- v0.0.1：`task001.json`（16 个任务，全部完成）
- v0.0.2：`task002.json`（20 个任务，全部完成）

---

## 参考文档

- **产品设计规划**：`think_log/v0.0.1/`、`think_log/v0.0.2/`
- **后端架构说明**：`backend/README.md`
- **API 交互文档**：http://127.0.0.1:8008/docs（服务启动后访问）
