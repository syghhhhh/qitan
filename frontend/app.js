// 企业背调智能体 - 前端交互逻辑

document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultSection = document.getElementById('result-section');
    const errorMessage = document.getElementById('error-message');

    // 分析按钮点击事件
    analyzeBtn.addEventListener('click', async function() {
        const companyName = document.getElementById('company-name').value.trim();

        // 验证必填项
        if (!companyName) {
            showError('请输入企业名称');
            return;
        }

        // 收集表单数据
        const requestData = {
            company_name: companyName,
            company_website: document.getElementById('company-website').value.trim() || null,
            user_company_product: document.getElementById('user-product').value.trim() || null,
            user_target_customer_profile: document.getElementById('target-customer').value.trim() || null,
            sales_goal: document.getElementById('sales-goal').value || null,
            target_role: document.getElementById('target-role').value.trim() || null,
            extra_context: document.getElementById('extra-context').value.trim() || null
        };

        // 显示加载状态
        setLoading(true);
        hideError();
        resultSection.style.display = 'none';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || '分析请求失败');
            }

            // 渲染结果
            renderResult(result);
            resultSection.style.display = 'block';

        } catch (error) {
            showError(error.message || '网络错误，请稍后重试');
        } finally {
            setLoading(false);
        }
    });

    // 设置加载状态
    function setLoading(loading) {
        analyzeBtn.disabled = loading;
        analyzeBtn.querySelector('.btn-text').style.display = loading ? 'none' : 'inline';
        analyzeBtn.querySelector('.btn-loading').style.display = loading ? 'inline' : 'none';
    }

    // 显示错误
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    // 隐藏错误
    function hideError() {
        errorMessage.style.display = 'none';
    }

    // 渲染结果
    function renderResult(data) {
        renderCompanyOverview(data.company_profile);
        renderRecentDevelopments(data.recent_developments);
        renderDemandSignals(data.demand_signals);
        renderRecommendedContacts(data.organization_insights);
        renderRiskSignals(data.risk_signals);
        renderSalesAssessment(data.sales_assessment);
        renderCommunicationStrategy(data.communication_strategy);
        renderEvidenceReferences(data.evidence_references);
        renderPriorityBadge(data.sales_assessment?.follow_up_priority);
    }

    // 渲染优先级标签
    function renderPriorityBadge(priority) {
        const badge = document.getElementById('priority-badge');
        const priorityMap = {
            'P1': { text: '高优先级', class: 'p1' },
            'P2': { text: '中优先级', class: 'p2' },
            'P3': { text: '低优先级', class: 'p3' },
            'discard': { text: '不建议跟进', class: 'discard' }
        };
        const info = priorityMap[priority] || { text: priority, class: 'p3' };
        badge.textContent = info.text;
        badge.className = 'priority-badge ' + info.class;
    }

    // 渲染企业概览
    function renderCompanyOverview(profile) {
        if (!profile) return;
        const content = document.querySelector('#company-overview .card-content');
        content.innerHTML = `
            <div class="company-info">
                <div class="info-item">
                    <span class="label">企业名称</span>
                    <span class="value">${profile.company_name || '-'}</span>
                </div>
                <div class="info-item">
                    <span class="label">行业</span>
                    <span class="value">${(profile.industry || []).join('、') || '-'}</span>
                </div>
                <div class="info-item">
                    <span class="label">企业类型</span>
                    <span class="value">${profile.company_type || '-'}</span>
                </div>
                <div class="info-item">
                    <span class="label">成立年份</span>
                    <span class="value">${profile.founded_year || '-'}</span>
                </div>
                <div class="info-item">
                    <span class="label">总部</span>
                    <span class="value">${profile.headquarters || '-'}</span>
                </div>
                <div class="info-item">
                    <span class="label">企业规模</span>
                    <span class="value">${profile.estimated_size || '-'}</span>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                    <span class="label">主营业务</span>
                    <span class="value">${(profile.business_scope || []).join('、') || '-'}</span>
                </div>
                <div class="info-item" style="grid-column: 1 / -1;">
                    <span class="label">企业简介</span>
                    <span class="value">${profile.profile_summary || '-'}</span>
                </div>
            </div>
        `;
    }

    // 渲染近期动态
    function renderRecentDevelopments(developments) {
        const content = document.querySelector('#recent-developments .card-content');
        if (!developments || developments.length === 0) {
            content.innerHTML = '<p class="empty-text">暂无近期动态信息</p>';
            return;
        }
        const typeMap = {
            'news': '新闻动态', 'financing': '融资事件', 'hiring': '招聘动态',
            'expansion': '业务扩张', 'new_product': '新产品', 'bidding': '招投标',
            'partnership': '合作伙伴', 'digital_transformation': '数字化建设',
            'management_change': '管理层变动', 'compliance': '合规相关', 'other': '其他'
        };
        content.innerHTML = `
            <ul class="item-list">
                ${developments.map(item => `
                    <li>
                        <div class="item-title">${item.title || '-'}</div>
                        <div class="item-meta">
                            <span>${item.date || '-'}</span>
                            <span> · </span>
                            <span>${typeMap[item.type] || item.type}</span>
                        </div>
                        <div class="item-desc">${item.summary || ''}</div>
                    </li>
                `).join('')}
            </ul>
        `;
    }

    // 渲染需求信号
    function renderDemandSignals(signals) {
        const content = document.querySelector('#demand-signals .card-content');
        if (!signals || signals.length === 0) {
            content.innerHTML = '<p class="empty-text">暂无需求信号</p>';
            return;
        }
        const typeMap = {
            'recruitment_signal': '招聘信号', 'expansion_signal': '扩张信号',
            'digitalization_signal': '数字化信号', 'growth_signal': '增长信号',
            'management_signal': '管理升级信号', 'cost_reduction_signal': '降本增效信号',
            'compliance_signal': '合规信号', 'customer_operation_signal': '客户经营信号',
            'sales_management_signal': '销售管理信号', 'data_governance_signal': '数据治理信号',
            'other': '其他信号'
        };
        content.innerHTML = `
            <ul class="item-list">
                ${signals.map(item => `
                    <li>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span class="item-title">${item.signal || '-'}</span>
                            <span class="strength-badge ${item.strength}">${item.strength === 'high' ? '强' : item.strength === 'medium' ? '中' : '弱'}</span>
                        </div>
                        <div class="item-meta">${typeMap[item.signal_type] || item.signal_type}</div>
                        <div class="item-desc">${item.inference || ''}</div>
                    </li>
                `).join('')}
            </ul>
        `;
    }

    // 渲染推荐联系人
    function renderRecommendedContacts(insights) {
        const content = document.querySelector('#recommended-contacts .card-content');
        if (!insights || !insights.recommended_target_roles || insights.recommended_target_roles.length === 0) {
            content.innerHTML = '<p class="empty-text">暂无推荐联系人</p>';
            return;
        }
        content.innerHTML = `
            <ul class="item-list">
                ${insights.recommended_target_roles.map((item, index) => `
                    <li>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span class="item-title">${item.role}</span>
                                ${item.department ? `<span class="item-meta"> · ${item.department}</span>` : ''}
                            </div>
                            <span style="font-size: 12px; color: #888;">优先级 ${item.priority}</span>
                        </div>
                        <div class="item-desc">${item.reason || ''}</div>
                    </li>
                `).join('')}
            </ul>
            ${insights.possible_decision_chain && insights.possible_decision_chain.length > 0 ? `
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #eee;">
                    <div style="font-size: 13px; color: #666; margin-bottom: 6px;">可能决策链</div>
                    <div style="font-size: 14px;">${insights.possible_decision_chain.join(' → ')}</div>
                </div>
            ` : ''}
        `;
    }

    // 渲染风险提示
    function renderRiskSignals(risks) {
        const content = document.querySelector('#risk-signals .card-content');
        if (!risks || risks.length === 0) {
            content.innerHTML = '<p class="empty-text">暂无明显风险</p>';
            return;
        }
        const typeMap = {
            'legal': '法律风险', 'compliance': '合规风险', 'financial': '财务风险',
            'reputation': '舆情风险', 'procurement_complexity': '采购复杂度高',
            'organization_instability': '组织不稳定', 'low_budget_probability': '预算不足概率高',
            'unclear_demand': '需求不清晰', 'long_decision_cycle': '决策周期长', 'other': '其他'
        };
        content.innerHTML = `
            <ul class="item-list">
                ${risks.map(item => `
                    <li>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span class="item-title">${item.risk || '-'}</span>
                            <span class="level-badge ${item.level}">${item.level === 'high' ? '高' : item.level === 'medium' ? '中' : '低'}</span>
                        </div>
                        <div class="item-meta">${typeMap[item.risk_type] || item.risk_type}</div>
                        <div class="item-desc">${item.description || ''}</div>
                    </li>
                `).join('')}
            </ul>
        `;
    }

    // 渲染商务判断
    function renderAssessment(assessment) {
        const content = document.querySelector('#sales-assessment .card-content');
        if (!assessment) {
            content.innerHTML = '<p class="empty-text">暂无商务判断</p>';
            return;
        }
        const fitMap = { 'high': '高匹配', 'medium': '中匹配', 'low': '低匹配' };
        const oppMap = { 'high': '高商机', 'medium': '中商机', 'low': '低商机' };
        const priorityMap = { 'P1': '高优先级', 'P2': '中优先级', 'P3': '低优先级', 'discard': '放弃' };
        content.innerHTML = `
            <div class="assessment-grid">
                <div class="assessment-item">
                    <div class="value">${fitMap[assessment.customer_fit_level] || assessment.customer_fit_level}</div>
                    <div class="label">客户匹配度</div>
                </div>
                <div class="assessment-item">
                    <div class="value">${oppMap[assessment.opportunity_level] || assessment.opportunity_level}</div>
                    <div class="label">商机等级</div>
                </div>
                <div class="assessment-item">
                    <div class="value">${priorityMap[assessment.follow_up_priority] || assessment.follow_up_priority}</div>
                    <div class="label">跟进优先级</div>
                </div>
            </div>
            ${assessment.core_opportunity_scenarios && assessment.core_opportunity_scenarios.length > 0 ? `
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 13px; color: #666; margin-bottom: 6px;">核心机会场景</div>
                    <div>${assessment.core_opportunity_scenarios.map(s => `<span class="entry-point-tag">${s}</span>`).join('')}</div>
                </div>
            ` : ''}
            <div class="assessment-summary">
                <div style="font-size: 13px; color: #666; margin-bottom: 4px;">判断摘要</div>
                <div>${assessment.assessment_summary || '-'}</div>
            </div>
        `;
    }

    // 渲染沟通策略
    function renderCommunicationStrategy(strategy) {
        const content = document.querySelector('#communication-strategy .card-content');
        if (!strategy) {
            content.innerHTML = '<p class="empty-text">暂无沟通策略</p>';
            return;
        }
        content.innerHTML = `
            ${strategy.recommended_entry_points && strategy.recommended_entry_points.length > 0 ? `
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 13px; color: #666; margin-bottom: 6px;">推荐切入点</div>
                    <div class="entry-points">
                        ${strategy.recommended_entry_points.map(p => `<span class="entry-point-tag">${p}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            ${strategy.avoid_points && strategy.avoid_points.length > 0 ? `
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 13px; color: #666; margin-bottom: 6px;">避免点</div>
                    <div>
                        ${strategy.avoid_points.map(p => `<span class="avoid-point-tag">${p}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            ${strategy.opening_message ? `
                <div class="script-block">
                    <h4>一句话破冰</h4>
                    <p>${strategy.opening_message}</p>
                </div>
            ` : ''}
            ${strategy.wechat_message ? `
                <div class="script-block">
                    <h4>微信话术</h4>
                    <p>${strategy.wechat_message}</p>
                </div>
            ` : ''}
            ${strategy.phone_script ? `
                <div class="script-block">
                    <h4>电话话术</h4>
                    <p>${strategy.phone_script}</p>
                </div>
            ` : ''}
            ${strategy.email_message ? `
                <div class="script-block">
                    <h4>邮件话术</h4>
                    <p>${strategy.email_message}</p>
                </div>
            ` : ''}
            ${strategy.next_step_suggestion ? `
                <div style="margin-top: 12px; padding: 12px; background: #e3f2fd; border-radius: 6px;">
                    <div style="font-size: 13px; color: #1565c0; margin-bottom: 4px;">下一步建议</div>
                    <div>${strategy.next_step_suggestion}</div>
                </div>
            ` : ''}
        `;
    }

    // 渲染证据来源
    function renderEvidenceReferences(references) {
        const content = document.querySelector('#evidence-references .card-content');
        if (!references || references.length === 0) {
            content.innerHTML = '<p class="empty-text">暂无证据来源</p>';
            return;
        }
        content.innerHTML = `
            <ul class="item-list">
                ${references.map(item => `
                    <li>
                        <div class="item-title">${item.title || '-'}</div>
                        <div class="item-meta">
                            <span>${item.source || '-'}</span>
                            ${item.date ? `<span> · ${item.date}</span>` : ''}
                        </div>
                        ${item.excerpt ? `<div class="item-desc">${item.excerpt}</div>` : ''}
                        ${item.url ? `<a href="${item.url}" target="_blank" style="font-size: 12px; color: #1a73e8;">查看原文</a>` : ''}
                    </li>
                `).join('')}
            </ul>
        `;
    }

    // 别名函数，保持兼容
    function renderSalesAssessment(assessment) {
        renderAssessment(assessment);
    }
});