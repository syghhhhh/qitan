# API 接口文档

## 基础信息

- **Base URL**: `http://127.0.0.1:8008`
- **Content-Type**: `application/json`
- **API 文档**: `http://127.0.0.1:8008/docs` (Swagger UI)

---

## 接口列表

### 1. GET /health

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

---

### 2. POST /analyze

企业背调分析接口，接收企业信息，返回完整的背调报告。

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| company_name | string | 是 | - | 目标企业名称 |
| company_website | string | 否 | null | 目标企业官网 |
| user_company_product | string | 否 | "CRM系统" | 我方产品/服务描述 |
| user_target_customer_profile | string | 否 | null | 我方理想客户画像 |
| sales_goal | string | 否 | "first_touch" | 跟进目标 |
| target_role | string | 否 | null | 用户希望接触的角色 |
| extra_context | string | 否 | null | 用户补充背景 |

#### sales_goal 枚举值

| 值 | 说明 |
|----|------|
| `lead_generation` | 线索挖掘 |
| `first_touch` | 首次触达 |
| `meeting_prep` | 会前准备 |
| `solution_pitch` | 方案推进 |
| `account_planning` | 客户经营 |
| `other` | 其他 |

#### 请求示例

```bash
curl -X POST http://127.0.0.1:8008/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "某科技有限公司",
    "user_company_product": "CRM系统",
    "sales_goal": "first_touch"
  }'
```

#### 响应结构

返回 `DueDiligenceOutput` 对象，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| meta | object | 元信息（版本、生成时间、处理耗时） |
| input | object | 输入信息快照 |
| company_profile | object | 企业画像 |
| recent_developments | array | 近期动态列表 |
| demand_signals | array | 需求信号列表 |
| organization_insights | object | 组织洞察与推荐联系人 |
| risk_signals | array | 风险提示列表 |
| sales_assessment | object | 商务判断 |
| communication_strategy | object | 沟通策略 |
| evidence_references | array | 证据来源列表 |

#### 响应示例

```json
{
  "meta": {
    "version": "1.0",
    "generated_at": "2026-03-13T10:00:00Z",
    "processing_time_seconds": 1.5
  },
  "input": {
    "company_name": "某科技有限公司",
    "user_company_product": "CRM系统",
    "sales_goal": "first_touch"
  },
  "company_profile": {
    "company_name": "某科技有限公司",
    "industry": ["信息技术", "软件开发"],
    "company_type": "民营企业",
    "estimated_size": "100-499人",
    "main_products_or_services": ["企业软件", "云计算服务"]
  },
  "recent_developments": [
    {
      "date": "2026-03-01",
      "type": "hiring",
      "title": "招聘销售运营经理",
      "summary": "正在招聘销售运营经理，负责销售流程优化..."
    }
  ],
  "demand_signals": [
    {
      "signal_type": "recruitment_signal",
      "strength": "high",
      "description": "招聘销售运营相关岗位",
      "evidence": "招聘JD显示需要CRM系统经验",
      "inference": "可能正在搭建或优化销售管理体系"
    }
  ],
  "organization_insights": {
    "recommended_target_roles": [
      {
        "role": "销售总监",
        "department": "销售部",
        "priority": "high",
        "reason": "负责销售体系搭建，对CRM有决策权"
      }
    ]
  },
  "risk_signals": [
    {
      "risk_type": "procurement_complexity",
      "severity": "medium",
      "description": "采购流程可能较长",
      "impact": "需要预留较长的跟进周期"
    }
  ],
  "sales_assessment": {
    "customer_fit_level": "high",
    "opportunity_level": "P1",
    "follow_up_priority": "P1",
    "priority_score": 82,
    "priority_reason": "行业匹配度高，近期有明确需求信号"
  },
  "communication_strategy": {
    "entry_point": {
      "angle": "销售效率提升",
      "reason": "基于招聘信号切入"
    },
    "wechat_script": "您好，看到贵司正在招聘销售运营经理...",
    "phone_script": "您好，我是XX公司的...",
    "email_script": "尊敬的销售总监，您好..."
  },
  "evidence_references": [
    {
      "claim": "正在招聘销售运营经理",
      "source_name": "招聘网站",
      "source_url": "https://xxx.com/job/123",
      "retrieved_at": "2026-03-13"
    }
  ]
}
```

#### 错误响应

| 状态码 | 错误类型 | 说明 |
|--------|---------|------|
| 400 | validation_error | 请求参数错误（如企业名称为空） |
| 500 | internal_error | 服务器内部错误 |

```json
{
  "error": "validation_error",
  "message": "企业名称不能为空",
  "detail": "company_name 字段为必填项，请提供有效的企业名称"
}
```