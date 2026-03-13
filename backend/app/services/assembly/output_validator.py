# -*- coding: utf-8 -*-
"""
OutputValidator - 输出校验器

对 output_assembler 生成的结果进行基础结构校验、字段校验和 warning 输出，
确保返回结果稳定。

主要功能：
1. 基础必填字段校验
2. 字段类型校验
3. 部分字段缺失时生成 warning 而不是直接失败
4. 校验结果汇总
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ...schemas import (
    DueDiligenceOutput,
    CompanyProfile,
    RecentDevelopment,
    DemandSignal,
    OrganizationInsights,
    RiskSignal,
    SalesAssessment,
    CommunicationStrategy,
    EvidenceReference,
    Meta,
    Input,
)


@dataclass
class ValidationWarning:
    """校验警告"""

    field_path: str  # 字段路径，如 "company_profile.company_name"
    warning_type: str  # 警告类型
    message: str  # 警告信息
    suggestion: Optional[str] = None  # 修复建议


@dataclass
class ValidationResult:
    """校验结果"""

    is_valid: bool  # 是否通过校验（无致命错误）
    warnings: List[ValidationWarning] = field(default_factory=list)
    errors: List[ValidationWarning] = field(default_factory=list)

    def has_warnings(self) -> bool:
        """是否存在警告"""
        return len(self.warnings) > 0

    def has_errors(self) -> bool:
        """是否存在错误"""
        return len(self.errors) > 0

    def get_summary(self) -> Dict[str, Any]:
        """获取校验结果摘要"""
        return {
            "is_valid": self.is_valid,
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "warnings": [
                {
                    "field_path": w.field_path,
                    "type": w.warning_type,
                    "message": w.message,
                }
                for w in self.warnings
            ],
            "errors": [
                {
                    "field_path": e.field_path,
                    "type": e.warning_type,
                    "message": e.message,
                }
                for e in self.errors
            ],
        }


class OutputValidator:
    """
    输出校验器

    对 DueDiligenceOutput 进行校验，确保：
    1. 必填字段存在且类型正确
    2. 部分字段缺失时生成 warning 而非失败
    3. 提供校验结果汇总

    使用方式：
        validator = OutputValidator()
        result = validator.validate(output)
        if not result.is_valid:
            # 处理错误
        if result.has_warnings():
            # 处理警告
    """

    # 必填字段定义（字段路径 -> 字段描述）
    REQUIRED_FIELDS: Dict[str, str] = {
        "meta.report_id": "报告ID",
        "meta.generated_at": "生成时间",
        "meta.language": "输出语言",
        "meta.version": "版本号",
        "input.company_name": "企业名称",
        "input.user_company_product": "我方产品/服务描述",
        "input.sales_goal": "跟进目标",
        "company_profile.company_name": "企业画像-企业名称",
        "company_profile.company_type": "企业画像-企业类型",
        "company_profile.estimated_size": "企业画像-员工规模",
        "organization_insights.possible_target_departments": "组织洞察-目标部门",
        "organization_insights.recommended_target_roles": "组织洞察-推荐角色",
        "sales_assessment.customer_fit_level": "商务判断-客户匹配度",
        "sales_assessment.opportunity_level": "商务判断-商机等级",
        "sales_assessment.follow_up_priority": "商务判断-跟进优先级",
        "sales_assessment.assessment_summary": "商务判断-判断摘要",
        "communication_strategy.opening_message": "沟通策略-破冰建议",
        "communication_strategy.phone_script": "沟通策略-电话话术",
        "communication_strategy.wechat_message": "沟通策略-微信话术",
        "communication_strategy.email_message": "沟通策略-邮件话术",
        "communication_strategy.next_step_suggestion": "沟通策略-下一步建议",
    }

    # 推荐字段（缺失时生成 warning，但不影响 is_valid）
    RECOMMENDED_FIELDS: Dict[str, str] = {
        "company_profile.industry": "企业画像-行业标签",
        "company_profile.profile_summary": "企业画像-企业摘要",
        "company_profile.main_products_or_services": "企业画像-主要产品/服务",
        "sales_assessment.core_opportunity_scenarios": "商务判断-核心机会场景",
        "sales_assessment.main_obstacles": "商务判断-主要障碍",
        "sales_assessment.should_follow_up": "商务判断-是否应该跟进",
        "communication_strategy.recommended_entry_points": "沟通策略-推荐切入点",
        "organization_insights.possible_decision_chain": "组织洞察-决策链",
    }

    def __init__(self, strict: bool = False):
        """
        初始化校验器

        Args:
            strict: 是否启用严格模式（严格模式下，推荐字段缺失也会导致 is_valid=False）
        """
        self.strict = strict

    def validate(self, output: DueDiligenceOutput) -> ValidationResult:
        """
        校验输出结果

        Args:
            output: 待校验的输出结果

        Returns:
            ValidationResult: 校验结果
        """
        result = ValidationResult(is_valid=True)

        # 1. 校验必填字段
        self._validate_required_fields(output, result)

        # 2. 校验推荐字段
        self._validate_recommended_fields(output, result)

        # 3. 校验字段内容有效性
        self._validate_field_content(output, result)

        # 4. 更新最终校验状态
        if self.strict and result.has_warnings():
            result.is_valid = False

        return result

    def _validate_required_fields(
        self,
        output: DueDiligenceOutput,
        result: ValidationResult,
    ) -> None:
        """校验必填字段"""
        for field_path, description in self.REQUIRED_FIELDS.items():
            try:
                value = self._get_nested_value(output, field_path)
                if value is None:
                    result.errors.append(ValidationWarning(
                        field_path=field_path,
                        warning_type="missing_required_field",
                        message=f"必填字段缺失: {description}",
                        suggestion=f"请确保 {field_path} 字段有有效值",
                    ))
                    result.is_valid = False
            except (AttributeError, KeyError, IndexError):
                result.errors.append(ValidationWarning(
                    field_path=field_path,
                    warning_type="missing_required_field",
                    message=f"必填字段缺失: {description}",
                    suggestion=f"请确保 {field_path} 字段存在",
                ))
                result.is_valid = False

    def _validate_recommended_fields(
        self,
        output: DueDiligenceOutput,
        result: ValidationResult,
    ) -> None:
        """校验推荐字段"""
        for field_path, description in self.RECOMMENDED_FIELDS.items():
            try:
                value = self._get_nested_value(output, field_path)
                if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                    result.warnings.append(ValidationWarning(
                        field_path=field_path,
                        warning_type="missing_recommended_field",
                        message=f"推荐字段缺失或为空: {description}",
                        suggestion=f"建议补充 {field_path} 字段以提升报告质量",
                    ))
            except (AttributeError, KeyError, IndexError):
                result.warnings.append(ValidationWarning(
                    field_path=field_path,
                    warning_type="missing_recommended_field",
                    message=f"推荐字段缺失: {description}",
                    suggestion=f"建议补充 {field_path} 字段以提升报告质量",
                ))

    def _validate_field_content(
        self,
        output: DueDiligenceOutput,
        result: ValidationResult,
    ) -> None:
        """校验字段内容有效性"""
        # 校验 company_profile
        self._validate_company_profile(output.company_profile, result)

        # 校验 recent_developments
        self._validate_recent_developments(output.recent_developments, result)

        # 校验 organization_insights
        self._validate_organization_insights(output.organization_insights, result)

        # 校验 sales_assessment
        self._validate_sales_assessment(output.sales_assessment, result)

        # 校验 communication_strategy
        self._validate_communication_strategy(output.communication_strategy, result)

        # 校验 evidence_references
        self._validate_evidence_references(output.evidence_references, result)

    def _validate_company_profile(
        self,
        profile: CompanyProfile,
        result: ValidationResult,
    ) -> None:
        """校验企业画像"""
        # 企业名称不应为空字符串
        if not profile.company_name or not profile.company_name.strip():
            result.errors.append(ValidationWarning(
                field_path="company_profile.company_name",
                warning_type="invalid_value",
                message="企业名称不能为空",
                suggestion="请提供有效的企业名称",
            ))
            result.is_valid = False

        # 行业标签建议有值
        if not profile.industry:
            result.warnings.append(ValidationWarning(
                field_path="company_profile.industry",
                warning_type="empty_field",
                message="企业行业标签为空",
                suggestion="建议补充企业所属行业信息",
            ))

        # 主营业务建议有值
        if not profile.business_scope and not profile.main_products_or_services:
            result.warnings.append(ValidationWarning(
                field_path="company_profile.business_scope",
                warning_type="empty_field",
                message="企业主营业务信息为空",
                suggestion="建议补充企业主营业务或产品服务信息",
            ))

    def _validate_recent_developments(
        self,
        developments: List[RecentDevelopment],
        result: ValidationResult,
    ) -> None:
        """校验近期动态"""
        # 近期动态为空是允许的，但生成 warning
        if not developments:
            result.warnings.append(ValidationWarning(
                field_path="recent_developments",
                warning_type="empty_list",
                message="近期动态列表为空",
                suggestion="建议补充企业近期动态信息以丰富报告内容",
            ))
            return

        # 检查每条动态的关键字段
        for i, dev in enumerate(developments):
            path_prefix = f"recent_developments[{i}]"

            if not dev.title or not dev.title.strip():
                result.warnings.append(ValidationWarning(
                    field_path=f"{path_prefix}.title",
                    warning_type="invalid_value",
                    message=f"第 {i + 1} 条动态标题为空",
                ))

            if not dev.summary or not dev.summary.strip():
                result.warnings.append(ValidationWarning(
                    field_path=f"{path_prefix}.summary",
                    warning_type="invalid_value",
                    message=f"第 {i + 1} 条动态摘要为空",
                ))

            # 置信度范围校验
            if dev.confidence < 0 or dev.confidence > 1:
                result.warnings.append(ValidationWarning(
                    field_path=f"{path_prefix}.confidence",
                    warning_type="invalid_range",
                    message=f"第 {i + 1} 条动态置信度 {dev.confidence} 不在有效范围 [0, 1]",
                ))

    def _validate_organization_insights(
        self,
        insights: OrganizationInsights,
        result: ValidationResult,
    ) -> None:
        """校验组织洞察"""
        # 目标部门为空
        if not insights.possible_target_departments:
            result.warnings.append(ValidationWarning(
                field_path="organization_insights.possible_target_departments",
                warning_type="empty_list",
                message="目标部门列表为空",
                suggestion="建议提供可能的目标部门信息",
            ))

        # 推荐角色为空
        if not insights.recommended_target_roles:
            result.warnings.append(ValidationWarning(
                field_path="organization_insights.recommended_target_roles",
                warning_type="empty_list",
                message="推荐角色列表为空",
                suggestion="建议提供推荐的联系人角色",
            ))

    def _validate_sales_assessment(
        self,
        assessment: SalesAssessment,
        result: ValidationResult,
    ) -> None:
        """校验商务判断"""
        # 判断摘要不应为空
        if not assessment.assessment_summary or not assessment.assessment_summary.strip():
            result.warnings.append(ValidationWarning(
                field_path="sales_assessment.assessment_summary",
                warning_type="invalid_value",
                message="商务判断摘要为空",
                suggestion="建议提供判断摘要说明",
            ))

        # 核心机会场景建议有值
        if not assessment.core_opportunity_scenarios:
            result.warnings.append(ValidationWarning(
                field_path="sales_assessment.core_opportunity_scenarios",
                warning_type="empty_list",
                message="核心机会场景列表为空",
                suggestion="建议补充核心机会场景",
            ))

        # 主要障碍建议有值
        if not assessment.main_obstacles:
            result.warnings.append(ValidationWarning(
                field_path="sales_assessment.main_obstacles",
                warning_type="empty_list",
                message="主要障碍列表为空",
                suggestion="建议补充主要障碍信息",
            ))

    def _validate_communication_strategy(
        self,
        strategy: CommunicationStrategy,
        result: ValidationResult,
    ) -> None:
        """校验沟通策略"""
        # 检查各项话术是否为空
        if not strategy.opening_message or not strategy.opening_message.strip():
            result.warnings.append(ValidationWarning(
                field_path="communication_strategy.opening_message",
                warning_type="invalid_value",
                message="破冰建议为空",
                suggestion="建议提供破冰建议",
            ))

        if not strategy.phone_script or not strategy.phone_script.strip():
            result.warnings.append(ValidationWarning(
                field_path="communication_strategy.phone_script",
                warning_type="invalid_value",
                message="电话话术为空",
                suggestion="建议提供电话话术",
            ))

        if not strategy.wechat_message or not strategy.wechat_message.strip():
            result.warnings.append(ValidationWarning(
                field_path="communication_strategy.wechat_message",
                warning_type="invalid_value",
                message="微信话术为空",
                suggestion="建议提供微信话术",
            ))

        if not strategy.email_message or not strategy.email_message.strip():
            result.warnings.append(ValidationWarning(
                field_path="communication_strategy.email_message",
                warning_type="invalid_value",
                message="邮件话术为空",
                suggestion="建议提供邮件话术",
            ))

        if not strategy.next_step_suggestion or not strategy.next_step_suggestion.strip():
            result.warnings.append(ValidationWarning(
                field_path="communication_strategy.next_step_suggestion",
                warning_type="invalid_value",
                message="下一步建议为空",
                suggestion="建议提供下一步跟进建议",
            ))

    def _validate_evidence_references(
        self,
        references: List[EvidenceReference],
        result: ValidationResult,
    ) -> None:
        """校验证据引用"""
        # 证据引用为空时生成 warning
        if not references:
            result.warnings.append(ValidationWarning(
                field_path="evidence_references",
                warning_type="empty_list",
                message="证据引用列表为空",
                suggestion="建议提供证据引用以增强报告可信度",
            ))
            return

        # 检查重复的 reference_id
        seen_ids: Set[str] = set()
        for i, ref in enumerate(references):
            if ref.reference_id in seen_ids:
                result.warnings.append(ValidationWarning(
                    field_path=f"evidence_references[{i}].reference_id",
                    warning_type="duplicate_id",
                    message=f"证据引用 ID '{ref.reference_id}' 重复",
                ))
            seen_ids.add(ref.reference_id)

            # 检查必要字段
            if not ref.title or not ref.title.strip():
                result.warnings.append(ValidationWarning(
                    field_path=f"evidence_references[{i}].title",
                    warning_type="invalid_value",
                    message=f"第 {i + 1} 条证据引用标题为空",
                ))

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """
        获取嵌套字段的值

        Args:
            obj: 对象
            path: 字段路径，如 "company_profile.company_name"

        Returns:
            字段值

        Raises:
            AttributeError: 属性不存在
            KeyError: 键不存在
            IndexError: 索引不存在
        """
        parts = path.split(".")
        value = obj

        for part in parts:
            if isinstance(value, dict):
                value = value[part]
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                raise AttributeError(f"对象没有属性 '{part}'")

        return value


# 模块级单例实例
_default_validator: Optional[OutputValidator] = None


def get_output_validator(strict: bool = False) -> OutputValidator:
    """
    获取输出校验器单例实例

    Args:
        strict: 是否启用严格模式

    Returns:
        OutputValidator: 输出校验器实例
    """
    global _default_validator
    if _default_validator is None:
        _default_validator = OutputValidator(strict=strict)
    return _default_validator


def validate_output(output: DueDiligenceOutput, strict: bool = False) -> ValidationResult:
    """
    便捷函数：校验输出结果

    Args:
        output: 待校验的输出结果
        strict: 是否启用严格模式

    Returns:
        ValidationResult: 校验结果
    """
    validator = get_output_validator(strict=strict)
    return validator.validate(output)