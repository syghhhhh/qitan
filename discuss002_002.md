Q:

请给出backend/app/services的详细重构方案，包括各模块的职责定义和调用关系。

GPT-5.4:

下面给你一个**面向你当前仓库现状**的 `backend/app/services` 详细重构方案。  
我会尽量贴近你现在这个项目：

- 已有 FastAPI + Pydantic Schema
- 已有 prompts 目录
- 已有 scoring 配置
- 当前 services 里还是 `mock_analyzer.py`

目标是把它重构成一个**可逐步替换 mock、可扩展为真实智能体工作流**的服务层。

---

# 一、先说重构目标

这次重构的核心目标，不是“多拆几个文件”，而是解决 4 个问题：

## 1. 把“总控流程”从“具体分析逻辑”中拆出来
现在 `mock_analyzer.py` 大概率既承担入口，又承担结果拼装。  
以后应该改成：

- 一个模块负责编排
- 多个模块负责子任务
- 每个模块只做一件事

---

## 2. 把“事实获取”和“商务判断”拆开
你这个项目里最重要的一条边界是：

- **collect / extract**：发现事实
- **analyze / assess**：基于事实做商务判断

这两个阶段必须分开。

---

## 3. 让每一层都能单独替换
比如未来你可能会替换：
- 数据源
- LLM 提取方式
- 评分规则
- 话术生成策略

所以服务层必须模块化。

---

## 4. 为“可观测”和“调试”留接口
你后面一定会遇到：
- 为什么判成 P2？
- 为什么推荐销售运营？
- 为什么说有 CRM 需求？
- 为什么 recent_developments 是空？

如果模块边界不清晰，很难定位问题。

---

# 二、建议的目录结构

我建议把 `backend/app/services` 从单文件重构成下面这种结构：

```text
backend/app/services/
├── __init__.py
├── orchestrator/
│   ├── __init__.py
│   ├── analysis_orchestrator.py
│   └── pipeline_state.py
├── context/
│   ├── __init__.py
│   └── context_builder.py
├── resolution/
│   ├── __init__.py
│   └── entity_resolver.py
├── collection/
│   ├── __init__.py
│   ├── base.py
│   ├── source_router.py
│   ├── website_collector.py
│   ├── news_collector.py
│   ├── jobs_collector.py
│   ├── company_registry_collector.py
│   └── risk_collector.py
├── preprocessing/
│   ├── __init__.py
│   ├── evidence_cleaner.py
│   ├── evidence_deduplicator.py
│   ├── evidence_normalizer.py
│   └── evidence_ranker.py
├── extraction/
│   ├── __init__.py
│   ├── company_profile_extractor.py
│   ├── development_extractor.py
│   ├── demand_signal_extractor.py
│   ├── risk_signal_extractor.py
│   ├── organization_extractor.py
│   └── evidence_reference_extractor.py
├── analysis/
│   ├── __init__.py
│   ├── company_profile_analyzer.py
│   ├── recent_development_analyzer.py
│   ├── demand_signal_analyzer.py
│   ├── organization_analyzer.py
│   ├── risk_analyzer.py
│   └── sales_assessment_analyzer.py
├── scoring/
│   ├── __init__.py
│   ├── scoring_engine.py
│   └── scoring_mapper.py
├── generation/
│   ├── __init__.py
│   ├── communication_strategy_generator.py
│   └── next_step_generator.py
├── assembly/
│   ├── __init__.py
│   ├── evidence_reference_builder.py
│   ├── output_assembler.py
│   └── output_validator.py
├── llm/
│   ├── __init__.py
│   ├── llm_client.py
│   ├── prompt_renderer.py
│   └── structured_generation.py
└── mock/
    ├── __init__.py
    └── mock_analyzer.py
```

---

# 三、按层解释：每个目录的职责

---

## 1. `orchestrator/`：总控编排层

这是整个服务层的“大脑”。

### 目录建议
```text
orchestrator/
├── analysis_orchestrator.py
└── pipeline_state.py
```

---

### `analysis_orchestrator.py` 的职责

负责完整流程的编排：

1. 接收标准输入
2. 调用 context builder
3. 调用 entity resolver
4. 调用各 collector 收集证据
5. 调用 preprocessing 清洗证据
6. 调用 extraction 提取结构化候选事实
7. 调用 analysis 做商务分析
8. 调用 scoring 计算优先级
9. 调用 generation 生成沟通策略
10. 调用 assembly 组装最终输出

### 它**不应该**做什么
- 不直接写抽取逻辑
- 不直接写评分细节
- 不直接写 prompt
- 不直接处理单个字段生成

### 它应该关注什么
- 流程顺序
- 模块调用
- 降级策略
- 超时/异常处理
- 结果汇总

---

### `pipeline_state.py` 的职责

定义流程执行中的“中间态容器”。

你现在虽然最终输出模型很清楚，但工作流运行时需要一个状态对象，记录每一步产物。  
比如里面可以概念上包含：

- request input
- normalized context
- resolved company
- raw evidences
- cleaned evidences
- extracted facts
- analyzed results
- score breakdown
- final output draft

### 为什么必须有这个对象
因为后续你会需要：
- 调试每个阶段的输出
- 部分阶段失败后降级继续
- 在日志里回放整条链路

---

## 2. `context/`：任务上下文构建层

### 文件建议
```text
context/
└── context_builder.py
```

### 职责
把 API 输入转成内部分析上下文。

### 输入
- `company_name`
- `company_website`
- `user_company_product`
- `user_target_customer_profile`
- `sales_goal`
- `target_role`
- `extra_context`

### 输出
一个内部上下文对象，至少要表达：

- 这次分析的目标企业
- 当前销售目标是什么
- 我方卖什么
- 重点关注什么信号
- 哪些模块优先
- 沟通对象偏好
- 是否允许保守降级

### 为什么单独拆出来
因为 `sales_goal` 会直接影响全流程策略：

- `first_touch` 更重切入点和联系人
- `lead_generation` 更重需求信号
- `meeting_prep` 更重组织和动态
- `solution_pitch` 更重场景与匹配度
- `account_planning` 更重长期经营路径

这类“任务意图理解”不应该散落在各 analyzer 里。

---

## 3. `resolution/`：企业实体确认层

### 文件建议
```text
resolution/
└── entity_resolver.py
```

### 职责
在正式采集前，先确认企业身份。

### 需要解决的问题
- 同名企业
- 简称/别名/品牌名
- 官网和主体名称是否一致
- 用户没给官网时如何构造搜索主语

### 输入
- 用户输入的公司名
- 官网（如有）
- 补充背景

### 输出
一个“已确认企业对象”，可以概念上包含：
- canonical company name
- website domain
- aliases
- identity confidence
- resolution notes

### 为什么重要
这是防串数据的第一道门。  
例如同名企业的新闻、招聘、司法信息一旦混进来，后面所有分析都会偏。

### 调用关系
它应当在 orchestrator 里最先调用，作为后续 `collection` 的输入。

---

## 4. `collection/`：数据采集层

这个目录负责“找资料”。

### 目录建议
```text
collection/
├── base.py
├── source_router.py
├── website_collector.py
├── news_collector.py
├── jobs_collector.py
├── company_registry_collector.py
└── risk_collector.py
```

---

### `base.py`
定义采集器的统一接口规范。

### 它的职责
规定每个 collector 都应当接受什么输入、返回什么结构。  
例如概念上：
- 输入：resolved company + context
- 输出：raw evidence list

### 为什么需要
否则每个 collector 风格不同，orchestrator 很难统一调度。

---

### `source_router.py`
决定本次任务要启用哪些数据源。

### 它的职责
基于：
- `sales_goal`
- 是否提供官网
- 时间预算 / 配置
- 任务类型

选择：
- 只采官网 + 新闻
- 采官网 + 新闻 + 招聘
- 再加风险信息
- 或者以后加更多扩展源

### 价值
让系统不是“永远全量抓取”，而是按任务做资源分配。

---

### `website_collector.py`
采集官网相关内容。

### 重点内容
- 首页
- about/company 页面
- 新闻中心
- 产品页
- 联系我们
- 招聘页面（如果站内有）

### 输出
原始网页证据。

### 用途
主要支持：
- company_profile
- recent_developments
- organization_insights
- communication_strategy

---

### `news_collector.py`
采集新闻和媒体报道。

### 重点内容
- 企业相关新闻
- 融资、合作、扩张、发布会、行业提及

### 用途
主要支持：
- recent_developments
- demand_signals
- sales_assessment

---

### `jobs_collector.py`
采集招聘信息。

### 为什么它非常重要
对商务场景来说，招聘信息是非常高价值的需求线索来源。

### 它支持的分析
- 是否在扩张
- 哪些岗位在加大投入
- 是否有数字化/IT/销售运营建设需求
- 推荐联系人的职能推断

---

### `company_registry_collector.py`
采企业基础登记/公开工商类信息。

### 用途
主要支持：
- 企业基本画像补全
- 企业类型
- 成立时间
- 所在地
- 规模辅助判断

---

### `risk_collector.py`
采集法律、经营异常、处罚、舆情等风险类公开信息。

### 注意
风险模块一定要和普通新闻采集分开，因为它的数据口径、可信度和解释方式不同。

---

## 5. `preprocessing/`：证据预处理层

采集回来的原始数据通常非常脏，必须单独有这一层。

### 目录建议
```text
preprocessing/
├── evidence_cleaner.py
├── evidence_deduplicator.py
├── evidence_normalizer.py
└── evidence_ranker.py
```

---

### `evidence_cleaner.py`
负责内容清洗。

### 职责
- 去掉导航、页脚、模板文字
- 截取正文
- 去除重复片段
- 清理无意义字符

---

### `evidence_deduplicator.py`
负责证据去重。

### 为什么单独拆
很多新闻会被转载，官网新闻和媒体报道也可能重复。  
如果不去重，后面的信号分析会误以为“多源一致”而过度加分。

---

### `evidence_normalizer.py`
负责标准化字段。

### 例如
- 日期格式统一
- 来源类型统一
- URL 标准化
- 公司名称标准化
- 证据标签标准化

---

### `evidence_ranker.py`
负责对证据排序和赋予优先级。

### 排序维度
- 相关性
- 来源可信度
- 时间新鲜度
- 信息密度

### 为什么有用
LLM 上下文有限，后面抽取时应该优先吃高质量证据。

---

## 6. `extraction/`：结构化事实抽取层

这一层把“证据文本”变成“可分析对象”。

### 目录建议
```text
extraction/
├── company_profile_extractor.py
├── development_extractor.py
├── demand_signal_extractor.py
├── risk_signal_extractor.py
├── organization_extractor.py
└── evidence_reference_extractor.py
```

---

### `company_profile_extractor.py`
从官网、工商资料、企业介绍中抽：
- 名称
- 行业
- 业务类型
- 规模
- 主营业务
- 成立时间
- 总部地点

### 输出
“企业画像候选事实”，注意这里还不是最终画像结论。

---

### `development_extractor.py`
从新闻、官网动态中抽取“近期动态候选项”。

### 输出字段应贴近你现有 Schema
- type
- date
- title
- summary
- source_url

### 但这里是候选项，后面 analyzer 再决定保留哪些。

---

### `demand_signal_extractor.py`
从招聘、扩张、合作、系统建设信息中抽取“需求信号候选”。

### 它做的是：
- 看到了什么现象
- 该现象可能指向哪种需求类别

### 它**不应该**最终判定“商机强弱”
那是 analyzer 的事。

---

### `risk_signal_extractor.py`
从风险类证据中抽取“风险候选”。

### 输出
事实化的风险条目，例如：
- 风险类型
- 发生时间
- 描述
- 来源

### 仍然不是最终 severity 结论。

---

### `organization_extractor.py`
抽取组织角色和部门线索。

### 来源
- 招聘 JD
- 团队介绍
- 新闻发言人
- 联系方式页面
- 组织描述

### 输出
候选组织信息，如：
- 可能部门
- 可能角色
- 角色与业务场景的关系

---

### `evidence_reference_extractor.py`
负责把候选事实和原始证据建立映射。

### 为什么单独拆
你的最终输出有 `evidence_references`，这意味着：
- 每个关键结论必须知道它来自哪些证据
- 否则最后没法做可追溯输出

---

## 7. `analysis/`：商务分析层

这是你的“智能体价值”核心。

### 目录建议
```text
analysis/
├── company_profile_analyzer.py
├── recent_development_analyzer.py
├── demand_signal_analyzer.py
├── organization_analyzer.py
├── risk_analyzer.py
└── sales_assessment_analyzer.py
```

---

### `company_profile_analyzer.py`
把多个来源的画像候选事实整合成最终 `company_profile`。

### 它负责
- 冲突消解
- 字段选择
- 不确定性处理
- 最终输出统一口径

### 举例
官网说“专注零售数字化”，注册信息显示“软件开发”，新闻说“SaaS 服务商”。  
analyzer 要决定最终行业/主营业务怎么表达最合适。

---

### `recent_development_analyzer.py`
从候选事件中筛出“真正值得保留的近期动态”。

### 它负责
- 去重合并
- 评估是否够新
- 判断是否值得商务关注
- 事件归类

### 输出
最终 `recent_developments`

---

### `demand_signal_analyzer.py`
把候选信号转成最终 `demand_signals`。

### 它负责
- 根据信号类型合并相似线索
- 判断强弱（high/medium/low）
- 写清 evidence 和 inference
- 结合我方产品判断是否相关

### 这是项目最核心的智能模块之一
因为“看到了什么”不等于“这家公司可能有需求”。

---

### `organization_analyzer.py`
从组织候选线索中得出：
- 推荐联系人
- 部门
- 优先级
- 推荐理由
- 组织结构补充说明

### 它要综合考虑
- `sales_goal`
- `target_role`
- 我方产品类型
- 企业当前信号
- 可触达可行性

---

### `risk_analyzer.py`
把风险候选转换成最终 `risk_signals`。

### 它负责
- 给 severity
- 评估 impact
- 过滤低可信风险
- 保守描述

### 注意
这一层最好偏保守，宁可少报，不要夸大。

---

### `sales_assessment_analyzer.py`
负责最终商务判断。

### 它会结合
- 企业画像
- 需求信号
- 联系人可行性
- 风险情况
- ICP 画像
- scoring engine 的结果

### 输出
- customer_fit
- opportunity_level
- priority_score
- priority_reason
- suggested_next_steps

### 注意
这里的“算分”和“解释分数”最好分开：
- 评分交给 `scoring/`
- 解释交给 analyzer

---

## 8. `scoring/`：评分与优先级映射层

### 目录建议
```text
scoring/
├── scoring_engine.py
└── scoring_mapper.py
```

---

### `scoring_engine.py`
实现你 README 里定义的多维评分模型。

### 它负责
- ICP 匹配度分数
- 需求信号分数
- 可触达可行性分数
- 风险扣分
- 总分计算

### 要求
尽量规则化、确定性，不要交给模型自由发挥。

---

### `scoring_mapper.py`
负责把分数映射成：
- P1 / P2 / P3 / discard
- 可选的标签化解释

### 为什么单独拆
这样以后如果调整阈值，只改 mapper，不影响 engine。

---

## 9. `generation/`：沟通策略生成层

### 目录建议
```text
generation/
├── communication_strategy_generator.py
└── next_step_generator.py
```

---

### `communication_strategy_generator.py`
基于前面分析结果生成：

- `entry_point`
- `wechat_script`
- `phone_script`
- `email_script`

### 它的输入必须来自上游成熟结果
不能直接对原始证据胡乱生成。

### 它应考虑的变量
- sales_goal
- 我方产品
- 企业画像
- 近期动态
- 需求信号
- 推荐联系人
- 风险限制

---

### `next_step_generator.py`
生成 `suggested_next_steps`

### 为什么值得单独拆
“下一步动作建议”在逻辑上更像销售行动规划，不完全等于话术生成。  
后期可以做得更细，比如：
- 补充信息验证
- 首触角色排序
- 外呼 / 微信 / 邮件顺序
- 会前问题清单

---

## 10. `assembly/`：结果组装与校验层

### 目录建议
```text
assembly/
├── evidence_reference_builder.py
├── output_assembler.py
└── output_validator.py
```

---

### `evidence_reference_builder.py`
把最终结论和证据绑定，生成 `evidence_references`。

### 它负责
- 为 claim 找到最合适来源
- 去重引用
- 填 source_name/source_url/retrieved_at

---

### `output_assembler.py`
把所有模块产物装配成最终 `DueDiligenceOutput`。

### 它做的是纯拼装，不做复杂业务判断。

---

### `output_validator.py`
对最终输出做质量控制。

### 校验内容
- 必填字段是否齐全
- 枚举是否合法
- 分数是否在 0-100
- priority 与 score 是否一致
- 关键结论是否有证据支撑
- 空列表/空字段是否符合降级策略

### 为什么必须有
防止上游某一环掉数据，最终 API 输出结构损坏。

---

## 11. `llm/`：大模型调用适配层

你现在已经有 `backend/app/prompts/`，所以 services 里建议有一个专门的 LLM 接入层，而不是让每个 extractor 自己拼 prompt。

### 目录建议
```text
llm/
├── llm_client.py
├── prompt_renderer.py
└── structured_generation.py
```

---

### `llm_client.py`
负责统一封装模型调用。

### 它应处理
- 模型名称
- 超时
- 重试
- 日志
- 成本统计
- 温度等参数

---

### `prompt_renderer.py`
负责把 `prompts/` 下模板与输入数据拼装成最终 prompt。

### 这样做好处
- prompt 管理集中
- 便于 A/B 测试
- extractor/analyzer 不关心 prompt 文件细节

---

### `structured_generation.py`
负责“让模型输出结构化结果”。

### 它应处理
- schema 约束
- JSON 解析
- 失败重试
- 容错修复

### 为什么重要
你这个项目大量依赖结构化输出，这层很关键。

---

## 12. `mock/`：保留 mock 作为降级与测试入口

### 文件建议
```text
mock/
└── mock_analyzer.py
```

### 职责
保留现有 mock 能力，但不再作为主实现。

### 使用场景
- 本地 UI 联调
- 某些 collector 未接入时的降级
- 端到端接口测试
- demo 模式

---

# 四、建议的调用关系

下面是最核心的部分：**各模块之间怎么调用**。

---

## 顶层调用链

```text
API /analyze
  ↓
AnalysisOrchestrator
  ↓
ContextBuilder
  ↓
EntityResolver
  ↓
SourceRouter
  ↓
Collectors（并行/串行）
  ↓
Preprocessing（clean → dedupe → normalize → rank）
  ↓
Extractors（并行）
  ↓
Analyzers
  ↓
ScoringEngine + ScoringMapper
  ↓
CommunicationStrategyGenerator + NextStepGenerator
  ↓
EvidenceReferenceBuilder
  ↓
OutputAssembler
  ↓
OutputValidator
  ↓
DueDiligenceOutput
```

---

## 更细一点的模块依赖图

```text
analysis_orchestrator
├─ context_builder
├─ entity_resolver
├─ source_router
├─ collectors
│  ├─ website_collector
│  ├─ news_collector
│  ├─ jobs_collector
│  ├─ company_registry_collector
│  └─ risk_collector
├─ preprocessing
│  ├─ evidence_cleaner
│  ├─ evidence_deduplicator
│  ├─ evidence_normalizer
│  └─ evidence_ranker
├─ extraction
│  ├─ company_profile_extractor
│  ├─ development_extractor
│  ├─ demand_signal_extractor
│  ├─ risk_signal_extractor
│  ├─ organization_extractor
│  └─ evidence_reference_extractor
├─ analysis
│  ├─ company_profile_analyzer
│  ├─ recent_development_analyzer
│  ├─ demand_signal_analyzer
│  ├─ organization_analyzer
│  ├─ risk_analyzer
│  └─ sales_assessment_analyzer
├─ scoring
│  ├─ scoring_engine
│  └─ scoring_mapper
├─ generation
│  ├─ communication_strategy_generator
│  └─ next_step_generator
└─ assembly
   ├─ evidence_reference_builder
   ├─ output_assembler
   └─ output_validator
```

---

# 五、按“输入输出”定义每个模块的职责边界

这里我用更工程化的方式写一下，方便你后面直接转成设计文档。

---

## 1. AnalysisOrchestrator

### 输入
- AnalyzeRequest（API request model）

### 输出
- DueDiligenceOutput

### 责任
- 组织整条链路
- 控制调用顺序
- 处理异常和降级
- 收集 meta 信息（耗时、版本等）

### 不负责
- 具体字段计算
- 具体 prompt 内容
- 具体分数规则

---

## 2. ContextBuilder

### 输入
- 原始用户输入

### 输出
- AnalysisContext

### 责任
- 标准化输入
- 推导本次分析重点
- 决定策略偏好

---

## 3. EntityResolver

### 输入
- AnalysisContext

### 输出
- ResolvedCompany

### 责任
- 企业主体确认
- 名称/域名/别名统一
- 身份置信度判断

---

## 4. Collectors

### 输入
- ResolvedCompany
- AnalysisContext

### 输出
- RawEvidence[]

### 责任
- 从不同来源采集信息
- 不做复杂推理
- 保留来源和原文

---

## 5. Preprocessing

### 输入
- RawEvidence[]

### 输出
- CleanEvidence[]

### 责任
- 去噪、去重、标准化、排序
- 给后续抽取提供高质量上下文

---

## 6. Extractors

### 输入
- CleanEvidence[]
- AnalysisContext
- ResolvedCompany

### 输出
- 各类 Candidate Facts

### 责任
- 从证据中提取结构化事实候选
- 不做最终商务结论

---

## 7. Analyzers

### 输入
- Candidate Facts
- AnalysisContext
- 我方产品/ICP信息

### 输出
- 最终业务模块结果

### 责任
- 把事实转为业务判断
- 生成理由和解释
- 形成可交付报告内容

---

## 8. ScoringEngine

### 输入
- 分析结果中的结构化指标

### 输出
- ScoreBreakdown + total score

### 责任
- 规则化评分

---

## 9. Generation

### 输入
- 已成熟的分析结论

### 输出
- 话术和行动建议

### 责任
- 生成客户沟通内容
- 保持与证据一致

---

## 10. Assembly

### 输入
- 所有分析模块结果

### 输出
- 最终 API 输出对象

### 责任
- 组装、校验、补齐、输出

---

# 六、建议的执行顺序

可以按下面顺序实现，不需要一步到位。

---

## Phase 1：先拆骨架，不改业务功能

目标：把现有 `mock_analyzer.py` 拆成可扩展架构，但内部仍返回 mock。

### 这一步应完成
- 新建 services 子目录结构
- 引入 `AnalysisOrchestrator`
- 建立 `ContextBuilder`
- 建立 `OutputAssembler`
- 把原 `mock_analyzer` 改成 orchestrator 的一个 fallback

### 效果
接口不变，但架构已经变成“可插拔”。

---

## Phase 2：先接入最小真实链路

建议最先实现这几个模块：

- `entity_resolver`
- `website_collector`
- `news_collector`
- `evidence_cleaner`
- `company_profile_extractor`
- `development_extractor`
- `company_profile_analyzer`
- `recent_development_analyzer`
- `communication_strategy_generator`

### 为什么先做这些
因为它们最容易形成对外可见价值。

---

## Phase 3：补需求信号闭环

再实现：

- `jobs_collector`
- `demand_signal_extractor`
- `demand_signal_analyzer`

这一步会明显提升“商务智能体”味道。

---

## Phase 4：补评分模块

实现：

- `scoring_engine`
- `scoring_mapper`
- `sales_assessment_analyzer`

---

## Phase 5：补组织推荐与风险分析

实现：

- `organization_extractor`
- `organization_analyzer`
- `risk_collector`
- `risk_signal_extractor`
- `risk_analyzer`

---

## Phase 6：补证据链与质量控制

实现：

- `evidence_reference_builder`
- `output_validator`

---

# 七、你当前代码里最应该改的入口位置

虽然你没有贴 `backend/app/main.py` 内容，但按 README 推测，`POST /analyze` 现在应该直接调用 `mock_analyzer`。

建议以后改成：

```text
main.py
  ↓
route handler
  ↓
AnalysisOrchestrator.analyze(request)
  ↓
返回 DueDiligenceOutput
```

也就是说：

- `main.py` 只保留 API 层职责
- 所有业务流程都进 orchestrator
- 不要在 route 里写具体分析逻辑

---

# 八、建议的依赖方向

这一点很关键，能避免后面循环依赖。

## 依赖方向应当是单向的：

```text
orchestrator
  → context / resolution / collection / preprocessing / extraction / analysis / scoring / generation / assembly

analysis
  → extraction / scoring（可通过数据对象，不直接强依赖实现）

extraction
  → llm / prompts

generation
  → llm / prompts

assembly
  → schemas

所有模块
  → schemas / config
```

---

## 不建议出现的依赖
- collector 直接调用 analyzer
- analyzer 反向调用 collector
- route 直接调用多个 service 子模块
- prompt 文件在每个模块里散着拼接

---

# 九、关于 mock 如何平滑迁移

你现在有 `mock_analyzer.py`，建议不要直接删除，而是这样过渡：

---

## 方案：保留三种模式

### 1. full_mock
整条链路全 mock  
用于前端联调和演示。

### 2. hybrid
部分真实、部分 mock  
比如：
- 画像和动态是真实
- 风险和联系人推荐先 mock

### 3. full_pipeline
全流程真实

---

## 为什么这样最好
因为你的工作流是分模块建设的，不可能一口气做完。  
hybrid 模式可以让系统持续可用。

---

# 十、模块之间的“契约”要先于代码

你说先不写具体代码，所以我建议你在落地前先定义以下契约文档。

---

## 1. Orchestrator 阶段契约
定义每个阶段：
- 输入对象
- 输出对象
- 失败时返回什么
- 是否允许空

---

## 2. Evidence 契约
统一原始证据和清洗后证据的数据格式。

否则后面 collector 一多就乱。

---

## 3. Candidate Fact 契约
统一 extractor 输出格式。

例如：
- company facts
- development candidates
- signal candidates
- risk candidates
- org candidates

---

## 4. Analysis Result 契约
统一 analyzer 输出格式。

这样 assembly 才好组装。

---

# 十一、一个适合你项目的“简化版调用示意”

下面这个最接近你可以实际落地的版本：

```text
POST /analyze
  ↓
AnalysisOrchestrator
  ├─ ContextBuilder
  ├─ EntityResolver
  ├─ SourceRouter
  ├─ WebsiteCollector
  ├─ NewsCollector
  ├─ JobsCollector
  ├─ EvidenceCleaner
  ├─ EvidenceDeduplicator
  ├─ EvidenceNormalizer
  ├─ CompanyProfileExtractor
  ├─ DevelopmentExtractor
  ├─ DemandSignalExtractor
  ├─ CompanyProfileAnalyzer
  ├─ RecentDevelopmentAnalyzer
  ├─ DemandSignalAnalyzer
  ├─ OrganizationAnalyzer
  ├─ ScoringEngine
  ├─ SalesAssessmentAnalyzer
  ├─ CommunicationStrategyGenerator
  ├─ EvidenceReferenceBuilder
  ├─ OutputAssembler
  └─ OutputValidator
```

这条链已经足够支撑一个比较真实的 MVP 了。

---

# 十二、我对你当前项目最推荐的 services 重构落地顺序

如果你现在马上要开始改，我建议按这个顺序做：

## 第 1 步
把 `mock_analyzer.py` 提升为：
- `orchestrator/analysis_orchestrator.py`
- `assembly/output_assembler.py`
- `mock/mock_analyzer.py`

先完成主干迁移。

---

## 第 2 步
补 `context/` 和 `resolution/`

让流程具备“任务上下文”和“企业确认”能力。

---

## 第 3 步
补 `collection/` + `preprocessing/`

即使先接简单数据源，也先把证据管道建立起来。

---

## 第 4 步
补 `extraction/`

先只做：
- 企业画像抽取
- 近期动态抽取
- 需求信号抽取

---

## 第 5 步
补 `analysis/` 和 `generation/`

形成真实商务输出。

---

## 第 6 步
补 `scoring/` 和 `assembly/output_validator.py`

把结果做稳定。

---

# 十三、最终建议：你应该把 services 层当成“分析引擎”

一句话总结这个重构方案：

> `backend/app/services` 不应该再是一个“返回 mock JSON 的地方”，而应该被重构成一个**分阶段、可插拔、证据驱动、可回溯的企业背调分析引擎**。

---

如果你愿意，下一步我可以继续帮你做两件更具体的事情之一：

## 选项 A
**直接给你输出一份“services 重构设计文档”Markdown 版本**，你可以放进 `docs/` 里

## 选项 B
**继续往下细化：把每个 services 模块的接口草案列出来**  
例如每个文件里有哪些类、方法、输入输出对象，但仍然不写实现代码

我建议下一步做 **选项 B**，这样你就可以直接按接口开始开发。