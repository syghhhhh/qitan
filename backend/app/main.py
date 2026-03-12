"""
企业背调智能体 MVP - FastAPI 应用入口
"""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .schemas import DueDiligenceOutput, SalesGoalEnum
from .services.mock_analyzer import get_mock_analysis

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


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误详情")
    detail: Optional[str] = Field(None, description="详细信息")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}


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

        # 调用 Mock 分析逻辑
        result = get_mock_analysis(
            company_name=request.company_name.strip(),
            user_company_product=request.user_company_product,
            company_website=request.company_website,
            user_target_customer_profile=request.user_target_customer_profile,
            sales_goal=request.sales_goal,
            target_role=request.target_role,
            extra_context=request.extra_context,
        )

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


# 挂载静态文件服务（CSS、JS）
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", response_class=FileResponse)
async def root():
    """返回前端首页"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="index.html not found")