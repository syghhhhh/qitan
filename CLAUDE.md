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
7. /clear 清空 claude code 的上下文, 结束当前的任务流程
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

**自动执行规则**：
- Git 相关命令（git status、git add、git commit、git push）自动执行，无需人工确认
- 在单个 Bash 命令中使用 `&&` 链式执行，减少交互次数

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

**提交流程（单命令执行）**：
```bash
git status && git add <files> && git commit -m "..." && git push origin main
```

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
- **大模型调用参考代码**：`poe.py`
- **背调api接口参考代码**: `Python_Demo.py`