# 企业背调智能体 MVP

面向企业商务岗位的企业背调智能体，对企业进行公开信息背调，输出企业画像、需求信号、风险提示、联系人建议和沟通话术。

## 项目目标

帮助商务人员快速了解目标企业，回答以下核心问题：
1. 这家公司是谁？
2. 最近有没有值得关注的动态？
3. 它可能有没有需求？
4. 我应该优先找谁？
5. 我第一次该怎么开口？

## 功能范围

### 输入
- 企业名称（必填）
- 企业官网（可选）
- 我方产品/服务描述（可选）
- 跟进目标（可选）：首次触达、线索挖掘、会前准备、方案推进、客户经营
- 目标角色（可选）
- 补充背景（可选）

### 输出
- 企业概览：名称、行业、类型、规模、主营业务等
- 近期动态：新闻、招聘、扩张、融资等事件
- 需求信号：招聘信号、扩张信号、数字化信号等
- 推荐联系人：推荐角色、部门、优先级、理由
- 风险提示：法律风险、合规风险、财务风险等
- 商务判断：客户匹配度、商机等级、跟进优先级
- 沟通策略：推荐切入点、微信话术、电话话术、邮件话术
- 证据来源：所有结论的数据来源

## 技术栈

- Python 3.10+
- FastAPI
- Pydantic
- uv（环境管理）

## 环境管理

本项目使用 uv 管理 Python 虚拟环境，确保与本机其他 Python 环境隔离。

### 安装 uv

```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 创建虚拟环境

```bash
uv venv
```

### 安装依赖

```bash
uv pip install fastapi uvicorn pydantic
```

### 激活虚拟环境

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

## 运行项目

```bash
# 使用 uv 运行
uv run uvicorn backend.app.main:app --reload --port 8008

# 或激活虚拟环境后运行
uvicorn backend.app.main:app --reload --port 8008
```

## 访问地址

- 首页：http://127.0.0.1:8008/
- 健康检查：http://127.0.0.1:8008/health
- API 文档：http://127.0.0.1:8008/docs
- 分析接口：POST http://127.0.0.1:8008/analyze

## 项目结构

```
qitan/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py           # FastAPI 应用入口
│       ├── schemas/          # 数据模型定义
│       │   ├── __init__.py
│       │   ├── common.py     # 基础模型
│       │   ├── company.py    # 企业相关模型
│       │   ├── analysis.py   # 分析相关模型
│       │   ├── assessment.py # 商务判断模型
│       │   ├── output.py     # 输出模型
│       │   └── enums.py      # 枚举定义
│       ├── prompts/          # Prompt 模板
│       │   ├── __init__.py
│       │   ├── extraction.py # 信息抽取 Prompt
│       │   ├── analysis.py   # 商务分析 Prompt
│       │   └── communication.py # 话术生成 Prompt
│       ├── services/         # 业务逻辑
│       │   ├── __init__.py
│       │   └── mock_analyzer.py
│       └── config/           # 配置文件
│           ├── __init__.py
│           └── scoring.py    # 评分规则配置
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docs/
├── pyproject.toml
└── README.md
```

## API 接口说明

### GET /health

健康检查接口，用于验证服务是否正常运行。

**请求示例**：
```bash
curl http://127.0.0.1:8008/health
```

**响应示例**：
```json
{
  "status": "ok"
}
```

### POST /analyze

企业背调分析接口，接收企业信息，返回完整的背调报告。

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| company_name | string | 是 | 目标企业名称 |
| company_website | string | 否 | 目标企业官网 |
| user_company_product | string | 否 | 我方产品/服务描述，默认 "CRM系统" |
| user_target_customer_profile | string | 否 | 我方理想客户画像 |
| sales_goal | string | 否 | 跟进目标，枚举值见下方 |
| target_role | string | 否 | 用户希望接触的角色 |
| extra_context | string | 否 | 用户补充背景 |

**sales_goal 枚举值**：
- `lead_generation` - 线索挖掘
- `first_touch` - 首次触达
- `meeting_prep` - 会前准备
- `solution_pitch` - 方案推进
- `account_planning` - 客户经营
- `other` - 其他

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
    "version": "string",
    "generated_at": "datetime",
    "processing_time_seconds": "number"
  },
  "input": {
    "company_name": "string",
    "company_website": "string?",
    "user_company_product": "string",
    "sales_goal": "string"
  },
  "company_profile": {
    "name": "string",
    "industry": "string",
    "business_type": "string",
    "scale": "string",
    "main_business": "string",
    "established_date": "string?",
    "headquarters_location": "string?"
  },
  "recent_developments": [
    {
      "type": "string",
      "date": "string",
      "title": "string",
      "summary": "string",
      "source_url": "string?"
    }
  ],
  "demand_signals": [
    {
      "signal_type": "string",
      "strength": "high|medium|low",
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
        "priority": "high|medium|low",
        "reason": "string"
      }
    ],
    "organization_structure": "string?"
  },
  "risk_signals": [
    {
      "risk_type": "string",
      "severity": "high|medium|low",
      "description": "string",
      "impact": "string",
      "source_url": "string?"
    }
  ],
  "sales_assessment": {
    "customer_fit": {
      "level": "high|medium|low",
      "reason": "string"
    },
    "opportunity_level": "P1|P2|P3|discard",
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
      "source_url": "string?",
      "retrieved_at": "string"
    }
  ]
}
```

## 数据模型说明

本项目数据模型基于 `discuss003.md` 定义的 JSON Schema 实现，主要包括：

### 核心模型

- **DueDiligenceOutput**: 完整的背调输出模型
- **CompanyProfile**: 企业画像模型
- **RecentDevelopment**: 近期动态模型
- **DemandSignal**: 需求信号模型
- **RiskSignal**: 风险提示模型
- **SalesAssessment**: 商务判断模型
- **CommunicationStrategy**: 沟通策略模型

### 枚举定义

详见 `backend/app/schemas/enums.py`：
- `SalesGoalEnum`: 跟进目标枚举
- `RecentDevelopmentTypeEnum`: 近期动态类型枚举
- `DemandSignalTypeEnum`: 需求信号类型枚举
- `RiskTypeEnum`: 风险类型枚举
- `StrengthEnum`: 强度等级枚举

完整 Schema 定义请参考 `discuss003.md`。

## 评分规则说明

本项目采用多维度评分模型，总分 100 分，详见 `discuss004.md`。

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

评分规则详细定义见 `backend/app/config/scoring.py`。

## 开发状态

参见 `task.json` 获取当前开发进度。