# 数据模型设计文档

## 概述

本项目数据模型基于 `discuss003.md` 定义的 JSON Schema 实现，使用 Pydantic v2 进行数据验证和序列化。

## 模型层级结构

```
DueDiligenceOutput (完整输出)
├── meta: Meta
├── input: Input
├── company_profile: CompanyProfile
├── recent_developments: List[RecentDevelopment]
├── demand_signals: List[DemandSignal]
├── organization_insights: OrganizationInsights
│   └── recommended_target_roles: List[RecommendedTargetRole]
├── risk_signals: List[RiskSignal]
├── sales_assessment: SalesAssessment
├── communication_strategy: CommunicationStrategy
└── evidence_references: List[EvidenceReference]
```

## 核心模型定义

### Meta (元信息)

```python
class Meta(BaseModel):
    version: str              # 输出版本
    generated_at: datetime    # 生成时间
    processing_time_seconds: float  # 处理耗时
```

### Input (输入信息)

```python
class Input(BaseModel):
    company_name: str                    # 企业名称
    company_website: Optional[str]       # 企业官网
    user_company_product: str            # 我方产品描述
    user_target_customer_profile: Optional[str]  # 理想客户画像
    sales_goal: SalesGoalEnum            # 跟进目标
    target_role: Optional[str]           # 目标角色
    extra_context: Optional[str]         # 补充背景
```

### CompanyProfile (企业画像)

```python
class CompanyProfile(BaseModel):
    company_name: str                    # 企业名称
    short_name: Optional[str]            # 简称
    industry: List[str]                  # 所属行业
    company_type: Optional[str]          # 企业类型
    founded_year: Optional[int]          # 成立年份
    headquarters: Optional[str]          # 总部所在地
    business_scope: List[str]            # 经营范围
    main_products_or_services: List[str] # 主营产品/服务
    estimated_size: Optional[str]        # 预估规模
    region_coverage: List[str]           # 业务覆盖区域
    official_website: Optional[str]      # 官网
    official_accounts: List[str]         # 公众号等
    profile_summary: Optional[str]       # 企业简介
```

### RecentDevelopment (近期动态)

```python
class RecentDevelopment(BaseModel):
    date: str                            # 日期
    type: RecentDevelopmentTypeEnum      # 动态类型
    title: str                           # 标题
    summary: str                         # 摘要
    source: Optional[str]                # 来源
    source_ref_ids: List[str]            # 关联证据ID
    confidence: int                      # 置信度 0-100
```

### DemandSignal (需求信号)

```python
class DemandSignal(BaseModel):
    signal_type: DemandSignalTypeEnum    # 信号类型
    signal: str                          # 信号描述
    evidence: str                        # 证据
    inference: str                       # 推断
    strength: StrengthEnum               # 信号强度
    source: Optional[str]                # 来源
    source_ref_ids: List[str]            # 关联证据ID
    date: Optional[str]                  # 日期
```

### OrganizationInsights (组织洞察)

```python
class OrganizationInsights(BaseModel):
    possible_target_departments: List[str]       # 可能的目标部门
    recommended_target_roles: List[RecommendedTargetRole]  # 推荐联系人
    possible_decision_chain: List[str]           # 可能的决策链
    key_people_public_info: List[KeyPeoplePublicInfo]      # 关键人公开信息
```

### RiskSignal (风险信号)

```python
class RiskSignal(BaseModel):
    risk_type: RiskTypeEnum              # 风险类型
    risk: str                            # 风险描述
    description: str                     # 详细说明
    impact: str                          # 影响评估
    level: StrengthEnum                  # 风险等级
    source: Optional[str]                # 来源
    source_ref_ids: List[str]            # 关联证据ID
    date: Optional[str]                  # 日期
```

### SalesAssessment (商务判断)

```python
class SalesAssessment(BaseModel):
    customer_fit_level: CustomerFitLevelEnum   # 客户匹配度
    opportunity_level: OpportunityLevelEnum    # 商机等级
    follow_up_priority: FollowUpPriorityEnum   # 跟进优先级
    core_opportunity_scenarios: List[str]      # 核心机会场景
    main_obstacles: List[str]                  # 主要障碍
    assessment_summary: str                    # 判断摘要
    should_follow_up: bool                     # 是否建议跟进
```

### CommunicationStrategy (沟通策略)

```python
class CommunicationStrategy(BaseModel):
    recommended_entry_points: List[str]  # 推荐切入点
    avoid_points: List[str]              # 避免切入点
    opening_message: str                 # 开场白建议
    phone_script: str                    # 电话话术
    wechat_message: str                  # 微信话术
    email_message: str                   # 邮件话术
    next_step_suggestion: str            # 下一步建议
```

### EvidenceReference (证据来源)

```python
class EvidenceReference(BaseModel):
    reference_id: str                    # 引用ID
    source: str                          # 来源名称
    title: Optional[str]                 # 标题
    url: Optional[str]                   # 链接
    date: Optional[str]                  # 日期
    excerpt: Optional[str]               # 摘录
```

## 枚举定义

详见 `backend/app/schemas/enums.py` 和 `backend/app/config/scoring.py`。

### 主要枚举

| 枚举名 | 说明 | 值 |
|--------|------|-----|
| SalesGoalEnum | 跟进目标 | lead_generation, first_touch, meeting_prep, solution_pitch, account_planning, other |
| RecentDevelopmentTypeEnum | 近期动态类型 | news, financing, hiring, expansion, new_product, bidding, partnership, digital_transformation, management_change, compliance, other |
| DemandSignalTypeEnum | 需求信号类型 | recruitment_signal, expansion_signal, digitalization_signal, growth_signal, management_signal, cost_reduction_signal, compliance_signal, customer_operation_signal, sales_management_signal, data_governance_signal, other |
| RiskTypeEnum | 风险类型 | legal, compliance, financial, reputation, procurement_complexity, organization_instability, low_budget_probability, unclear_demand, long_decision_cycle, other |
| StrengthEnum | 强度等级 | high, medium, low |
| CustomerFitLevelEnum | 客户匹配度 | high, medium, low |
| OpportunityLevelEnum | 商机等级 | P1, P2, P3, discard |
| FollowUpPriorityEnum | 跟进优先级 | P1, P2, P3, discard |

## 文件结构

```
backend/app/schemas/
├── __init__.py      # 模块导出
├── common.py        # 基础模型 (Meta, Input)
├── company.py       # 企业相关 (CompanyProfile, RecentDevelopment)
├── analysis.py      # 分析相关 (DemandSignal, RiskSignal, OrganizationInsights)
├── assessment.py    # 判断相关 (SalesAssessment, CommunicationStrategy)
├── output.py        # 输出模型 (DueDiligenceOutput, EvidenceReference)
└── enums.py         # 枚举定义和标签映射
```