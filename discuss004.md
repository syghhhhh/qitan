Q:

请同时提供字段枚举字典和评分规则表，以便我进行后续的开发落地

GPT-5.4:

# 企业背调智能体 MVP  
## 字段枚举字典 + 评分规则表

下面我直接补一套**适合开发落地**的版本，尽量满足这几个目标：

- **前后端统一口径**
- **便于 LLM 稳定输出**
- **便于规则引擎接入**
- **便于后续扩展为可解释评分系统**

我会分成两部分：

1. **字段枚举字典**
2. **评分规则表**

---

# 一、字段枚举字典

建议你们把枚举统一维护成一份配置，例如：

- 后端常量
- 前端展示映射
- Prompt 中的允许值
- 数据校验器的 enum
- BI 分析字段

---

## 1. `meta.language`

```json
{
  "zh-CN": "简体中文",
  "en-US": "English (US)"
}
```

---

## 2. `input.sales_goal`

这是“本次任务意图”，建议不要太多，先控制在 MVP 范围。

```json
{
  "lead_generation": {
    "label": "线索挖掘",
    "description": "判断企业是否值得进入销售线索池"
  },
  "first_touch": {
    "label": "首次触达",
    "description": "生成初次沟通建议和切入点"
  },
  "meeting_prep": {
    "label": "会前准备",
    "description": "为销售拜访或线上会议提供背景材料"
  },
  "solution_pitch": {
    "label": "方案推进",
    "description": "辅助识别业务场景和价值表达方向"
  },
  "account_planning": {
    "label": "客户经营",
    "description": "针对重点客户做账户规划和角色分析"
  },
  "other": {
    "label": "其他",
    "description": "保留扩展用途"
  }
}
```

---

## 3. `recent_developments[].type`

建议这个枚举严格控制，否则模型容易乱造类别。

```json
{
  "news": {
    "label": "新闻动态",
    "description": "泛新闻、媒体报道、企业公告"
  },
  "financing": {
    "label": "融资事件",
    "description": "融资、增资、投资并购等资本动作"
  },
  "hiring": {
    "label": "招聘动态",
    "description": "公开招聘、岗位扩张、关键岗位招聘"
  },
  "expansion": {
    "label": "业务扩张",
    "description": "区域扩张、团队扩张、渠道扩张、海外拓展"
  },
  "new_product": {
    "label": "新产品/新方案",
    "description": "发布新产品、新解决方案、新服务能力"
  },
  "bidding": {
    "label": "招投标相关",
    "description": "招标、中标、采购立项、集采等"
  },
  "partnership": {
    "label": "合作伙伴动态",
    "description": "生态合作、战略合作、渠道合作"
  },
  "digital_transformation": {
    "label": "数字化建设",
    "description": "信息化、数字化、系统建设、平台升级"
  },
  "management_change": {
    "label": "管理层变动",
    "description": "高管任命、组织调整、负责人变更"
  },
  "compliance": {
    "label": "合规相关",
    "description": "监管、资质、审计、整改、合规建设"
  },
  "other": {
    "label": "其他",
    "description": "不适合归类到上述类型的动态"
  }
}
```

---

## 4. `demand_signals[].signal_type`

这个字段非常关键，因为它决定后续的分析维度、推荐话术和评分逻辑。

```json
{
  "recruitment_signal": {
    "label": "招聘信号",
    "description": "通过招聘岗位反映企业组织或能力建设方向"
  },
  "expansion_signal": {
    "label": "扩张信号",
    "description": "区域、业务、团队、渠道或市场扩张"
  },
  "digitalization_signal": {
    "label": "数字化信号",
    "description": "信息化系统建设、平台升级、流程数字化"
  },
  "growth_signal": {
    "label": "增长信号",
    "description": "融资、营收增长、业务增长、客户增长"
  },
  "management_signal": {
    "label": "管理升级信号",
    "description": "流程标准化、组织调整、经营管理升级"
  },
  "cost_reduction_signal": {
    "label": "降本增效信号",
    "description": "提效、自动化、成本控制、运营优化"
  },
  "compliance_signal": {
    "label": "合规信号",
    "description": "内控、审计、监管、资质、数据合规"
  },
  "customer_operation_signal": {
    "label": "客户经营信号",
    "description": "客户成功、会员运营、客户生命周期管理"
  },
  "sales_management_signal": {
    "label": "销售管理信号",
    "description": "销售流程、CRM、销售运营、商机管理"
  },
  "data_governance_signal": {
    "label": "数据治理信号",
    "description": "数据平台、数据质量、主数据、BI、治理体系"
  },
  "other": {
    "label": "其他信号",
    "description": "暂不归类"
  }
}
```

---

## 5. `demand_signals[].strength`

```json
{
  "high": {
    "label": "强",
    "description": "有直接证据支撑，且与采购/建设场景高度相关"
  },
  "medium": {
    "label": "中",
    "description": "有一定证据支撑，但仍需进一步确认"
  },
  "low": {
    "label": "弱",
    "description": "仅为间接信号，推断成分较多"
  }
}
```

---

## 6. `risk_signals[].risk_type`

```json
{
  "legal": {
    "label": "法律风险",
    "description": "诉讼、仲裁、法律争议等"
  },
  "compliance": {
    "label": "合规风险",
    "description": "监管处罚、整改、资质问题、数据合规问题"
  },
  "financial": {
    "label": "财务风险",
    "description": "资金压力、经营异常、偿债压力等"
  },
  "reputation": {
    "label": "舆情风险",
    "description": "负面舆论、品牌形象受损"
  },
  "procurement_complexity": {
    "label": "采购复杂度高",
    "description": "招采流程复杂、审批链长、集采门槛高"
  },
  "organization_instability": {
    "label": "组织不稳定",
    "description": "高管频繁变动、组织频繁调整"
  },
  "low_budget_probability": {
    "label": "预算不足概率高",
    "description": "需求可能存在，但预算条件不明或偏弱"
  },
  "unclear_demand": {
    "label": "需求不清晰",
    "description": "缺少明确场景和强需求信号"
  },
  "long_decision_cycle": {
    "label": "决策周期长",
    "description": "涉及多部门、多层审批或大型采购流程"
  },
  "other": {
    "label": "其他风险",
    "description": "暂不归类"
  }
}
```

---

## 7. `risk_signals[].level`

```json
{
  "high": "高",
  "medium": "中",
  "low": "低"
}
```

---

## 8. `sales_assessment.customer_fit_level`

这个字段表示“企业与我方 ICP 的静态适配度”。

```json
{
  "high": {
    "label": "高匹配",
    "description": "行业、规模、业务模式、场景与我方目标客户高度一致"
  },
  "medium": {
    "label": "中匹配",
    "description": "存在一定适配性，但不是典型目标客户"
  },
  "low": {
    "label": "低匹配",
    "description": "行业、规模、场景或组织形态与我方产品明显不匹配"
  }
}
```

---

## 9. `sales_assessment.opportunity_level`

这个字段表示“当前是否值得推进”。

```json
{
  "high": {
    "label": "高商机",
    "description": "近期存在明显需求信号，且与我方产品价值场景吻合"
  },
  "medium": {
    "label": "中商机",
    "description": "存在一些需求信号，但仍需进一步确认"
  },
  "low": {
    "label": "低商机",
    "description": "缺少有效需求信号，或当前窗口不明显"
  }
}
```

---

## 10. `sales_assessment.follow_up_priority`

建议直接作为销售动作优先级，而不是机会评分的简单映射。

```json
{
  "P1": {
    "label": "高优先级",
    "description": "建议尽快跟进，适合分配给销售做重点触达"
  },
  "P2": {
    "label": "中优先级",
    "description": "建议进入跟进池，择机触达"
  },
  "P3": {
    "label": "低优先级",
    "description": "建议保留观察，暂不重点投入"
  },
  "discard": {
    "label": "放弃",
    "description": "当前不建议继续投入销售资源"
  }
}
```

---

## 11. `organization_insights.recommended_target_roles[].priority`

这个字段建议统一为数值越小优先级越高，便于排序。

```json
{
  "1": "最高优先联系角色",
  "2": "较高优先联系角色",
  "3": "可作为备选切入角色",
  "4": "低优先级辅助角色",
  "5": "仅在特定场景下考虑"
}
```

如果你希望更强约束，MVP 里可以只允许 `1~5`，不要到 `10`。  
这样对销售更友好。

---

## 12. 推荐补充的“内部标准枚举”

虽然你之前 Schema 没有强制要求，但我建议开发时额外维护以下枚举字典。

---

### 12.1 企业规模标准化枚举 `normalized_company_size`

建议不要只存原始文本，最好做一个标准化字段，方便打分。

```json
{
  "micro": {
    "label": "1-20人",
    "description": "微型团队"
  },
  "small": {
    "label": "21-99人",
    "description": "小型企业"
  },
  "medium": {
    "label": "100-499人",
    "description": "中型企业"
  },
  "large": {
    "label": "500-1999人",
    "description": "大型企业"
  },
  "enterprise": {
    "label": "2000人以上",
    "description": "超大型/集团型企业"
  },
  "unknown": {
    "label": "未知",
    "description": "公开信息不足"
  }
}
```

---

### 12.2 企业类型标准化枚举 `normalized_company_type`

```json
{
  "private": "民营企业",
  "state_owned": "国有企业",
  "foreign_owned": "外资企业",
  "joint_venture": "合资企业",
  "public_listed": "上市公司",
  "subsidiary": "子公司/分公司",
  "government_institution": "政府/事业单位",
  "nonprofit": "非营利组织",
  "other": "其他",
  "unknown": "未知"
}
```

---

### 12.3 来源类型标准化枚举 `evidence_references[].source`

```json
{
  "official_website": "官网",
  "official_wechat": "官方公众号",
  "news_media": "新闻媒体",
  "recruitment_posting": "招聘信息",
  "annual_report": "年报/财报/招股书",
  "registry_record": "工商/登记公开信息",
  "bidding_notice": "招标公告",
  "winning_notice": "中标公告",
  "social_media": "社交媒体",
  "user_input": "用户补充",
  "model_inference": "模型推断",
  "other": "其他"
}
```

注意：  
`model_inference` 最好只用于风险摘要等弱推断，不建议当作强证据源。

---

# 二、评分规则表

下面这部分建议你们做成：

- 一份**规则说明文档**
- 一份**代码中的评分配置**
- 一份**Prompt 口径说明**

这样模型输出与规则引擎更容易对齐。

---

# 三、评分框架建议

MVP 建议拆成 3 层：

1. **客户匹配度（Fit）**
2. **商机热度（Opportunity）**
3. **跟进优先级（Priority）**

它们不是一回事：

- **Fit 高**：说明像目标客户
- **Opportunity 高**：说明现在可能有窗口
- **Priority 高**：说明值得当前投入资源

---

# 四、评分维度总览

建议总分 100 分，由 4 个一级维度组成：

```json
{
  "icp_fit_score": 35,
  "demand_signal_score": 35,
  "engagement_feasibility_score": 15,
  "risk_penalty_score": 15
}
```

其中：
- 前三项是加分项
- 最后一项是扣分项

最终分数建议公式：

```text
total_score = icp_fit_score + demand_signal_score + engagement_feasibility_score - risk_penalty_score
```

再做边界处理：

```text
if total_score < 0 then total_score = 0
if total_score > 100 then total_score = 100
```

---

# 五、一级评分规则表

---

## 1）ICP 匹配度评分 `icp_fit_score`（0-35分）

用于判断该企业是否接近理想客户画像。

### 1.1 评分子项

| 子项 | 分值 | 说明 |
|---|---:|---|
| 行业匹配 | 0-12 | 是否属于目标行业或相邻行业 |
| 企业规模匹配 | 0-8 | 员工规模、组织复杂度是否适配 |
| 业务场景匹配 | 0-10 | 是否存在我方产品对应场景 |
| 企业类型匹配 | 0-5 | 是否适合当前销售模式 |

---

### 1.2 详细规则

#### A. 行业匹配 `0-12`

| 条件 | 分值 |
|---|---:|
| 明确属于核心目标行业 | 12 |
| 属于相邻可拓展行业 | 8 |
| 行业关联弱但可能可做 | 4 |
| 明显不匹配 | 0 |

---

#### B. 企业规模匹配 `0-8`

| 条件 | 分值 |
|---|---:|
| 完全符合目标规模带 | 8 |
| 略大或略小，但仍可服务 | 5 |
| 偏差明显，但理论可做 | 2 |
| 明显不适配 | 0 |

---

#### C. 业务场景匹配 `0-10`

| 条件 | 分值 |
|---|---:|
| 明确存在核心业务场景 | 10 |
| 存在部分可切入场景 | 6 |
| 场景模糊，仅弱相关 | 3 |
| 无明显适配场景 | 0 |

---

#### D. 企业类型匹配 `0-5`

| 条件 | 分值 |
|---|---:|
| 与我方销售模式高度适配 | 5 |
| 存在一定适配性 | 3 |
| 流程复杂或成交门槛高 | 1 |
| 基本不适配 | 0 |

例如：
- 你卖标准化 SaaS，民营成长型企业可能高分
- 政府/超大型央企若你没有对应交付能力，可能低分

---

### 1.3 客户匹配等级映射

| 分数区间 | customer_fit_level |
|---|---|
| 26-35 | high |
| 15-25 | medium |
| 0-14 | low |

---

## 2）需求信号评分 `demand_signal_score`（0-35分）

用于判断现在是否存在可推进的窗口。

### 2.1 评分子项

| 子项 | 分值 | 说明 |
|---|---:|---|
| 近期动态数量与新鲜度 | 0-10 | 最近 3-6 个月是否有变化 |
| 信号强度 | 0-15 | 是否直接指向采购/建设需求 |
| 多信号一致性 | 0-10 | 是否多个来源互相印证 |

---

### 2.2 详细规则

#### A. 动态新鲜度 `0-10`

| 条件 | 分值 |
|---|---:|
| 近 3 个月有强相关动态 | 10 |
| 近 6 个月有相关动态 | 7 |
| 近 12 个月有较弱动态 | 4 |
| 无有效近期动态 | 0 |

---

#### B. 信号强度 `0-15`

| 条件 | 分值 |
|---|---:|
| 有直接需求信号，如招聘 CRM/数字化/销售运营负责人、采购公告、系统建设公告 | 15 |
| 有较强间接信号，如扩张、管理升级、融资后组织扩充 | 10 |
| 有弱信号，如泛新闻、品牌宣传 | 5 |
| 几乎无信号 | 0 |

---

#### C. 多信号一致性 `0-10`

| 条件 | 分值 |
|---|---:|
| 3个及以上不同来源互相印证 | 10 |
| 2个来源相互支持 | 6 |
| 仅单一来源 | 3 |
| 没有可靠证据链 | 0 |

---

### 2.3 商机等级映射

| 分数区间 | opportunity_level |
|---|---|
| 26-35 | high |
| 15-25 | medium |
| 0-14 | low |

---

## 3）可触达与推进可行性评分 `engagement_feasibility_score`（0-15分）

这个维度容易被忽略，但很重要。  
因为“有需求”不等于“好推进”。

### 3.1 评分子项

| 子项 | 分值 | 说明 |
|---|---:|---|
| 目标角色清晰度 | 0-5 | 是否知道找谁 |
| 切入场景清晰度 | 0-5 | 是否知道聊什么 |
| 组织路径可推断性 | 0-5 | 是否能大致判断决策链 |

---

### 3.2 详细规则

#### A. 目标角色清晰度 `0-5`

| 条件 | 分值 |
|---|---:|
| 明确知道优先接触角色 | 5 |
| 可推断 1-2 个关键角色 | 3 |
| 角色模糊 | 1 |
| 基本无法判断 | 0 |

#### B. 切入场景清晰度 `0-5`

| 条件 | 分值 |
|---|---:|
| 有非常明确的业务切入点 | 5 |
| 有可讨论的通用场景 | 3 |
| 场景比较泛 | 1 |
| 没有清晰切入点 | 0 |

#### C. 组织路径可推断性 `0-5`

| 条件 | 分值 |
|---|---:|
| 可判断主要决策链 | 5 |
| 只能判断部分参与部门 | 3 |
| 组织结构不清晰 | 1 |
| 完全无法判断 | 0 |

---

## 4）风险扣分 `risk_penalty_score`（0-15分）

建议**只扣分，不加分**。  
避免“负面信息越多模型越兴奋”的问题。

### 4.1 扣分规则

| 风险等级 | 单项扣分 |
|---|---:|
| high | 5 |
| medium | 3 |
| low | 1 |

### 4.2 风险上限
- 所有风险累计扣分，但总扣分**最多 15 分**

### 4.3 风险类型建议权重修正

如果你想更细，可以在同样 high/medium/low 基础上增加风险类型权重。

#### 高影响风险类型
- `legal`
- `compliance`
- `financial`

建议：
- high = 5
- medium = 4
- low = 2

#### 中影响风险类型
- `procurement_complexity`
- `organization_instability`
- `long_decision_cycle`

建议：
- high = 4
- medium = 3
- low = 1

#### 低到中影响风险类型
- `unclear_demand`
- `low_budget_probability`
- `reputation`
- `other`

建议：
- high = 3
- medium = 2
- low = 1

如果 MVP 想简单一点，就统一按 `5/3/1` 扣分即可。

---

# 六、总分与最终分级映射

---

## 1）总分区间映射

| 总分 | 建议 follow_up_priority |
|---|---|
| 75-100 | P1 |
| 55-74 | P2 |
| 35-54 | P3 |
| 0-34 | discard |

---

## 2）总分解释建议

| 分数段 | 含义 |
|---|---|
| 75-100 | 高匹配且近期窗口明确，值得优先投入 |
| 55-74 | 有一定匹配度和商机，适合进入跟进池 |
| 35-54 | 信息有限或信号较弱，建议观察或轻触达 |
| 0-34 | 不适合当前投入资源 |

---

# 七、推荐的“规则优先于总分”的兜底逻辑

MVP 一定要加**兜底规则**，否则会出现一些“总分还可以但实际上不该跟”的情况。

---

## 1）直接 `discard` 条件

满足任一条，可直接判定：

```json
[
  "customer_fit_level = low 且 opportunity_level = low",
  "存在 high 级 financial/legal/compliance 风险且无明确业务机会",
  "企业类型明显不适配当前产品交付方式",
  "信息极度不足，无法识别行业、规模和场景"
]
```

---

## 2）直接升为 `P1` 条件

满足任一条，可优先进入 P1 候选：

```json
[
  "customer_fit_level = high 且 opportunity_level = high",
  "近3个月内存在明确数字化/采购/招聘相关强信号，且场景与产品高度匹配",
  "已有多个来源共同证明企业正在进行组织扩张或系统建设"
]
```

---

## 3）降级规则

即使总分高，也建议降级到 `P2` 或 `P3` 的情况：

```json
[
  "采购链明显复杂，且当前无法识别关键角色",
  "需求信号较强，但预算/时机不明",
  "企业确有需求，但已高度怀疑被现有成熟系统锁定",
  "风险扣分较高（>=10）"
]
```

---

# 八、推荐的程序化评分配置

下面给你一个适合后端落地的 JSON 配置样例。

---

## 1）评分配置 JSON

```json
{
  "score_config": {
    "dimensions": {
      "icp_fit_score": {
        "max": 35,
        "items": {
          "industry_match": {
            "max": 12,
            "rules": {
              "core_target_industry": 12,
              "adjacent_industry": 8,
              "weak_related_industry": 4,
              "not_matched": 0
            }
          },
          "company_size_match": {
            "max": 8,
            "rules": {
              "ideal": 8,
              "acceptable": 5,
              "weak": 2,
              "not_matched": 0
            }
          },
          "business_scenario_match": {
            "max": 10,
            "rules": {
              "clear_core_scenario": 10,
              "partial_scenario": 6,
              "weak_scenario": 3,
              "no_scenario": 0
            }
          },
          "company_type_match": {
            "max": 5,
            "rules": {
              "highly_matched": 5,
              "partially_matched": 3,
              "complex_but_possible": 1,
              "not_matched": 0
            }
          }
        }
      },
      "demand_signal_score": {
        "max": 35,
        "items": {
          "recency": {
            "max": 10,
            "rules": {
              "within_3_months_strong": 10,
              "within_6_months_relevant": 7,
              "within_12_months_weak": 4,
              "none": 0
            }
          },
          "signal_strength": {
            "max": 15,
            "rules": {
              "direct_procurement_or_build_signal": 15,
              "strong_indirect_signal": 10,
              "weak_signal": 5,
              "none": 0
            }
          },
          "multi_source_consistency": {
            "max": 10,
            "rules": {
              "three_or_more_sources": 10,
              "two_sources": 6,
              "single_source": 3,
              "no_reliable_chain": 0
            }
          }
        }
      },
      "engagement_feasibility_score": {
        "max": 15,
        "items": {
          "target_role_clarity": {
            "max": 5,
            "rules": {
              "clear": 5,
              "inferable": 3,
              "vague": 1,
              "unknown": 0
            }
          },
          "entry_point_clarity": {
            "max": 5,
            "rules": {
              "clear": 5,
              "general": 3,
              "weak": 1,
              "none": 0
            }
          },
          "decision_path_clarity": {
            "max": 5,
            "rules": {
              "clear": 5,
              "partial": 3,
              "weak": 1,
              "unknown": 0
            }
          }
        }
      },
      "risk_penalty_score": {
        "max": 15,
        "rules": {
          "default": {
            "high": 5,
            "medium": 3,
            "low": 1
          },
          "weighted_types": {
            "legal": {
              "high": 5,
              "medium": 4,
              "low": 2
            },
            "compliance": {
              "high": 5,
              "medium": 4,
              "low": 2
            },
            "financial": {
              "high": 5,
              "medium": 4,
              "low": 2
            },
            "procurement_complexity": {
              "high": 4,
              "medium": 3,
              "low": 1
            },
            "organization_instability": {
              "high": 4,
              "medium": 3,
              "low": 1
            },
            "long_decision_cycle": {
              "high": 4,
              "medium": 3,
              "low": 1
            },
            "unclear_demand": {
              "high": 3,
              "medium": 2,
              "low": 1
            },
            "low_budget_probability": {
              "high": 3,
              "medium": 2,
              "low": 1
            },
            "reputation": {
              "high": 3,
              "medium": 2,
              "low": 1
            },
            "other": {
              "high": 3,
              "medium": 2,
              "low": 1
            }
          }
        }
      }
    },
    "mapping": {
      "customer_fit_level": {
        "high": [26, 35],
        "medium": [15, 25],
        "low": [0, 14]
      },
      "opportunity_level": {
        "high": [26, 35],
        "medium": [15, 25],
        "low": [0, 14]
      },
      "follow_up_priority": {
        "P1": [75, 100],
        "P2": [55, 74],
        "P3": [35, 54],
        "discard": [0, 34]
      }
    },
    "override_rules": {
      "force_discard": [
        "fit_low_and_opportunity_low",
        "high_critical_risk_without_clear_opportunity",
        "delivery_model_not_matched",
        "insufficient_information"
      ],
      "force_p1_candidates": [
        "fit_high_and_opportunity_high",
        "strong_signal_within_3_months",
        "multi_source_building_or_expansion_signal"
      ],
      "downgrade_conditions": [
        "risk_penalty_gte_10",
        "unclear_budget_or_timing",
        "complex_procurement_without_key_roles",
        "locked_by_existing_system"
      ]
    }
  }
}
```

---

# 九、推荐新增一个“评分明细”结构

为了便于可解释性，我强烈建议你在 Schema 里新增一个字段，例如：

```json
{
  "scoring_details": {
    "icp_fit_score": 28,
    "demand_signal_score": 26,
    "engagement_feasibility_score": 11,
    "risk_penalty_score": 6,
    "total_score": 59,
    "score_reasons": [
      "企业属于目标行业，行业匹配度较高",
      "近期存在招聘销售运营岗位信号",
      "可推断销售负责人和销售运营负责人为潜在切入角色",
      "决策链可能跨部门，存在一定推进难度"
    ]
  }
}
```

如果你愿意，可以把它加入上一版大 Schema：

---

## 可追加字段 Schema

```json
{
  "scoring_details": {
    "type": "object",
    "required": [
      "icp_fit_score",
      "demand_signal_score",
      "engagement_feasibility_score",
      "risk_penalty_score",
      "total_score",
      "score_reasons"
    ],
    "properties": {
      "icp_fit_score": {
        "type": "number",
        "minimum": 0,
        "maximum": 35
      },
      "demand_signal_score": {
        "type": "number",
        "minimum": 0,
        "maximum": 35
      },
      "engagement_feasibility_score": {
        "type": "number",
        "minimum": 0,
        "maximum": 15
      },
      "risk_penalty_score": {
        "type": "number",
        "minimum": 0,
        "maximum": 15
      },
      "total_score": {
        "type": "number",
        "minimum": 0,
        "maximum": 100
      },
      "score_reasons": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "additionalProperties": false
  }
}
```

---

# 十、开发落地建议

---

## 1）让模型“产出候选”，让规则引擎“做最终分数”
最稳的方式是：

- LLM 输出：
  - 事实
  - 信号
  - 风险
  - 推荐角色
  - 评分理由候选
- 规则引擎计算：
  - `customer_fit_level`
  - `opportunity_level`
  - `follow_up_priority`
  - `total_score`

这样比纯模型端到端更稳定。

---

## 2）枚举值要“中英双轨”
建议内部存 code，前端展示 label：

例如：

```json
{
  "risk_type": "long_decision_cycle",
  "risk_type_label": "决策周期长"
}
```

如果不想冗余，就只存 code，前端映射。

---

## 3）给 LLM 的 Prompt 中要显式限制 enum
例如明确写：

```text
risk_type 只能从以下值中选择：
legal, compliance, financial, reputation, procurement_complexity, organization_instability, low_budget_probability, unclear_demand, long_decision_cycle, other
```

否则模型会自己发明字段。

---

## 4）评分时优先看“最近 3-6 个月”
背调不是百科，销售最关心的是现在有没有窗口。

---

# 十一、建议你下一步补的内容

如果你已经准备进入开发，我建议下一步最值得补的是下面 3 个东西：

1. **最终版 API 出入参定义**
2. **带 scoring_details 的完整 Schema v2**
3. **一套可直接用于 LLM function calling / structured output 的精简字段定义**

---

如果你愿意，我下一步可以直接继续给你这三份中的任意一份，尤其我建议我直接继续给你：

## **企业背调智能体 MVP v2 完整 Schema（含 scoring_details）**
以及  
## **后端 API 请求/响应示例**

这样你基本就可以直接进入联调。