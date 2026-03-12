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

## 数据模型

详细的数据模型定义请参考 `discuss003.md`，评分规则请参考 `discuss004.md`。

## 开发状态

参见 `task.json` 获取当前开发进度。