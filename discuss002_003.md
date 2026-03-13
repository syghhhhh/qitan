Q:

选项 A
输出一份“services 重构设计文档”Markdown 版本

GPT-5.4:

# `backend/app/services` 重构设计文档

## 1. 文档目标

本文档用于定义 `backend/app/services` 的重构方案，明确：

- 服务层的总体职责
- 各模块的边界与职责
- 模块间调用关系
- 分阶段落地路径
- 与现有 `schemas`、`prompts`、`config` 的协作方式

本文档聚焦**架构设计**，不包含具体实现代码。

---

## 2. 背景与问题定义

当前项目已经具备以下基础：

- FastAPI 接口层
- Pydantic 数据模型
- Prompt 模板目录
- 评分配置
- 基础 mock 服务能力

但 `services` 层仍然偏单体化，尤其是当主逻辑集中在 `mock_analyzer.py` 这类文件中时，会带来以下问题：

### 2.1 主要问题

#### 2.1.1 业务编排与业务逻辑耦合
同一个模块可能同时承担：
- 请求入口
- 证据处理
- 商业判断
- 输出拼装

导致职责不清、难以维护。

#### 2.1.2 事实获取与商务分析混在一起
企业背调场景天然包含两个阶段：

1. **事实发现阶段**
   - 收集官网、新闻、招聘、风险等信息
   - 抽取结构化事实

2. **商务判断阶段**
   - 评估客户匹配度
   - 判断商机优先级
   - 推荐联系对象
   - 生成沟通策略

如果两者不分层，就会导致：
- 逻辑不可复用
- 分析依据不透明
- 难以追踪错误来源

#### 2.1.3 模块不可替换
未来系统会逐步接入：
- 新数据源
- 真正的检索组件
- 更稳定的 LLM 抽取链路
- 更精细的评分引擎

若当前结构缺乏清晰边界，就无法平滑演进。

#### 2.1.4 缺乏可追踪性和可调试性
业务上会频繁遇到类似问题：

- 为什么这个客户被评为 `P2`？
- 为什么推荐联系销售运营，而不是 IT？
- 为什么判定其存在 CRM 需求？
- 为什么 `recent_developments` 为空？

如果没有中间状态和证据链，就难以定位原因。

---

## 3. 重构目标

本次重构希望将 `backend/app/services` 建设为一个：

- **分阶段**
- **可插拔**
- **证据驱动**
- **可追溯**
- **支持 mock / hybrid / full pipeline 共存**

的企业分析引擎。

### 3.1 目标原则

#### 3.1.1 单一职责
每个模块只处理一类问题。

#### 3.1.2 清晰分层
按如下逻辑分层：

- 编排
- 上下文构建
- 实体确认
- 采集
- 预处理
- 抽取
- 分析
- 评分
- 生成
- 组装与校验

#### 3.1.3 可替换
任一层都可以独立替换实现，而不影响整体架构。

#### 3.1.4 可降级
当某些模块尚未实现或发生故障时，应支持：
- mock fallback
- 部分结果缺失但流程继续
- hybrid 模式运行

#### 3.1.5 可观测
流程中应保留足够的中间状态，以支持：
- 日志追踪
- 调试定位
- 结果解释
- 证据回放

---

## 4. 总体架构

### 4.1 建议目录结构

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

## 5. 分层设计与职责定义

---

## 5.1 `orchestrator/`：流程编排层

### 模块
- `analysis_orchestrator.py`
- `pipeline_state.py`

### 职责
编排整条分析链路，负责控制执行顺序、异常处理、降级策略和结果汇总。

### 关键职责
- 接收 API 层传入的标准请求
- 初始化分析上下文
- 组织各子模块调用
- 记录中间状态
- 对失败模块进行降级处理
- 最终输出统一结果对象

### 不负责
- 证据抽取细节
- 评分规则细节
- prompt 拼装
- 业务字段的直接生成

### `pipeline_state.py` 的作用
作为一次分析任务的运行时状态容器，记录如下中间产物：

- 原始请求
- 分析上下文
- 已确认企业对象
- 原始证据
- 清洗后证据
- 各类候选事实
- 各分析模块结果
- 评分明细
- 最终输出草稿
- 错误与降级信息

### 设计要求
- 支持调试与日志追踪
- 支持阶段失败后的部分继续执行
- 支持结果回放

---

## 5.2 `context/`：分析上下文构建层

### 模块
- `context_builder.py`

### 职责
将 API 请求中的业务输入转换为内部可用的分析上下文对象。

### 输入信息示例
- `company_name`
- `company_website`
- `user_company_product`
- `user_target_customer_profile`
- `sales_goal`
- `target_role`
- `extra_context`

### 输出目标
形成统一的 `AnalysisContext` 概念对象，用于表达：

- 分析目标公司
- 当前销售任务目标
- 我方产品定位
- ICP 特征
- 重点关注信号
- 联系对象偏好
- 分析优先级与降级策略

### 设计意义
同一个企业在不同场景下的分析重点不同：

- `first_touch`：更关注切入点和话术
- `lead_generation`：更关注需求信号
- `meeting_prep`：更关注组织结构和近期动态
- `solution_pitch`：更关注业务场景匹配
- `account_planning`：更关注长期经营机会

因此，上下文构建必须独立成层，避免分析逻辑散落在各个模块中。

---

## 5.3 `resolution/`：企业实体确认层

### 模块
- `entity_resolver.py`

### 职责
在信息采集前，先确认当前分析对象到底是哪一家企业。

### 要解决的问题
- 同名企业混淆
- 品牌名与注册主体不一致
- 官网域名与公司名映射不一致
- 用户仅给出简称或不完整名称

### 输出目标
形成统一的 `ResolvedCompany` 概念对象，建议包含：
- 标准公司名
- 官网域名
- 别名列表
- 实体识别置信度
- 解析备注

### 设计意义
实体确认是所有后续采集的基础。如果主体混淆，后续新闻、招聘、风险信息都会污染整体结果。

---

## 5.4 `collection/`：数据采集层

### 模块
- `base.py`
- `source_router.py`
- `website_collector.py`
- `news_collector.py`
- `jobs_collector.py`
- `company_registry_collector.py`
- `risk_collector.py`

### 总体职责
从不同来源获取原始证据，形成统一的 `RawEvidence` 集合。

### 设计原则
- 采集层只负责“获取信息”
- 不承担复杂业务判断
- 必须保留来源、原文、时间、URL 等元信息

---

### 5.4.1 `base.py`
定义采集器统一接口规范。

#### 作用
- 统一输入格式
- 统一输出格式
- 便于 orchestrator 统一调度不同采集器

---

### 5.4.2 `source_router.py`
根据任务类型选择本次应启用的数据源。

#### 判断依据
- `sales_goal`
- 是否提供官网
- 当前配置与预算
- 任务时延要求
- 数据源可用性

#### 示例
- 快速首触分析：官网 + 新闻
- 深度线索分析：官网 + 新闻 + 招聘
- 风险敏感场景：增加风险采集
- 组织洞察场景：增加招聘和团队页面

#### 设计意义
避免所有请求都走全量抓取，降低成本与时延。

---

### 5.4.3 `website_collector.py`
负责官网及站内相关页面采集。

#### 典型页面
- 首页
- 关于我们
- 产品/解决方案
- 新闻中心
- 联系我们
- 站内招聘页面

#### 支持下游场景
- 企业画像
- 近期动态
- 组织线索
- 沟通切入点分析

---

### 5.4.4 `news_collector.py`
负责企业相关新闻与媒体信息采集。

#### 关注信息
- 融资
- 合作
- 发布会
- 市场拓展
- 战略升级
- 行业提及

#### 支持下游场景
- 近期动态分析
- 需求信号分析
- 商机判断

---

### 5.4.5 `jobs_collector.py`
负责招聘信息采集。

#### 价值
招聘是需求信号的重要来源，可反映：
- 业务扩张
- 部门建设
- 数字化投入
- 系统采购方向
- 组织分工变化

#### 支持下游场景
- 需求信号分析
- 联系角色推荐
- 组织洞察

---

### 5.4.6 `company_registry_collector.py`
负责企业公开注册与基本信息采集。

#### 主要支持
- 企业基础画像补全
- 成立时间
- 企业类型
- 所在地
- 规模辅助判断

---

### 5.4.7 `risk_collector.py`
负责公开风险类信息采集。

#### 可包括
- 经营异常
- 司法信息
- 行政处罚
- 负面舆情
- 失信与执行相关公开信息

#### 设计要求
风险信息应与普通新闻采集分层处理，避免口径混淆。

---

## 5.5 `preprocessing/`：证据预处理层

### 模块
- `evidence_cleaner.py`
- `evidence_deduplicator.py`
- `evidence_normalizer.py`
- `evidence_ranker.py`

### 总体职责
将采集层返回的原始证据转化为高质量、统一格式、便于抽取的证据对象。

---

### 5.5.1 `evidence_cleaner.py`
负责文本清洗。

#### 包括
- 移除导航、页脚、模板内容
- 提取正文
- 去除 HTML 噪声
- 清理无意义字符
- 截取有效片段

---

### 5.5.2 `evidence_deduplicator.py`
负责证据去重。

#### 主要场景
- 新闻转载重复
- 官网新闻与媒体报道内容重复
- 站内多个页面重复介绍同一信息

#### 设计意义
避免重复信息被误判为“多源一致”。

---

### 5.5.3 `evidence_normalizer.py`
负责标准化。

#### 示例
- 统一日期格式
- 统一来源类型
- 统一 URL 格式
- 统一企业名称写法
- 统一证据标签

---

### 5.5.4 `evidence_ranker.py`
负责证据质量排序。

#### 排序维度
- 来源可信度
- 时间新鲜度
- 与任务目标的相关性
- 信息密度

#### 设计意义
后续抽取和分析应优先使用高质量证据，尤其在上下文长度受限时更关键。

---

## 5.6 `extraction/`：结构化事实抽取层

### 模块
- `company_profile_extractor.py`
- `development_extractor.py`
- `demand_signal_extractor.py`
- `risk_signal_extractor.py`
- `organization_extractor.py`
- `evidence_reference_extractor.py`

### 总体职责
将“证据文本”转为“结构化候选事实”。

### 设计原则
- 这一层只负责抽取候选事实
- 不做最终商业判断
- 允许多来源、带冲突、带置信度的候选结果存在

---

### 5.6.1 `company_profile_extractor.py`
负责抽取企业基础画像候选事实。

#### 可能字段
- 公司名称
- 行业
- 业务类型
- 主营业务
- 企业规模
- 成立时间
- 总部地点

---

### 5.6.2 `development_extractor.py`
负责抽取近期动态候选事件。

#### 目标字段
- 事件类型
- 日期
- 标题
- 摘要
- 来源

#### 特点
这里输出的是候选事件，不一定全部进入最终结果。

---

### 5.6.3 `demand_signal_extractor.py`
负责抽取需求信号候选。

#### 可能来源
- 招聘信息
- 合作公告
- 业务扩张信息
- 系统建设信息
- 组织变动线索

#### 说明
这里只抽取现象和候选方向，不直接输出商机判断。

---

### 5.6.4 `risk_signal_extractor.py`
负责抽取风险候选项。

#### 输出内容
- 风险类型
- 发生时间
- 风险描述
- 来源与证据

#### 说明
风险强弱与影响评估应由 analyzer 层完成。

---

### 5.6.5 `organization_extractor.py`
负责抽取组织与角色线索。

#### 可能输出
- 可识别部门
- 可能相关岗位
- 发言人/负责人角色
- 组织职责线索
- 联系入口线索

---

### 5.6.6 `evidence_reference_extractor.py`
负责建立候选事实与原始证据的映射。

#### 设计意义
后续 `evidence_references` 构建依赖这一层建立好 claim-to-evidence 映射。

---

## 5.7 `analysis/`：业务分析层

### 模块
- `company_profile_analyzer.py`
- `recent_development_analyzer.py`
- `demand_signal_analyzer.py`
- `organization_analyzer.py`
- `risk_analyzer.py`
- `sales_assessment_analyzer.py`

### 总体职责
基于候选事实、上下文和产品信息形成最终业务结论。

### 设计原则
- 分析层负责“判断”
- 抽取层负责“发现”
- 评分层负责“规则打分”
- 生成层负责“表达结果”

---

### 5.7.1 `company_profile_analyzer.py`
负责整合企业画像候选事实，生成最终 `company_profile`。

#### 核心工作
- 多来源合并
- 冲突消解
- 字段规范化
- 处理不确定性

---

### 5.7.2 `recent_development_analyzer.py`
负责筛选并整合最终 `recent_developments`。

#### 核心工作
- 事件去重与合并
- 时效性判断
- 商务相关性判断
- 分类与摘要统一

---

### 5.7.3 `demand_signal_analyzer.py`
负责生成最终 `demand_signals`。

#### 核心工作
- 信号聚合
- 强弱判断
- 将事实现象转化为业务需求判断
- 结合我方产品判断相关性与可转化性

#### 重要性
这是整个系统中最核心的价值模块之一。

---

### 5.7.4 `organization_analyzer.py`
负责输出组织洞察与推荐联系角色。

#### 输出方向
- 推荐联系部门
- 推荐角色
- 优先级
- 推荐理由
- 组织结构说明

#### 输入考虑因素
- `sales_goal`
- `target_role`
- 我方产品
- 当前需求信号
- 企业组织线索

---

### 5.7.5 `risk_analyzer.py`
负责生成最终 `risk_signals`。

#### 核心工作
- 风险严重程度判断
- 风险影响分析
- 低可信风险过滤
- 保守描述策略

---

### 5.7.6 `sales_assessment_analyzer.py`
负责形成最终销售判断。

#### 输出方向
- `customer_fit`
- `opportunity_level`
- `priority_score`
- `priority_reason`
- `suggested_next_steps`

#### 设计建议
- 分值计算交给 `scoring_engine`
- 解释与结论由 analyzer 完成

---

## 5.8 `scoring/`：评分层

### 模块
- `scoring_engine.py`
- `scoring_mapper.py`

### 总体职责
将分析结果转为规则化、可解释的优先级评分。

---

### 5.8.1 `scoring_engine.py`
负责多维评分计算。

#### 评分维度建议
- ICP 匹配度
- 需求信号强度
- 联系可行性
- 近期动态活跃度
- 风险扣分

#### 设计原则
尽量规则化、可解释，避免完全依赖模型自由生成。

---

### 5.8.2 `scoring_mapper.py`
负责将总分映射为业务优先级。

#### 示例输出
- `P1`
- `P2`
- `P3`
- `discard`

#### 设计意义
将“打分逻辑”与“阈值映射”解耦，便于后续调整策略。

---

## 5.9 `generation/`：内容生成层

### 模块
- `communication_strategy_generator.py`
- `next_step_generator.py`

### 总体职责
基于已确认的分析结论，生成对销售可直接使用的表达内容。

---

### 5.9.1 `communication_strategy_generator.py`
负责生成沟通策略与话术。

#### 输出内容
- `entry_point`
- `wechat_script`
- `phone_script`
- `email_script`

#### 设计要求
- 必须建立在已验证的分析结果上
- 不应直接从原始证据跳到话术生成
- 应控制风险表达，避免夸大与臆测

---

### 5.9.2 `next_step_generator.py`
负责生成下一步动作建议。

#### 示例方向
- 优先联系对象顺序
- 首触渠道建议
- 会前补充验证问题
- 后续推进动作建议

#### 设计意义
该能力偏行动规划，适合与话术生成分开维护。

---

## 5.10 `assembly/`：结果组装与校验层

### 模块
- `evidence_reference_builder.py`
- `output_assembler.py`
- `output_validator.py`

### 总体职责
将各模块产物整合成最终 API 输出，并进行质量校验。

---

### 5.10.1 `evidence_reference_builder.py`
负责构建最终 `evidence_references`。

#### 核心工作
- 为结论分配最相关证据
- 统一 source metadata
- 控制引用数量
- 去重与排序

---

### 5.10.2 `output_assembler.py`
负责将所有分析结果拼装成最终 `DueDiligenceOutput`。

#### 设计要求
- 只做拼装与映射
- 不承担复杂业务判断

---

### 5.10.3 `output_validator.py`
负责最终输出质量控制。

#### 校验内容示例
- 必填字段完整性
- 枚举值合法性
- 分数范围合法性
- 优先级与分数一致性
- 关键结论是否具备证据支撑
- 空字段是否符合降级策略

---

## 5.11 `llm/`：大模型适配层

### 模块
- `llm_client.py`
- `prompt_renderer.py`
- `structured_generation.py`

### 总体职责
为抽取与生成模块提供统一的大模型调用能力。

---

### 5.11.1 `llm_client.py`
负责模型调用封装。

#### 应处理内容
- 模型选择
- 超时
- 重试
- 调用日志
- 成本统计
- 参数管理

---

### 5.11.2 `prompt_renderer.py`
负责渲染 prompt 模板。

#### 设计意义
- 将 prompt 模板管理集中化
- 避免各模块自行拼接 prompt
- 便于版本管理和 A/B 测试

---

### 5.11.3 `structured_generation.py`
负责结构化输出控制。

#### 主要职责
- schema 对齐
- JSON 解析
- 容错修复
- 失败重试

#### 设计意义
系统中的大量抽取结果都依赖结构化输出，必须统一封装。

---

## 5.12 `mock/`：Mock 与降级层

### 模块
- `mock_analyzer.py`

### 职责
保留 mock 能力作为测试、演示和降级手段，而不是主分析实现。

### 使用场景
- 前端联调
- 某些真实模块未完成
- 端到端接口测试
- fallback 方案

---

## 6. 调用关系设计

### 6.1 顶层调用链

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
Collectors（并行或串行）
  ↓
Preprocessing（clean → dedupe → normalize → rank）
  ↓
Extractors
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

### 6.2 模块依赖关系图

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

## 7. 依赖方向约束

### 7.1 推荐依赖方向

```text
orchestrator
  → context / resolution / collection / preprocessing / extraction / analysis / scoring / generation / assembly

analysis
  → 基于 extraction 结果和 scoring 输出进行判断

extraction
  → llm / prompts

generation
  → llm / prompts

assembly
  → schemas

所有模块
  → schemas / config
```

### 7.2 禁止或不推荐的依赖
- collector 直接依赖 analyzer
- analyzer 反向调用 collector
- route 层直接调用多个 services 子模块
- prompt 内容散落在各业务模块中手工拼接
- 输出拼装逻辑写在 analyzer 或 route 中

---

## 8. 数据流分层原则

### 8.1 从“证据”到“结论”的标准路径

```text
RawEvidence
  ↓
CleanEvidence
  ↓
CandidateFacts
  ↓
AnalysisResults
  ↓
ScoreBreakdown
  ↓
GeneratedContent
  ↓
FinalOutput
```

### 8.2 各阶段含义

#### `RawEvidence`
采集到的原始文本、页面、新闻、职位、风险条目等。

#### `CleanEvidence`
经过清洗、去重、标准化和排序的高质量证据。

#### `CandidateFacts`
从证据中抽取出的结构化候选事实。

#### `AnalysisResults`
基于候选事实做出的业务判断结果。

#### `ScoreBreakdown`
规则化评分明细。

#### `GeneratedContent`
面向销售使用的文案、切入点、行动建议。

#### `FinalOutput`
最终 API 返回结果。

---

## 9. 模块职责边界总结

### 9.1 编排层
负责控制流程，不负责生成具体结论。

### 9.2 采集层
负责找信息，不负责判断信息意味着什么。

### 9.3 抽取层
负责把文本转结构，不负责判定商机强弱。

### 9.4 分析层
负责做业务判断，不负责底层模型调用细节。

### 9.5 评分层
负责量化规则，不负责解释文案。

### 9.6 生成层
负责“如何说”，不负责“是否成立”。

### 9.7 组装层
负责“如何交付”，不负责新增业务逻辑。

---

## 10. Mock、Hybrid、Full Pipeline 运行模式

为了支持渐进式落地，建议保留三种运行模式。

### 10.1 `full_mock`
整条链路使用 mock 输出。

#### 适用场景
- 前端联调
- 演示环境
- 无外部依赖测试

---

### 10.2 `hybrid`
部分模块使用真实实现，部分模块使用 mock。

#### 示例
- 企业画像、近期动态使用真实链路
- 风险与联系人推荐暂时 mock

#### 适用场景
- 分阶段开发
- 模块能力逐步上线
- 保持系统持续可用

---

### 10.3 `full_pipeline`
全流程使用真实实现。

#### 适用场景
- 生产环境
- 评测环境
- A/B 测试

---

## 11. 与现有项目结构的协作建议

### 11.1 与 `schemas/`
`services` 层应以 `schemas` 作为：
- 输入输出契约
- 最终结果结构标准
- 枚举与字段限制来源

### 11.2 与 `prompts/`
Prompt 模板建议仍保存在 `backend/app/prompts/`，由 `llm/prompt_renderer.py` 统一使用。

### 11.3 与 `config/`
评分权重、阈值、模块开关、数据源启用策略建议保存在 `config` 中，由：
- `source_router`
- `scoring_engine`
- `scoring_mapper`
- `orchestrator`
统一读取

### 11.4 与 API 层
API 层只做：
- 参数接收
- 调用 orchestrator
- 返回结果

不应承担业务流程逻辑。

---

## 12. 建议的 API 层调用方式

### 当前建议
路由层统一调用：

```text
AnalysisOrchestrator.analyze(request)
```

### API 层职责应仅包括
- 请求校验
- trace id 生成
- 调用 orchestrator
- 返回响应
- 异常映射为 HTTP 响应

### 不应包括
- 直接调用 collector
- 直接拼装最终输出
- 直接处理评分逻辑
- 直接读取 prompt 模板

---

## 13. 分阶段实施路径

---

## 13.1 Phase 1：拆分骨架，保持现有能力不变

### 目标
先完成目录结构和主干编排，不改变外部接口。

### 工作内容
- 创建分层目录结构
- 建立 `AnalysisOrchestrator`
- 建立 `pipeline_state`
- 建立 `output_assembler`
- 将现有 `mock_analyzer` 下沉到 `mock/`

### 结果
系统从“单文件逻辑”切换为“编排器驱动架构”，但仍可返回 mock 结果。

---

## 13.2 Phase 2：接入最小真实能力

### 推荐优先模块
- `context_builder`
- `entity_resolver`
- `website_collector`
- `news_collector`
- `evidence_cleaner`
- `company_profile_extractor`
- `development_extractor`
- `company_profile_analyzer`
- `recent_development_analyzer`
- `communication_strategy_generator`

### 目标
先做出“企业画像 + 近期动态 + 基础切入话术”的真实闭环。

---

## 13.3 Phase 3：补齐需求信号链路

### 推荐模块
- `jobs_collector`
- `demand_signal_extractor`
- `demand_signal_analyzer`

### 目标
提升系统的商务价值，使其真正具备线索判断能力。

---

## 13.4 Phase 4：接入评分能力

### 推荐模块
- `scoring_engine`
- `scoring_mapper`
- `sales_assessment_analyzer`

### 目标
形成可解释的优先级判断体系。

---

## 13.5 Phase 5：补齐组织与风险模块

### 推荐模块
- `organization_extractor`
- `organization_analyzer`
- `risk_collector`
- `risk_signal_extractor`
- `risk_analyzer`

### 目标
提升报告完整性与销售策略可执行性。

---

## 13.6 Phase 6：补齐证据链与质量控制

### 推荐模块
- `evidence_reference_builder`
- `output_validator`

### 目标
增强结果可信度、可回溯性与稳定性。

---

## 14. 关键设计原则

### 14.1 证据优先
所有关键结论都应尽量能追溯到证据来源。

### 14.2 先事实，后判断
先收集和抽取，再做业务分析，不要反向混写。

### 14.3 尽量规则化评分
评分尽可能由规则引擎完成，避免纯生成式打分。

### 14.4 保守处理不确定性
对不确定信息：
- 可以保留
- 需要标注置信度或弱化表达
- 不应强行下结论

### 14.5 渐进落地
不要试图一次性完成所有真实能力，应优先打通核心闭环。

---

## 15. 风险与注意事项

### 15.1 过早抽象风险
如果尚未建立最小真实链路，过度抽象可能导致结构复杂但无实际收益。建议按阶段推进。

### 15.2 collector 与 analyzer 边界被破坏
开发过程中最容易出现的退化是：collector 顺手做判断、analyzer 顺手读原始页面。应严格避免。

### 15.3 evidence 结构不统一
若不提前统一证据格式，后续模块会形成大量兼容代码。

### 15.4 prompt 分散
如果每个 extractor 都各自拼 prompt，后期将难以维护。应尽早统一到 `llm/prompt_renderer.py`。

### 15.5 输出质量不可控
若没有 `output_validator`，随着模块增多，输出结构和业务一致性会逐渐失控。

---

## 16. 结论

本次 `backend/app/services` 重构的核心，不是简单地“把一个文件拆成多个文件”，而是把服务层建设成一个真正的：

- 分层清晰
- 支持渐进式演化
- 以证据为基础
- 可解释、可调试、可替换

的分析引擎。

最终目标是让系统形成如下能力闭环：

```text
输入企业信息
  → 获取可信证据
  → 抽取结构化事实
  → 做出业务判断
  → 计算优先级
  → 生成销售策略
  → 输出可追溯报告
```

---

## 17. 后续建议

建议本文档落地后，下一步继续补充以下文档之一：

### 17.1 接口设计文档
为每个模块定义：
- 类名
- 方法名
- 输入对象
- 输出对象
- 失败策略

### 17.2 数据契约文档
定义统一的数据结构：
- `RawEvidence`
- `CleanEvidence`
- `CandidateFacts`
- `AnalysisContext`
- `ResolvedCompany`
- `ScoreBreakdown`
- `PipelineState`

### 17.3 编排时序文档
补充完整时序图，明确：
- 并行采集点
- 降级分支
- 超时处理
- fallback 路径

如果你愿意，我下一步可以继续直接给你输出：

1. **`services` 接口设计文档**
2. **`PipelineState / Evidence / CandidateFacts` 数据契约文档**
3. **完整时序图版架构文档**

我建议下一步先做 **2**，这样你后面开发时最不容易跑偏。