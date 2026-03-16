# 企业背调智能体 MVP

面向企业商务岗位的企业背调智能体，对企业进行公开信息背调，输出企业画像、需求信号、风险提示、联系人建议和沟通话术。

**当前版本**：v0.0.2（全链路已打通）

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
- 企查查 API（企业工商数据）
- POE API / gpt-5.4（大模型分析）

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

### 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# 企查查 API 密钥
QICHACHA_KEY=你的appKey
QICHACHA_SECRETKEY=你的secretKey

# POE API 密钥
POE_API_KEY=你的poe_api_key
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

通过环境变量 `RUN_MODE` 控制运行模式（默认 `full_pipeline`）：

```bash
# 全流程真实模式（默认，企查查 + LLM 全链路）
export RUN_MODE=full_pipeline

# 混合模式（真实链路失败时自动降级到 mock）
export RUN_MODE=hybrid

# 全量 Mock 模式（用于前端联调和演示）
export RUN_MODE=full_mock
```

---

## 项目结构

```
qitan/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 应用入口
│   │   ├── schemas/                 # Pydantic 数据模型
│   │   ├── prompts/                 # Prompt 模板
│   │   ├── config/
│   │   │   ├── run_mode.py          # 运行模式配置
│   │   │   └── scoring.py           # 评分规则配置
│   │   └── services/                # 业务逻辑分层
│   │       ├── orchestrator/        # 流程编排层
│   │       ├── context/             # 上下文构建
│   │       ├── collection/          # 数据采集（企查查 API）
│   │       ├── llm/                 # LLM 适配层（POE API）
│   │       ├── assembly/            # 结果组装
│   │       ├── logging/             # 流水线日志
│   │       ├── mock/                # Mock 数据
│   │       └── ...                  # 其他服务模块骨架
│   ├── logs/                        # 分析日志（每次请求一个文件）
│   └── README.md                    # 后端架构说明
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── api_qichacha/                    # 企查查 API 文档与缓存数据
│   └── test_result/                 # API 返回结果缓存
├── think_log/                       # 产品设计与架构规划文档
├── pyproject.toml
└── README.md
```

---

## 全链路流程

```
用户输入企业名称
    │
    ▼
AnalysisOrchestrator（主编排器）
    │
    ├── 1. Context Build     → 构建分析上下文，标准化输入
    ├── 2. Collection        → 企查查模糊搜索 + 企业信息核验
    ├── 3. LLM Analysis      → POE/gpt-5.4 一次调用生成 7 个分析维度
    └── 4. Assembly          → 组装最终 DueDiligenceOutput
    │
    ▼
返回完整背调报告 JSON
```

### 数据采集

通过企查查 API 获取企业工商数据：
- **模糊搜索**（FuzzySearch/GetList）：根据关键词匹配准确企业名
- **企业信息核验**（EnterpriseInfo/Verify）：获取完整工商信息（经营范围、行业、注册资本、联系方式等）
- **本地缓存**：查询结果自动缓存到 `api_qichacha/test_result/`，避免重复调用

### LLM 分析

通过 POE API 调用 gpt-5.4，一次性生成全部 7 个分析维度：
- 企业画像（company_profile）
- 近期动态（recent_developments）
- 需求信号（demand_signals）
- 风险信号（risk_signals）
- 组织洞察（organization_insights）
- 商务判断（sales_assessment）
- 沟通策略（communication_strategy）

### 流水线日志

每次分析请求自动生成独立日志文件，存储于 `backend/logs/`：
- 文件命名：`{调用时间}_{企业名}.log`
- 记录内容：用户输入、各模块函数入参、返回结果、完成用时

---

## API 接口说明

### GET /health

健康检查接口。

```bash
curl http://127.0.0.1:8008/health
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
  "meta": { "report_id": "string", "generated_at": "datetime", "language": "zh-CN", "version": "string" },
  "input": { "company_name": "string", "user_company_product": "string", "sales_goal": "string" },
  "company_profile": { "company_name": "string", "industry": ["string"], "profile_summary": "string", "..." : "..." },
  "recent_developments": [{ "date": "string", "type": "string", "title": "string", "summary": "string" }],
  "demand_signals": [{ "signal_type": "string", "signal": "string", "evidence": "string", "inference": "string", "strength": "high|medium|low" }],
  "organization_insights": { "recommended_target_roles": [{ "role": "string", "department": "string", "priority": "number", "reason": "string" }] },
  "risk_signals": [{ "risk_type": "string", "risk": "string", "description": "string", "impact": "string", "level": "high|medium|low" }],
  "sales_assessment": { "customer_fit_level": "string", "opportunity_level": "string", "follow_up_priority": "P1|P2|P3|discard", "assessment_summary": "string" },
  "communication_strategy": { "opening_message": "string", "phone_script": "string", "wechat_message": "string", "email_message": "string" },
  "evidence_references": []
}
```

---

## 模块实现状态

| 模块 | 状态 | 说明 |
|------|------|------|
| orchestrator | ✅ 已实现 | 主流程编排器，4 阶段全链路 |
| pipeline_state | ✅ 已实现 | 统一运行时状态容器 |
| context_builder | ✅ 已实现 | 分析上下文构建 |
| qichacha_client | ✅ 已实现 | 企查查 API 客户端（模糊搜索 + 核验 + 缓存） |
| llm_analysis | ✅ 已实现 | LLM 分析模块（POE/gpt-5.4，7 维度一次生成） |
| llm_client | ✅ 已实现 | LLM 客户端（POE API，含代理支持） |
| output_assembler | ✅ 已实现 | 输出组装 |
| output_validator | ✅ 已实现 | 输出校验 |
| pipeline_logger | ✅ 已实现 | 流水线日志（每请求独立文件） |
| mock_analyzer | ✅ 已实现 | Mock 数据生成（降级兜底） |
| news_collector | ⏳ 跳过 | 新闻采集（后续版本实现） |
| preprocessing | ⏳ 跳过 | 证据预处理（LLM 直接处理） |
| scoring | ⏳ 待实现 | 评分计算 |

---

## 开发状态

| 版本 | 状态 | 说明 |
|------|------|------|
| v0.0.1 | ✅ 已完成 | MVP 骨架：数据模型、API、前端页面、Mock 数据 |
| v0.0.2 | ✅ 已完成 | Services 分层架构 + 全链路打通（企查查 + LLM） |
| v0.0.3 | 规划中 | 新闻数据采集、证据预处理、评分计算 |

详细任务清单：
- v0.0.1：`task001.json`（16 个任务，全部完成）
- v0.0.2：`task002.json`（20 个任务，全部完成）

---

## 参考文档

- **产品设计规划**：`think_log/v0.0.1/`、`think_log/v0.0.2/`
- **后端架构说明**：`backend/README.md`
- **API 交互文档**：http://127.0.0.1:8008/docs（服务启动后访问）
