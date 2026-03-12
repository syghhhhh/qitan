# CLAUDE.md - 企业背调智能体开发规范

本文档定义了项目的开发规则、任务执行流程和代码规范，用于指导 Claude Code 自动化执行开发任务。

---

## 项目概述

**项目名称**：企业背调智能体 MVP

**目标**：面向企业商务岗位，对企业进行公开信息背调，输出企业画像、需求信号、风险提示、联系人建议和沟通话术。

**技术栈**：
- Python 3.10+
- FastAPI
- Pydantic
- uv（环境管理）

**产品规划文档**：
- `discuss001.md`：项目拆解与商务背调框架
- `discuss002.md`：MVP 方案设计
- `discuss003.md`：JSON Schema + Prompt 模板
- `discuss004.md`：字段枚举字典 + 评分规则表

---

## 开发流程规则

### 任务执行流程

每个任务按以下流程执行：

```
1. 读取 task.json 获取当前任务
2. 更新任务状态为 in_progress
3. 按步骤执行任务
4. 验证执行结果
5. 更新任务状态为 completed
6. Git 提交并推送
7. 继续下一个任务
```

### 任务状态管理

任务状态存储在 `task.json` 中：
- `passes: false` - 未完成
- `passes: true` - 已完成

每完成一个任务后，必须：
1. 更新 `task.json` 中对应任务的 `passes` 字段为 `true`
2. 执行 Git 提交
3. 推送到远程仓库

### Git 提交规范

**Commit 格式**：
```
<type>: <subject>

<body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**提交时机**：
- 每完成一个 task.json 中的任务后提交
- 提交后立即推送到远程仓库

**提交流程**：
```bash
git status                           # 查看变更
git add <files>                      # 添加文件
git diff --cached --stat             # 确认暂存内容
git commit -m "..."                  # 提交
git push origin main                 # 推送
```

---

## 任务清单

### Task 1: 初始化项目目录与基础文件 ✅

**步骤**：
1. 创建 `backend/`、`frontend/`、`docs/` 目录
2. 创建 `backend/app/` 作为 FastAPI 入口
3. 创建 `backend/app/schemas/` 存放数据模型
4. 创建 `backend/app/prompts/` 存放 Prompt 模板
5. 创建 `backend/app/services/` 存放业务逻辑
6. 创建 `frontend/index.html`、`style.css`、`app.js`
7. 创建 `pyproject.toml`、`README.md`
8. 验证目录结构

**验收标准**：
- 目录结构符合要求
- 所有 `__init__.py` 文件存在
- 前端三文件存在且有内容

---

### Task 2: 使用 uv 初始化项目级 Python 环境

**步骤**：
```bash
# 检查 uv 版本
uv --version

# 创建虚拟环境
uv venv

# 验证虚拟环境创建
ls -la .venv/
```

**验收标准**：
- `.venv/` 目录存在
- 后续命令可通过 `uv run` 执行

---

### Task 3: 定义企业背调核心数据模型 Schema

**步骤**：
1. 创建 `backend/app/schemas/common.py`：
   - 定义 `Meta` 模型：report_id, generated_at, language, version
   - 定义 `Input` 模型：company_name(必填), company_website, user_company_product 等

2. 创建 `backend/app/schemas/company.py`：
   - 定义 `CompanyProfile` 模型
   - 定义 `RecentDevelopment` 模型

3. 创建 `backend/app/schemas/analysis.py`：
   - 定义 `DemandSignal` 模型
   - 定义 `RiskSignal` 模型
   - 定义 `OrganizationInsights` 模型

4. 创建 `backend/app/schemas/assessment.py`：
   - 定义 `SalesAssessment` 模型
   - 定义 `CommunicationStrategy` 模型

5. 创建 `backend/app/schemas/output.py`：
   - 定义 `EvidenceReference` 模型
   - 定义 `DueDiligenceOutput` 完整输出模型

6. 更新 `schemas/__init__.py` 导出所有模型

**参考文档**：`discuss003.md` 第37-580行的 JSON Schema

**验收标准**：
- 所有字段与 discuss003.md 一致
- 模型可通过 Pydantic 验证

---

### Task 4: 定义字段枚举字典

**步骤**：
1. 创建 `backend/app/schemas/enums.py`
2. 定义枚举类（参考 discuss004.md 第23-443行）：
   - `SalesGoalEnum`
   - `RecentDevelopmentTypeEnum`
   - `DemandSignalTypeEnum`
   - `RiskTypeEnum`
   - `StrengthEnum`
   - `CustomerFitLevelEnum`
   - `OpportunityLevelEnum`
   - `FollowUpPriorityEnum`
3. 创建枚举字典用于前端展示映射

**验收标准**：
- 所有枚举值与 discuss004.md 一致
- 枚举可被 Pydantic 模型使用

---

### Task 5: 定义评分规则配置

**步骤**：
1. 创建 `backend/app/config/scoring.py`
2. 定义评分配置（参考 discuss004.md 第450-1043行）：
   - ICP 匹配度评分（0-35分）
   - 需求信号评分（0-35分）
   - 可触达可行性评分（0-15分）
   - 风险扣分规则（0-15分）
   - 总分映射规则
   - 兜底规则

**验收标准**：
- 评分规则完整
- 配置可被后续规则引擎使用

---

### Task 6: 创建三个核心 Prompt 模板

**步骤**：
1. 创建 `backend/app/prompts/extraction.py`：
   - System Prompt（参考 discuss003.md 第824-837行）
   - User Prompt Template（参考 discuss003.md 第842-915行）

2. 创建 `backend/app/prompts/analysis.py`：
   - System Prompt（参考 discuss003.md 第964-981行）
   - User Prompt Template（参考 discuss003.md 第987-1046行）

3. 创建 `backend/app/prompts/communication.py`：
   - System Prompt（参考 discuss003.md 第1093-1107行）
   - User Prompt Template（参考 discuss003.md 第1114-1141行）

4. 创建 Prompt 渲染函数，支持 `{{variable}}` 替换

**验收标准**：
- Prompt 模板与 discuss003.md 一致
- 渲染函数正确替换变量

---

### Task 7: 使用 uv 安装后端依赖

**步骤**：
```bash
# 安装依赖
uv pip install fastapi uvicorn pydantic

# 更新 pyproject.toml
uv pip freeze > requirements.txt

# 验证导入
uv run python -c "import fastapi; import uvicorn; import pydantic; print('OK')"
```

**验收标准**：
- 依赖成功安装到 .venv
- 可正确导入 fastapi、uvicorn、pydantic

---

### Task 8: 创建 FastAPI 应用入口并启动健康检查接口

**步骤**：
1. 创建 `backend/app/main.py`：
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI(title="企业背调智能体")

   # CORS 配置
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_methods=["*"],
       allow_headers=["*"],
   )

   @app.get("/health")
   async def health():
       return {"status": "ok"}
   ```

2. 启动服务：
   ```bash
   uv run uvicorn backend.app.main:app --reload --port 8008
   ```

3. 验证：访问 http://127.0.0.1:8008/health

**验收标准**：
- 服务成功启动
- `/health` 返回 `{"status": "ok"}`

---

### Task 9: 实现标准 Mock 分析数据

**步骤**：
1. 创建 `backend/app/services/mock_analyzer.py`
2. 实现 `get_mock_analysis(company_name: str)` 函数
3. 返回完整的 `DueDiligenceOutput` 结构
4. 根据企业名称关键词返回不同 Mock 数据

**参考文档**：`discuss003.md` 第589-745行的样例

**验收标准**：
- Mock 数据结构完整
- 数据符合 Schema 定义

---

### Task 10: 实现 POST /analyze 接口

**步骤**：
1. 在 `main.py` 中添加：
   ```python
   from schemas.output import DueDiligenceOutput
   from services.mock_analyzer import get_mock_analysis

   class AnalyzeRequest(BaseModel):
       company_name: str
       company_website: str = None
       user_company_product: str = None
       # ... 其他字段

   @app.post("/analyze", response_model=DueDiligenceOutput)
   async def analyze(request: AnalyzeRequest):
       return get_mock_analysis(request.company_name)
   ```

2. 测试接口：
   ```bash
   curl -X POST http://127.0.0.1:8008/analyze \
     -H "Content-Type: application/json" \
     -d '{"company_name": "某科技有限公司"}'
   ```

**验收标准**：
- 接口正常返回
- Swagger 文档正确展示

---

### Task 11: 创建前端页面骨架

**步骤**：
1. 更新 `frontend/index.html`：页面结构已完成
2. 更新 `frontend/style.css`：样式已完成
3. 更新 `frontend/app.js`：交互逻辑已完成

**注意**：Task 1 已完成大部分前端工作，此任务验证并补充。

**验收标准**：
- 页面可正常打开
- 样式正确渲染

---

### Task 12: 实现前端请求与结果渲染

**步骤**：
1. 验证 `app.js` 中的交互逻辑
2. 测试表单提交
3. 测试结果渲染

**注意**：Task 1 已完成大部分工作，此任务验证并调试。

**验收标准**：
- 可提交表单
- 结果正确渲染到各卡片

---

### Task 13: 将前端静态页面挂载到 FastAPI 服务

**步骤**：
1. 在 `main.py` 中添加：
   ```python
   from fastapi.staticfiles import StaticFiles
   from fastapi.responses import FileResponse

   app.mount("/static", StaticFiles(directory="frontend"), name="static")

   @app.get("/")
   async def root():
       return FileResponse("frontend/index.html")
   ```

2. 重启服务验证

**验收标准**：
- http://127.0.0.1:8008/ 显示前端页面
- 静态资源正确加载

---

### Task 14: 完成端到端联调与验收

**步骤**：
1. 启动 FastAPI 服务
2. 打开浏览器访问首页
3. 输入企业名称测试
4. 验证结果展示
5. 测试边界场景

**验收标准**：
- 完整闭环可用
- 所有功能正常

---

### Task 15: 补充 README 项目说明

**步骤**：
1. 更新 `README.md`
2. 添加运行说明
3. 添加接口文档

**验收标准**：
- 文档完整准确

---

### Task 16: 创建开发文档索引

**步骤**：
1. 创建 `docs/ARCHITECTURE.md`
2. 创建 `docs/API.md`
3. 创建 `docs/SCHEMA.md`
4. 创建 `docs/SCORING.md`
5. 创建 `docs/PROMPTS.md`

**验收标准**：
- 文档与代码一致

---

## 代码规范

### Python 代码规范

- 使用 Python 3.10+ 类型注解
- 使用 Pydantic v2 定义数据模型
- 遵循 PEP 8 编码规范
- 使用 `from __future__ import annotations` 支持前向引用

### 文件命名规范

- Python 文件：小写下划线 `snake_case.py`
- 类名：大驼峰 `PascalCase`
- 函数名：小写下划线 `snake_case`
- 常量：大写下划线 `UPPER_CASE`

### 目录结构规范

```
backend/app/
├── __init__.py
├── main.py              # FastAPI 应用入口
├── schemas/             # Pydantic 数据模型
│   ├── __init__.py
│   ├── common.py        # 基础模型
│   ├── company.py       # 企业相关
│   ├── analysis.py      # 分析相关
│   ├── assessment.py    # 判断相关
│   ├── output.py        # 输出模型
│   └── enums.py         # 枚举定义
├── prompts/             # Prompt 模板
│   ├── __init__.py
│   ├── extraction.py    # 信息抽取
│   ├── analysis.py      # 商务分析
│   └── communication.py # 话术生成
├── services/            # 业务逻辑
│   ├── __init__.py
│   └── mock_analyzer.py
└── config/              # 配置文件
    ├── __init__.py
    └── scoring.py       # 评分规则
```

---

## 自动化执行指南

### 开始新任务时

1. 读取 `task.json` 找到第一个 `passes: false` 的任务
2. 按本文档定义的步骤执行
3. 完成后更新 `task.json`
4. Git 提交并推送

### 恢复中断的任务

1. 查看 `task.json` 确认当前进度
2. 检查已创建的文件
3. 继续执行未完成的步骤

### 验证任务完成

每个任务完成后必须验证：
1. 文件是否正确创建
2. 代码是否可运行
3. 功能是否符合预期

---

## 参考资源

- **产品规划**：`discuss001.md` - `discuss004.md`
- **任务清单**：`task.json`
- **FastAPI 文档**：https://fastapi.tiangolo.com/
- **Pydantic 文档**：https://docs.pydantic.dev/
- **uv 文档**：https://docs.astral.sh/uv/