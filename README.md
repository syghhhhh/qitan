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
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docs/
├── pyproject.toml
└── README.md

backend/app/
├── __init__.py
├── main.py                                  # FastAPI 应用入口，负责创建应用实例、注册路由与初始化配置
├── schemas/                                 # Pydantic 数据模型定义，统一接口输入输出与内部结构化对象
│   ├── __init__.py
│   ├── common.py                            # 通用基础模型，如分页、时间戳、证据基类、通用响应字段等
│   ├── company.py                           # 企业相关模型，如企业基础信息、域名、别名、行业、组织信息等
│   ├── analysis.py                          # 分析过程相关模型，如候选事实、分析结果、中间状态对象等
│   ├── assessment.py                        # 判断与评估相关模型，如销售价值判断、风险判断、优先级评估等
│   ├── output.py                            # 最终输出模型，定义 API 返回结果结构
│   └── enums.py                             # 枚举定义，如数据源类型、事件类型、评分等级、任务状态等
├── prompts/                                 # Prompt 模板目录，集中管理不同业务阶段使用的大模型提示词
│   ├── __init__.py
│   ├── extraction.py                        # 信息抽取类 Prompt，如企业画像、事件、信号、组织信息抽取
│   ├── analysis.py                          # 商务分析类 Prompt，如需求判断、风险分析、销售机会分析
│   └── communication.py                     # 话术与沟通生成类 Prompt，如触达策略、销售话术、下一步建议
├── services/                                # 业务逻辑主目录，按职责拆分为编排、采集、抽取、分析、生成等模块
│   ├── __init__.py
│   ├── orchestrator/                        # 流程编排层，负责串联各服务模块形成完整分析链路
│   │   ├── __init__.py
│   │   ├── analysis_orchestrator.py         # 分析主编排器，统一驱动 context、采集、抽取、分析、组装等流程
│   │   └── pipeline_state.py                # 流水线状态容器，记录请求上下文、中间结果、错误与最终输出
│   ├── context/                             # 上下文构建层，负责将原始请求转换为统一分析上下文
│   │   ├── __init__.py
│   │   └── context_builder.py               # 分析上下文构建器，归一化企业信息、销售目标、用户输入等
│   ├── resolution/                          # 实体解析层，负责标准化企业实体与基础识别
│   │   ├── __init__.py
│   │   └── entity_resolver.py               # 企业实体解析器，根据公司名/官网解析标准企业名称、域名、别名等
│   ├── collection/                          # 数据采集层，负责从不同数据源抓取原始证据
│   │   ├── __init__.py
│   │   ├── base.py                          # 采集器基础接口与通用抽象，定义 collector 输入输出协议
│   │   ├── source_router.py                 # 数据源路由器，根据上下文和配置决定启用哪些采集器
│   │   ├── website_collector.py             # 官网采集器，抓取企业官网内容与基础公开信息
│   │   ├── news_collector.py                # 新闻采集器，抓取企业相关新闻、公告、媒体报道等
│   │   ├── jobs_collector.py                # 招聘采集器，抓取招聘岗位信息以识别扩张、技术方向和组织需求
│   │   ├── company_registry_collector.py    # 工商/注册信息采集器，采集企业登记、法人、资本、成立时间等信息
│   │   └── risk_collector.py                # 风险信息采集器，采集法律纠纷、经营异常、处罚、舆情等风险证据
│   ├── preprocessing/                       # 证据预处理层，对原始采集结果进行清洗、去重、标准化和排序
│   │   ├── __init__.py
│   │   ├── evidence_cleaner.py              # 证据清洗器，移除噪声内容、无效文本和明显脏数据
│   │   ├── evidence_deduplicator.py         # 证据去重器，合并重复新闻、重复页面和相似证据
│   │   ├── evidence_normalizer.py           # 证据标准化器，统一日期、URL、字段命名与文本格式
│   │   └── evidence_ranker.py               # 证据排序器，依据来源质量、时效性、相关度对证据排序
│   ├── extraction/                          # 信息抽取层，从预处理后的证据中提取结构化候选事实
│   │   ├── __init__.py
│   │   ├── company_profile_extractor.py     # 企业画像抽取器，提取行业、主营业务、产品服务、公司简介等信息
│   │   ├── development_extractor.py         # 近期动态抽取器，提取融资、合作、发布、扩张等事件信息
│   │   ├── demand_signal_extractor.py       # 需求信号抽取器，提取采购意向、数字化需求、增长需求等销售信号
│   │   ├── risk_signal_extractor.py         # 风险信号抽取器，提取经营、舆情、合规、财务等风险线索
│   │   ├── organization_extractor.py        # 组织信息抽取器，提取部门、岗位、决策链、团队结构等组织信息
│   │   └── evidence_reference_extractor.py  # 证据引用抽取器，为结构化结论绑定来源证据与引用片段
│   ├── analysis/                            # 分析层，对抽取结果进行归并、判断、推理与业务分析
│   │   ├── __init__.py
│   │   ├── company_profile_analyzer.py      # 企业画像分析器，归并多来源画像信息并输出统一企业画像
│   │   ├── recent_development_analyzer.py   # 近期动态分析器，对事件进行筛选、去重、排序和摘要整理
│   │   ├── demand_signal_analyzer.py        # 需求信号分析器，判断企业可能存在的业务需求和销售机会
│   │   ├── organization_analyzer.py         # 组织分析器，分析关键部门、角色分工和潜在决策链条
│   │   ├── risk_analyzer.py                 # 风险分析器，综合评估经营风险、合作风险与推进阻力
│   │   └── sales_assessment_analyzer.py     # 销售评估分析器，综合输出客户价值、可推进性和优先级建议
│   ├── scoring/                             # 评分层，将分析结果映射为统一可解释分数或等级
│   │   ├── __init__.py
│   │   ├── scoring_engine.py                # 评分引擎，执行评分规则计算总分、子分与权重汇总
│   │   └── scoring_mapper.py                # 评分映射器，将原始分值映射为等级、标签和前端可展示结果
│   ├── generation/                          # 生成层，基于分析结论生成销售动作建议与沟通内容
│   │   ├── __init__.py
│   │   ├── communication_strategy_generator.py # 沟通策略生成器，生成触达策略、沟通重点和话术方向
│   │   └── next_step_generator.py           # 下一步行动生成器，生成销售跟进建议、推进动作和执行建议
│   ├── assembly/                            # 结果组装层，将分析结果整合为最终输出结构
│   │   ├── __init__.py
│   │   ├── evidence_reference_builder.py    # 证据引用构建器，整理结论对应的证据引用列表与来源说明
│   │   ├── output_assembler.py              # 输出组装器，将各分析模块结果合成为统一 API 响应结构
│   │   └── output_validator.py              # 输出校验器，校验最终结果字段完整性、类型正确性与兼容性
│   ├── llm/                                 # 大模型适配层，封装模型调用、Prompt 渲染与结构化生成能力
│   │   ├── __init__.py
│   │   ├── llm_client.py                    # 大模型客户端，统一封装模型请求、重试、超时和返回处理
│   │   ├── prompt_renderer.py               # Prompt 渲染器，负责模板变量填充与提示词拼装
│   │   └── structured_generation.py         # 结构化生成器，约束模型输出为指定 JSON / schema 结构
│   └── mock/                                # Mock 模块，在真实链路未完成时提供可稳定返回的模拟结果
│      ├── __init__.py
│      └── mock_analyzer.py                  # Mock 分析器，生成模拟分析结果用于开发、联调与降级兜底
└── config/                                  # 配置目录，存放评分规则、运行参数和其他系统配置
    ├── __init__.py
    └── scoring.py                           # 评分规则配置，定义各分析维度的权重、区间与映射方式
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