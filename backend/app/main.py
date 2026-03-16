"""
企业背调智能体 MVP - FastAPI 应用入口
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import get_run_mode_config
from .schemas import DueDiligenceOutput, SalesGoalEnum
from .services.collection.qichacha_client import get_qichacha_client
from .services.llm.llm_client import LLMMessage, LLMRequest, get_llm_client, LLMProvider
from .services.orchestrator import AnalysisRequest, get_orchestrator, RunMode

# 前端静态文件目录
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"

# 创建 FastAPI 应用实例
app = FastAPI(
    title="企业背调智能体",
    description="面向企业商务岗位，对企业进行公开信息背调，输出企业画像、需求信号、风险提示、联系人建议和沟通话术。",
    version="0.1.0",
)

# 配置 CORS 中间件支持跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """分析请求模型"""

    company_name: str = Field(..., description="目标企业名称（必填）")
    company_website: Optional[str] = Field(None, description="目标企业官网")
    user_company_product: str = Field(
        default="CRM系统", description="我方产品/服务描述"
    )
    user_target_customer_profile: Optional[str] = Field(
        None, description="我方理想客户画像"
    )
    sales_goal: SalesGoalEnum = Field(
        default=SalesGoalEnum.FIRST_TOUCH, description="本次跟进目标"
    )
    target_role: Optional[str] = Field(None, description="用户希望接触的角色")
    extra_context: Optional[str] = Field(None, description="用户补充背景")
    run_mode: Optional[str] = Field(None, description="运行模式: full_mock, hybrid, full_pipeline")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误详情")
    detail: Optional[str] = Field(None, description="详细信息")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    config = get_run_mode_config()
    return {
        "status": "ok",
        "default_run_mode": config.default_run_mode.value,
        "full_pipeline_available": config._check_full_pipeline_available(),
        "hybrid_available": config._check_hybrid_available(),
    }


@app.post(
    "/analyze",
    response_model=DueDiligenceOutput,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
    summary="企业背调分析",
    description="接收企业名称等输入信息，返回完整的企业背调报告。",
)
async def analyze(request: AnalyzeRequest) -> DueDiligenceOutput:
    """
    企业背调分析接口

    接收企业信息，返回包含企业画像、需求信号、风险提示、
    推荐联系人、商务判断和沟通话术的完整背调报告。
    """
    try:
        # 参数校验：企业名称不能为空
        if not request.company_name or not request.company_name.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "企业名称不能为空",
                    "detail": "company_name 字段为必填项，请提供有效的企业名称",
                },
            )

        # 获取运行模式配置
        config = get_run_mode_config()

        # 解析请求中的运行模式
        run_mode_value: Optional[RunMode] = None
        if request.run_mode:
            mode_map = {
                "full_mock": RunMode.FULL_MOCK,
                "hybrid": RunMode.HYBRID,
                "full_pipeline": RunMode.FULL_PIPELINE,
            }
            run_mode_value = mode_map.get(request.run_mode.lower())

        # 构建 orchestrator 请求（只在有值时传入 run_mode）
        request_kwargs = {
            "company_name": request.company_name.strip(),
            "company_website": request.company_website,
            "user_company_product": request.user_company_product,
            "user_target_customer_profile": request.user_target_customer_profile,
            "sales_goal": request.sales_goal,
            "target_role": request.target_role,
            "extra_context": request.extra_context,
        }
        if run_mode_value is not None:
            request_kwargs["run_mode"] = run_mode_value

        orchestrator_request = AnalysisRequest(**request_kwargs)

        # 通过 orchestrator 统一调用
        orchestrator = get_orchestrator()
        result = await orchestrator.analyze(orchestrator_request)

        return result

    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        # 捕获未预期的异常，返回 JSON 格式错误
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "服务器内部错误",
                "detail": str(e),
            },
        )


class CollectRequest(BaseModel):
    """数据采集请求模型"""
    company_name: str = Field(..., description="目标企业名称（必填）")


class CollectResponse(BaseModel):
    """数据采集响应模型"""
    accurate_name: str
    fuzzy_results: List[Dict[str, Any]]
    verify_data: Dict[str, Any]


@app.post(
    "/collect",
    response_model=CollectResponse,
    summary="企业数据采集",
    description="调用企查查 API 获取企业全量信息，用于前端即时展示。",
)
async def collect(request: CollectRequest) -> CollectResponse:
    """企业数据采集接口 — 直接调用企查查，不经过分析流水线"""
    try:
        if not request.company_name or not request.company_name.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "validation_error", "message": "企业名称不能为空"},
            )

        client = get_qichacha_client()
        result = client.get_company_info(request.company_name.strip())

        return CollectResponse(
            accurate_name=result["accurate_name"],
            fuzzy_results=result["fuzzy_results"],
            verify_data=result["verify_data"],
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "collection_error", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": str(e)})


class ChatRequest(BaseModel):
    """智能体对话请求模型"""
    messages: List[Dict[str, str]]  # [{"role":"user","content":"..."}]
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096


@app.post("/chat/stream", summary="智能体流式问答")
async def chat_stream(request: ChatRequest, raw_request: Request):
    """SSE 流式对话接口"""

    async def event_generator():
        # 构建 LLM 消息
        messages = []
        if request.system_prompt:
            messages.append(LLMMessage(role="system", content=request.system_prompt))
        for msg in request.messages:
            messages.append(LLMMessage(role=msg.get("role", "user"), content=msg.get("content", "")))

        llm_request = LLMRequest(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        try:
            client = get_llm_client(provider=LLMProvider.POE)
        except Exception:
            client = get_llm_client(provider=LLMProvider.MOCK)

        try:
            async for chunk in client.stream_complete(llm_request):
                # 检查客户端是否断开
                if await raw_request.is_disconnected():
                    break
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'token', 'content': f'[错误] {e}'}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# 挂载静态文件服务（CSS、JS）
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", response_class=FileResponse)
async def root():
    """返回前端首页"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="index.html not found")