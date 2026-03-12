Q:

请直接提供企业背调智能体 MVP 的 JSON Schema 以及三个核心 Prompt 模板。

GPT-5.4:

# 企业背调智能体 MVP  
## JSON Schema + 三个核心 Prompt 模板

下面我直接给你一套**可落地开发**的版本，目标是：

- 可以做 **MVP 后端字段定义**
- 可以直接拿去做 **LLM 输出约束**
- 可以作为 **前端展示数据结构**
- 可以支持后续扩展到评分、CRM、工作流

---

# 一、MVP 总体设计原则

这版 Schema 按 4 个原则设计：

1. **先够用，不追求过度复杂**
2. **事实、推断、建议分层**
3. **保留来源，方便追溯**
4. **兼容人工补录和自动采集**

---

# 二、MVP JSON Schema

下面给你一版推荐的 **Draft 2020-12 风格 JSON Schema**。  
如果你们工程里不严格校验 Draft 版本，也可以把它当成“结构规范”直接使用。

---

## 1）完整 JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/company-due-diligence-mvp.schema.json",
  "title": "Company Due Diligence Agent MVP Output",
  "type": "object",
  "required": [
    "meta",
    "input",
    "company_profile",
    "recent_developments",
    "demand_signals",
    "organization_insights",
    "risk_signals",
    "sales_assessment",
    "communication_strategy",
    "evidence_references"
  ],
  "properties": {
    "meta": {
      "type": "object",
      "required": [
        "report_id",
        "generated_at",
        "language",
        "version"
      ],
      "properties": {
        "report_id": {
          "type": "string",
          "description": "报告唯一ID"
        },
        "generated_at": {
          "type": "string",
          "format": "date-time",
          "description": "生成时间"
        },
        "language": {
          "type": "string",
          "enum": ["zh-CN", "en-US"],
          "description": "输出语言"
        },
        "version": {
          "type": "string",
          "description": "Schema或Prompt版本"
        }
      },
      "additionalProperties": false
    },
    "input": {
      "type": "object",
      "required": [
        "company_name",
        "user_company_product",
        "sales_goal"
      ],
      "properties": {
        "company_name": {
          "type": "string",
          "description": "目标企业名称"
        },
        "company_website": {
          "type": "string",
          "description": "目标企业官网"
        },
        "user_company_product": {
          "type": "string",
          "description": "我方产品/服务描述"
        },
        "user_target_customer_profile": {
          "type": "string",
          "description": "我方理想客户画像"
        },
        "sales_goal": {
          "type": "string",
          "enum": [
            "lead_generation",
            "first_touch",
            "meeting_prep",
            "solution_pitch",
            "account_planning",
            "other"
          ],
          "description": "本次跟进目标"
        },
        "target_role": {
          "type": "string",
          "description": "用户希望接触的角色"
        },
        "extra_context": {
          "type": "string",
          "description": "用户补充背景"
        }
      },
      "additionalProperties": false
    },
    "company_profile": {
      "type": "object",
      "required": [
        "company_name",
        "industry",
        "company_type",
        "business_scope",
        "main_products_or_services",
        "estimated_size"
      ],
      "properties": {
        "company_name": {
          "type": "string"
        },
        "short_name": {
          "type": "string"
        },
        "industry": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "行业标签"
        },
        "company_type": {
          "type": "string",
          "description": "企业类型，如民营/国企/外企/上市公司/子公司等"
        },
        "founded_year": {
          "type": ["integer", "null"],
          "minimum": 1800,
          "maximum": 2100
        },
        "headquarters": {
          "type": "string"
        },
        "business_scope": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "主营业务范围"
        },
        "main_products_or_services": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "estimated_size": {
          "type": "string",
          "description": "员工规模或规模估计"
        },
        "region_coverage": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "official_website": {
          "type": "string"
        },
        "official_accounts": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "profile_summary": {
          "type": "string",
          "description": "企业画像摘要"
        }
      },
      "additionalProperties": false
    },
    "recent_developments": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "date",
          "type",
          "title",
          "summary",
          "source",
          "confidence"
        ],
        "properties": {
          "date": {
            "type": "string",
            "description": "事件日期，建议 YYYY-MM-DD，未知可写 YYYY-MM 或 YYYY"
          },
          "type": {
            "type": "string",
            "enum": [
              "news",
              "financing",
              "hiring",
              "expansion",
              "new_product",
              "bidding",
              "partnership",
              "digital_transformation",
              "management_change",
              "compliance",
              "other"
            ]
          },
          "title": {
            "type": "string"
          },
          "summary": {
            "type": "string"
          },
          "source": {
            "type": "string"
          },
          "source_ref_ids": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        },
        "additionalProperties": false
      }
    },
    "demand_signals": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "signal_type",
          "signal",
          "evidence",
          "inference",
          "strength"
        ],
        "properties": {
          "signal_type": {
            "type": "string",
            "enum": [
              "recruitment_signal",
              "expansion_signal",
              "digitalization_signal",
              "growth_signal",
              "management_signal",
              "cost_reduction_signal",
              "compliance_signal",
              "customer_operation_signal",
              "sales_management_signal",
              "data_governance_signal",
              "other"
            ]
          },
          "signal": {
            "type": "string",
            "description": "观察到的客观信号"
          },
          "evidence": {
            "type": "string",
            "description": "支撑该信号的证据摘要"
          },
          "inference": {
            "type": "string",
            "description": "基于事实得出的商务推断"
          },
          "strength": {
            "type": "string",
            "enum": ["high", "medium", "low"]
          },
          "source": {
            "type": "string"
          },
          "source_ref_ids": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "date": {
            "type": "string"
          }
        },
        "additionalProperties": false
      }
    },
    "organization_insights": {
      "type": "object",
      "required": [
        "possible_target_departments",
        "recommended_target_roles"
      ],
      "properties": {
        "possible_target_departments": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "recommended_target_roles": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "role",
              "reason",
              "priority"
            ],
            "properties": {
              "role": {
                "type": "string"
              },
              "department": {
                "type": "string"
              },
              "reason": {
                "type": "string"
              },
              "priority": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10
              }
            },
            "additionalProperties": false
          }
        },
        "possible_decision_chain": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "key_people_public_info": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string"
              },
              "role": {
                "type": "string"
              },
              "public_context": {
                "type": "string"
              },
              "source_ref_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            },
            "required": ["name", "role"],
            "additionalProperties": false
          }
        }
      },
      "additionalProperties": false
    },
    "risk_signals": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "risk_type",
          "risk",
          "description",
          "impact",
          "level"
        ],
        "properties": {
          "risk_type": {
            "type": "string",
            "enum": [
              "legal",
              "compliance",
              "financial",
              "reputation",
              "procurement_complexity",
              "organization_instability",
              "low_budget_probability",
              "unclear_demand",
              "long_decision_cycle",
              "other"
            ]
          },
          "risk": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "impact": {
            "type": "string"
          },
          "level": {
            "type": "string",
            "enum": ["high", "medium", "low"]
          },
          "source": {
            "type": "string"
          },
          "source_ref_ids": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "date": {
            "type": "string"
          }
        },
        "additionalProperties": false
      }
    },
    "sales_assessment": {
      "type": "object",
      "required": [
        "customer_fit_level",
        "opportunity_level",
        "follow_up_priority",
        "core_opportunity_scenarios",
        "main_obstacles",
        "assessment_summary"
      ],
      "properties": {
        "customer_fit_level": {
          "type": "string",
          "enum": ["high", "medium", "low"]
        },
        "opportunity_level": {
          "type": "string",
          "enum": ["high", "medium", "low"]
        },
        "follow_up_priority": {
          "type": "string",
          "enum": ["P1", "P2", "P3", "discard"]
        },
        "core_opportunity_scenarios": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "main_obstacles": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "assessment_summary": {
          "type": "string"
        },
        "should_follow_up": {
          "type": "boolean"
        }
      },
      "additionalProperties": false
    },
    "communication_strategy": {
      "type": "object",
      "required": [
        "recommended_entry_points",
        "avoid_points",
        "opening_message",
        "phone_script",
        "wechat_message",
        "email_message",
        "next_step_suggestion"
      ],
      "properties": {
        "recommended_entry_points": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "avoid_points": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "opening_message": {
          "type": "string",
          "description": "一句话破冰建议"
        },
        "phone_script": {
          "type": "string"
        },
        "wechat_message": {
          "type": "string"
        },
        "email_message": {
          "type": "string"
        },
        "next_step_suggestion": {
          "type": "string"
        }
      },
      "additionalProperties": false
    },
    "evidence_references": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "reference_id",
          "source",
          "title"
        ],
        "properties": {
          "reference_id": {
            "type": "string"
          },
          "source": {
            "type": "string",
            "description": "来源类型，如官网/新闻/招聘/用户补充"
          },
          "title": {
            "type": "string"
          },
          "url": {
            "type": "string"
          },
          "date": {
            "type": "string"
          },
          "excerpt": {
            "type": "string"
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

---

# 三、推荐的最小输出样例

这个样例非常适合你拿去做联调测试。

```json
{
  "meta": {
    "report_id": "dd_20260312_001",
    "generated_at": "2026-03-12T10:30:00Z",
    "language": "zh-CN",
    "version": "mvp_v1"
  },
  "input": {
    "company_name": "某科技有限公司",
    "company_website": "https://www.example.com",
    "user_company_product": "我们提供面向中大型企业的CRM和销售运营管理系统",
    "user_target_customer_profile": "快速增长、销售团队扩张、客户管理流程复杂的企业",
    "sales_goal": "first_touch",
    "target_role": "销售负责人",
    "extra_context": "优先切销售管理和线索转化场景"
  },
  "company_profile": {
    "company_name": "某科技有限公司",
    "short_name": "某科技",
    "industry": ["企业服务", "软件", "数字化"],
    "company_type": "民营企业",
    "founded_year": 2018,
    "headquarters": "上海",
    "business_scope": ["企业数字化解决方案", "SaaS产品研发"],
    "main_products_or_services": ["企业协同平台", "数据分析工具"],
    "estimated_size": "200-500人",
    "region_coverage": ["华东", "全国"],
    "official_website": "https://www.example.com",
    "official_accounts": ["微信公众号：某科技"],
    "profile_summary": "一家面向企业客户提供数字化产品和解决方案的成长型科技公司。"
  },
  "recent_developments": [
    {
      "date": "2026-01-18",
      "type": "hiring",
      "title": "招聘销售运营经理",
      "summary": "公开招聘销售运营经理，职责涉及销售流程优化、CRM管理和数据分析。",
      "source": "招聘信息",
      "source_ref_ids": ["ref_001"],
      "confidence": 0.91
    },
    {
      "date": "2025-12-20",
      "type": "expansion",
      "title": "拓展华南市场",
      "summary": "公司宣布进一步拓展华南区域业务布局。",
      "source": "新闻稿",
      "source_ref_ids": ["ref_002"],
      "confidence": 0.84
    }
  ],
  "demand_signals": [
    {
      "signal_type": "sales_management_signal",
      "signal": "公司正在招聘销售运营相关岗位",
      "evidence": "招聘职责明确提到销售流程优化、CRM管理和数据分析",
      "inference": "公司可能正在加强销售管理体系建设，对CRM和销售运营工具存在潜在需求",
      "strength": "high",
      "source": "招聘信息",
      "source_ref_ids": ["ref_001"],
      "date": "2026-01-18"
    },
    {
      "signal_type": "expansion_signal",
      "signal": "企业拓展新区域市场",
      "evidence": "新闻稿提到华南区域业务扩张",
      "inference": "随着跨区域业务拓展，线索分配、客户跟进和销售协同复杂度上升",
      "strength": "medium",
      "source": "新闻稿",
      "source_ref_ids": ["ref_002"],
      "date": "2025-12-20"
    }
  ],
  "organization_insights": {
    "possible_target_departments": ["销售部", "销售运营", "信息化部门"],
    "recommended_target_roles": [
      {
        "role": "销售负责人",
        "department": "销售部",
        "reason": "更关注销售流程、团队管理和业绩提升",
        "priority": 1
      },
      {
        "role": "销售运营负责人",
        "department": "销售运营",
        "reason": "与CRM落地、数据管理和流程标准化高度相关",
        "priority": 2
      }
    ],
    "possible_decision_chain": ["业务负责人提出需求", "销售运营评估方案", "管理层审批预算", "信息化协同落地"],
    "key_people_public_info": []
  },
  "risk_signals": [
    {
      "risk_type": "long_decision_cycle",
      "risk": "可能存在跨部门决策链",
      "description": "如果CRM涉及销售、运营和IT协同，决策流程可能较长",
      "impact": "项目推进周期可能拉长，需要多角色沟通",
      "level": "medium",
      "source": "模型推断",
      "source_ref_ids": [],
      "date": "2026-03-12"
    }
  ],
  "sales_assessment": {
    "customer_fit_level": "high",
    "opportunity_level": "high",
    "follow_up_priority": "P1",
    "core_opportunity_scenarios": [
      "销售流程标准化",
      "CRM管理升级",
      "线索与客户跟进协同",
      "销售数据分析"
    ],
    "main_obstacles": [
      "可能已有现有系统",
      "决策涉及多部门"
    ],
    "assessment_summary": "该企业存在明显销售管理与区域扩张信号，较符合CRM产品的目标客户画像，建议优先跟进。",
    "should_follow_up": true
  },
  "communication_strategy": {
    "recommended_entry_points": [
      "销售流程标准化",
      "跨区域团队协同",
      "线索到商机转化效率"
    ],
    "avoid_points": [
      "一开始过度强调系统功能",
      "直接推大而全的平台替换"
    ],
    "opening_message": "注意到贵司近期在拓展区域业务，同时也在招聘销售运营岗位，说明销售体系建设可能正在加速。",
    "phone_script": "您好，我们关注到贵司近期在销售运营和区域拓展上动作比较明显。很多类似阶段的企业会开始遇到销售流程不统一、客户跟进协同难和数据不透明的问题。我们这边主要帮助企业优化CRM和销售管理流程，想看看是否有机会交流一下你们当前在这块的管理重点。",
    "wechat_message": "您好，看到贵司近期在拓展区域业务，也在招销售运营相关岗位。很多成长型企业在这个阶段会开始关注销售流程标准化、客户跟进协同和数据分析效率。我们这边在CRM和销售运营管理方面有一些实践，若方便的话想跟您交流下是否有可借鉴的地方。",
    "email_message": "您好，关注到贵司近期在业务扩张及销售运营建设方面有较多动作。对于成长型企业而言，这通常意味着销售流程标准化、客户管理协同及数据分析能力的重要性提升。我们团队长期服务于类似阶段企业，帮助其优化CRM和销售管理机制。如果您愿意，我可以基于贵司当前发展阶段提供一个简短的交流建议。",
    "next_step_suggestion": "优先联系销售负责人或销售运营负责人，围绕销售流程标准化与区域拓张协同问题发起首次交流。"
  },
  "evidence_references": [
    {
      "reference_id": "ref_001",
      "source": "招聘信息",
      "title": "销售运营经理招聘",
      "url": "https://example.com/job/1",
      "date": "2026-01-18",
      "excerpt": "负责销售流程优化、CRM管理、销售数据分析。"
    },
    {
      "reference_id": "ref_002",
      "source": "新闻稿",
      "title": "某科技拓展华南市场",
      "url": "https://example.com/news/1",
      "date": "2025-12-20",
      "excerpt": "公司进一步拓展华南区域业务布局。"
    }
  ]
}
```

---

# 四、字段设计建议：工程落地版

这里补充几个非常关键的工程建议。

---

## 1）事实和推断一定要分开

比如：

- `recent_developments` = 事实层
- `demand_signals` = 信号层
- `sales_assessment` = 判断层
- `communication_strategy` = 行动层

这会大幅降低“AI胡说”的风险。

---

## 2）所有重要结论尽量挂 `source_ref_ids`

这样你后面做前端时可以实现：

- 点击“需求信号”
- 展开“依据来源”
- 展示对应文章/招聘/官网摘录

这对用户信任感很重要。

---

## 3）MVP 不强求每个字段都填满

有些企业公开信息少，所以建议你的程序允许：

- 空数组 `[]`
- 空字符串 `""`
- 少量 `null`

但是**结构必须稳定**。

---

# 五、三个核心 Prompt 模板

下面我给你三套可以直接使用的 Prompt：

1. **信息抽取 Prompt**
2. **商务分析 Prompt**
3. **话术生成 Prompt**

我会按实际开发习惯写成：

- System Prompt
- User Prompt Template
- 输出要求

你们可以直接放到工作流里。

---

# Prompt 1：企业信息抽取 Prompt

## 用途
把原始资料抽取为结构化信息，重点生成：

- `company_profile`
- `recent_developments`
- `risk_signals`
- `evidence_references`

---

## 1.1 System Prompt

```text
你是一个企业公开信息抽取助手。你的任务是从用户提供的企业原始材料中，提取“客观事实信息”，并输出为严格的 JSON。

要求：
1. 只根据提供的材料提取，不要臆测没有依据的事实。
2. 信息不足时，使用空字符串、空数组或 null，不要编造。
3. 优先提取客观、可验证、可追溯的信息。
4. 将不同来源整理为 evidence_references，并给每条信息尽量关联 source_ref_ids。
5. recent_developments 只保留相对重要、与商务跟进相关的动态。
6. risk_signals 中仅保留可以从材料中直接看到的风险，或基于材料做出的非常弱推断；不要输出夸张结论。
7. 输出必须是合法 JSON，不要输出任何 JSON 之外的解释。
8. 如果用户材料中存在互相冲突的信息，保留较新来源，或在 summary 中简要体现不确定性。
```

---

## 1.2 User Prompt Template

```text
请根据以下输入，抽取企业公开信息并输出 JSON。

【目标企业】
{{company_name}}

【官网】
{{company_website}}

【原始材料】
{{raw_documents}}

原始材料可能包含以下内容：
- 官网介绍
- 新闻稿
- 招聘信息
- 公众号文章
- 工商/公开登记信息
- 用户手工补充文本

请输出以下 JSON 结构，不要增加额外字段：

{
  "company_profile": {
    "company_name": "",
    "short_name": "",
    "industry": [],
    "company_type": "",
    "founded_year": null,
    "headquarters": "",
    "business_scope": [],
    "main_products_or_services": [],
    "estimated_size": "",
    "region_coverage": [],
    "official_website": "",
    "official_accounts": [],
    "profile_summary": ""
  },
  "recent_developments": [
    {
      "date": "",
      "type": "",
      "title": "",
      "summary": "",
      "source": "",
      "source_ref_ids": [],
      "confidence": 0
    }
  ],
  "risk_signals": [
    {
      "risk_type": "",
      "risk": "",
      "description": "",
      "impact": "",
      "level": "",
      "source": "",
      "source_ref_ids": [],
      "date": ""
    }
  ],
  "evidence_references": [
    {
      "reference_id": "",
      "source": "",
      "title": "",
      "url": "",
      "date": "",
      "excerpt": ""
    }
  ]
}
```

---

## 1.3 使用建议

### 输入 `raw_documents` 推荐格式
建议你把原始材料整理成这种结构喂给模型：

```text
[Doc 1]
source: 官网
title: 公司介绍
url: https://xxx.com/about
date: 2026-03-01
content: ...

[Doc 2]
source: 招聘信息
title: 销售运营经理
url: https://xxx.com/jobs/123
date: 2026-01-18
content: ...

[Doc 3]
source: 新闻稿
title: 完成A轮融资
url: https://xxx.com/news/888
date: 2025-12-10
content: ...
```

这样模型更容易输出 `reference_id` 映射关系。

---

# Prompt 2：商务分析 Prompt

## 用途
基于输入信息和我方销售目标，输出：

- `demand_signals`
- `organization_insights`
- `sales_assessment`

---

## 2.1 System Prompt

```text
你是一个ToB商务分析助手。你的任务是基于企业基础信息、近期动态、我方产品信息和销售目标，做“潜在商机判断”。

要求：
1. 必须区分“事实”和“推断”。
2. demand_signals 中：
   - signal = 事实信号
   - evidence = 支撑证据
   - inference = 商务推断
3. 不要因为信息少就过度乐观，也不要无依据判定为高商机。
4. recommended_target_roles 必须围绕“谁最可能对该场景负责”来推荐。
5. sales_assessment 必须综合以下因素：
   - 企业与我方ICP匹配度
   - 近期动态是否构成需求信号
   - 决策难度与推进风险
6. 如果证据不足，应降低机会等级，并在 assessment_summary 中明确说明。
7. 输出必须是合法 JSON，不要输出任何多余解释。
```

---

## 2.2 User Prompt Template

```text
请基于以下信息，输出企业的商务分析结果 JSON。

【我方产品/服务】
{{user_company_product}}

【我方理想客户画像】
{{user_target_customer_profile}}

【本次销售目标】
{{sales_goal}}

【希望接触角色】
{{target_role}}

【额外上下文】
{{extra_context}}

【企业结构化信息】
{{company_structured_data}}

请输出以下 JSON 结构，不要增加额外字段：

{
  "demand_signals": [
    {
      "signal_type": "",
      "signal": "",
      "evidence": "",
      "inference": "",
      "strength": "",
      "source": "",
      "source_ref_ids": [],
      "date": ""
    }
  ],
  "organization_insights": {
    "possible_target_departments": [],
    "recommended_target_roles": [
      {
        "role": "",
        "department": "",
        "reason": "",
        "priority": 1
      }
    ],
    "possible_decision_chain": [],
    "key_people_public_info": []
  },
  "sales_assessment": {
    "customer_fit_level": "",
    "opportunity_level": "",
    "follow_up_priority": "",
    "core_opportunity_scenarios": [],
    "main_obstacles": [],
    "assessment_summary": "",
    "should_follow_up": true
  }
}
```

---

## 2.3 判断口径建议

你可以在程序里加一些“隐式规则”，比如：

### `customer_fit_level`
主要看：
- 行业是否接近 ICP
- 企业规模是否适配
- 场景是否适配

### `opportunity_level`
主要看：
- 是否有近期动态
- 是否有明确信号
- 信号强度高不高

### `follow_up_priority`
可参考：
- 高匹配 + 高商机 = `P1`
- 高/中匹配 + 中商机 = `P2`
- 低商机或信息弱 = `P3`
- 明显不适合 = `discard`

---

# Prompt 3：话术生成 Prompt

## 用途
基于商务分析结果生成：

- `communication_strategy`

适用于：
- 微信
- 邮件
- 电话开场
- 下一步推进建议

---

## 3.1 System Prompt

```text
你是一个B2B销售沟通助手。你的任务是根据企业背调结果，生成“自然、克制、可执行”的首次触达策略和话术。

要求：
1. 语气要专业、简洁，不要夸张，不要像群发广告。
2. 必须围绕企业近期动态、潜在场景和目标角色来写，不要空泛推销。
3. opening_message 应为一句话破冰建议。
4. phone_script 要适合电话开场，控制在简短可说完的长度。
5. wechat_message 要适合企业微信/微信初次触达，不宜过长。
6. email_message 要适合首次商务邮件，结构清楚，避免太硬的销售感。
7. recommended_entry_points 应对应“对方可能在意的问题”。
8. avoid_points 应提示不适合的切入方式。
9. next_step_suggestion 要给出一个明确、轻量的下一步动作建议。
10. 如果证据不足，话术要更保守，避免过强结论。
11. 输出必须是合法 JSON，不要输出任何多余说明。
```

---

## 3.2 User Prompt Template

```text
请根据以下信息，输出首次触达沟通策略 JSON。

【我方产品/服务】
{{user_company_product}}

【本次销售目标】
{{sales_goal}}

【目标角色】
{{target_role}}

【企业基础画像与分析结果】
{{analysis_data}}

请输出以下 JSON 结构，不要增加额外字段：

{
  "communication_strategy": {
    "recommended_entry_points": [],
    "avoid_points": [],
    "opening_message": "",
    "phone_script": "",
    "wechat_message": "",
    "email_message": "",
    "next_step_suggestion": ""
  }
}
```

---

# 六、推荐的串联方式

你们实际调用时，建议按下面流程串起来：

---

## Step 1：原始资料抽取
使用 **Prompt 1**

输入：
- 企业名
- 官网
- 原始文档集合

输出：
- `company_profile`
- `recent_developments`
- `risk_signals`
- `evidence_references`

---

## Step 2：商务分析
使用 **Prompt 2**

输入：
- Prompt 1 输出
- 我方产品信息
- ICP
- 跟进目标

输出：
- `demand_signals`
- `organization_insights`
- `sales_assessment`

---

## Step 3：话术生成
使用 **Prompt 3**

输入：
- Prompt 2 输出
- 产品信息
- 目标角色
- 跟进目标

输出：
- `communication_strategy`

---

## Step 4：最终拼装
将三个结果组合成最终对象：

```json
{
  "meta": {},
  "input": {},
  "company_profile": {},
  "recent_developments": [],
  "demand_signals": [],
  "organization_insights": {},
  "risk_signals": [],
  "sales_assessment": {},
  "communication_strategy": {},
  "evidence_references": []
}
```

---

# 七、给你一个更适合 MVP 的“精简版 Schema”

如果你现在想更快上线，可以先用这个精简版。

## 精简版 JSON 结构

```json
{
  "company_name": "",
  "industry": [],
  "company_type": "",
  "main_business": [],
  "estimated_size": "",
  "recent_developments": [],
  "demand_signals": [],
  "recommended_roles": [],
  "risks": [],
  "follow_up_priority": "",
  "summary": "",
  "entry_points": [],
  "wechat_message": "",
  "phone_script": "",
  "email_message": "",
  "sources": []
}
```

### 适合场景
- 快速验证 MVP
- 前端只做单页结果展示
- 后端先不做复杂校验
- 先跑 10~20 个真实案例

---

# 八、落地时最容易踩的坑

---

## 1. 一个 Prompt 做到底
不建议。  
原因：抽取、判断、生成话术是三种不同任务，混在一起容易漂。

---

## 2. 不保留来源
后面用户一问“依据是什么”，你就很难解释。

---

## 3. 输出结论过满
企业公开信息经常不完整，所以系统要允许“不确定”。

---

## 4. 话术太像广告
要让话术像“有做过功课的人在交流”，而不是“万能销售模板”。

---

# 九、我建议你下一步再补的两个东西

如果你继续往下做，最值得补的是：

## 1. 字段枚举表
把所有 `type` / `risk_type` / `signal_type` / `sales_goal` 统一枚举，前后端一致。

## 2. 评分规则文档
比如：
- 什么情况是 `P1`
- 什么情况是 `high opportunity`
- 什么情况下应该 `discard`

这样输出会稳定很多。

---

如果你愿意，我下一步可以继续直接给你这两份：

1. **企业背调智能体 MVP 的字段枚举字典**
2. **企业背调智能体的评分规则表（客户匹配度 / 商机等级 / 跟进优先级）**

如果你要，我可以直接继续补成开发可用版。