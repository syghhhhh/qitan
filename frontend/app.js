// 企业背调智能体 - 前端交互逻辑 v0.0.3

// 全局状态
let chatMessages = [];
let chatSystemPrompt = '';
let chatAbortController = null;
let collectData = null;
let analysisData = null;

document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const errorMessage = document.getElementById('error-message');

    // === Panel 1: 分析按钮 ===
    analyzeBtn.addEventListener('click', async function() {
        const companyName = document.getElementById('company-name').value.trim();
        if (!companyName) {
            showError('请输入企业名称');
            return;
        }

        setLoading(true);
        hideError();
        hideAllPanels();

        // Step 1: 调用 /collect 获取企业信息
        try {
            const collectResponse = await fetch('/collect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ company_name: companyName })
            });
            const collectResult = await collectResponse.json();
            if (!collectResponse.ok) {
                throw new Error(parseErrorMessage(collectResult));
            }
            collectData = collectResult;
            renderEnterpriseInfo(collectResult);
            document.getElementById('panel-enterprise').style.display = 'block';
        } catch (error) {
            showError('企业信息获取失败: ' + error.message);
            setLoading(false);
            return;
        }

        // Step 2: 调用 /analyze 获取分析结果
        try {
            document.getElementById('panel-analysis').style.display = 'block';
            document.getElementById('analysis-loading').style.display = 'flex';
            document.getElementById('analysis-content').style.display = 'none';

            const requestData = buildAnalyzeRequest(companyName);
            const analyzeResponse = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            const analyzeResult = await analyzeResponse.json();
            if (!analyzeResponse.ok) {
                throw new Error(parseErrorMessage(analyzeResult));
            }
            analysisData = analyzeResult;
            renderAnalysisResult(analyzeResult);
            document.getElementById('analysis-loading').style.display = 'none';
            document.getElementById('analysis-content').style.display = 'block';
        } catch (error) {
            document.getElementById('analysis-loading').innerHTML =
                `<span style="color:#c62828;">分析失败: ${error.message}</span>`;
        }

        // Step 3: 激活聊天面板
        initChat();
        setLoading(false);
    });

    // === Chat 发送按钮 ===
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('chat-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // === Chat 停止按钮 ===
    document.getElementById('stop-btn').addEventListener('click', stopStream);

    // === Chat 清空按钮 ===
    document.getElementById('clear-chat-btn').addEventListener('click', clearChat);
});

// === 折叠/展开企业信息分组 ===
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.classList.toggle('collapsed');
}

// === 工具函数 ===
function setLoading(loading) {
    const btn = document.getElementById('analyze-btn');
    btn.disabled = loading;
    btn.querySelector('.btn-text').style.display = loading ? 'none' : 'inline';
    btn.querySelector('.btn-loading').style.display = loading ? 'inline' : 'none';
}

function showError(message) {
    const el = document.getElementById('error-message');
    el.textContent = message;
    el.style.display = 'block';
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}

function hideAllPanels() {
    document.getElementById('panel-enterprise').style.display = 'none';
    document.getElementById('panel-analysis').style.display = 'none';
    document.getElementById('panel-chat').style.display = 'none';
}

function parseErrorMessage(result) {
    if (result.detail) {
        if (typeof result.detail === 'string') return result.detail;
        if (result.detail.message) return result.detail.message;
        if (Array.isArray(result.detail)) {
            return result.detail.map(e => {
                const field = e.loc ? e.loc.join(' -> ') : '未知字段';
                return `${field}: ${e.msg}`;
            }).join('; ');
        }
        return JSON.stringify(result.detail);
    }
    return '请求失败';
}

function val(v) {
    if (v === null || v === undefined || v === '') return '—';
    return String(v);
}

function buildAnalyzeRequest(companyName) {
    const data = { company_name: companyName };
    const website = document.getElementById('company-website').value.trim();
    if (website) data.company_website = website;
    const product = document.getElementById('user-product').value.trim();
    if (product) data.user_company_product = product;
    const targetCustomer = document.getElementById('target-customer').value.trim();
    if (targetCustomer) data.user_target_customer_profile = targetCustomer;
    const salesGoal = document.getElementById('sales-goal').value;
    if (salesGoal) data.sales_goal = salesGoal;
    const targetRole = document.getElementById('target-role').value.trim();
    if (targetRole) data.target_role = targetRole;
    const extraContext = document.getElementById('extra-context').value.trim();
    if (extraContext) data.extra_context = extraContext;
    return data;
}

// === Panel 2: 企业信息渲染 ===
function renderEnterpriseInfo(data) {
    document.getElementById('enterprise-name-badge').textContent = data.accurate_name;
    const d = data.verify_data || {};

    // 基本信息
    renderGrid('grid-basic', [
        ['企业名称', d.Name],
        ['Logo', d.ImageUrl ? `<img src="${d.ImageUrl}" style="height:40px;border-radius:4px;">` : null],
        ['统一信用代码', d.CreditCode],
        ['法定代表人', d.OperName],
        ['经营状态', d.Status],
        ['成立日期', d.StartDate],
        ['经济类型', d.EconKind],
        ['企业类型', d.EntType],
        ['企业规模', d.Scale],
        ['是否小微', d.IsSmall],
        ['人员规模', d.PersonScope],
        ['参保人数', d.InsuredCount],
        ['纳税人类型', d.TaxpayerType],
    ]);

    // 资本信息
    const rc = d.RegisteredCapital || {};
    const pc = d.PaidUpCapital || {};
    renderGrid('grid-capital', [
        ['注册资本', d.RegistCapi],
        ['注册资本(结构)', rc.Amount ? `${rc.Amount} ${val(rc.Unit)} ${val(rc.CCY)}` : null],
        ['实缴资本', d.RealCapi],
        ['实缴资本(结构)', pc.Amount ? `${pc.Amount} ${val(pc.Unit)} ${val(pc.CCY)}` : null],
    ]);

    // 注册信息
    renderGrid('grid-registration', [
        ['组织机构代码', d.OrgNo],
        ['注册号', d.No],
        ['税务登记号', d.TaxNo],
        ['营业期限起', d.TermStart],
        ['营业期限止', d.TermEnd],
        ['核准日期', d.CheckDate],
        ['登记机关', d.BelongOrg],
        ['进出口代码', d.ImExCode],
        ['机构代码列表', d.OrgCodeList],
    ]);

    // 地址信息
    const area = d.Area || {};
    renderGrid('grid-address', [
        ['省份', area.Province],
        ['城市', area.City],
        ['区县', area.County],
        ['注册地址', d.Address],
        ['邮编', d.AddressPostalCode],
        ['年报地址', d.AnnualAddress],
        ['年报邮编', d.AnnualAddressPostalCode],
        ['经纬度', d.LongLat],
    ]);

    // 行业分类
    const ind = d.Industry || {};
    const qind = d.QccIndustry || {};
    renderGrid('grid-industry', [
        ['国标行业(大类)', ind.IndustryName],
        ['国标行业(中类)', ind.SubIndustryName],
        ['国标行业(小类)', ind.MiddleCategory],
        ['国标行业(细类)', ind.SmallCategory],
        ['企查查行业(大类)', qind.AName],
        ['企查查行业(中类)', qind.BName],
        ['企查查行业(小类)', qind.CName],
        ['企查查行业(细类)', qind.DName],
    ]);

    // 经营信息
    renderGrid('grid-operation', [
        ['经营范围', d.Scope],
        ['英文名称', d.EnglishName],
        ['是否官方英文', d.IsOfficialEnglish],
    ], true);

    // 联系方式
    const ci = d.ContactInfo || {};
    const websites = (ci.WebSiteList || []).map(w => w.Name || w).join('、');
    const moreEmails = (ci.MoreEmailList || []).map(e => e.Email || e).join('、');
    const moreTels = (ci.MoreTelList || []).map(t => t.Tel || t).join('、');
    renderGrid('grid-contact', [
        ['官网', websites],
        ['邮箱', ci.Email],
        ['更多邮箱', moreEmails],
        ['电话', ci.Tel],
        ['更多电话', moreTels],
    ]);

    // 银行/开票
    const bi = d.BankInfo || {};
    renderGrid('grid-bank', [
        ['开户行', bi.Bank],
        ['银行账号', bi.BankAccount],
        ['开票名称', bi.Name],
        ['开票信用代码', bi.CreditCode],
        ['开票地址', bi.Address],
        ['开票电话', bi.Tel],
    ]);

    // 历史/股票
    const origNames = (d.OriginalName || []).map(o => o.Name || o).join('、');
    const si = d.StockInfo || {};
    renderGrid('grid-history', [
        ['曾用名', origNames],
        ['股票代码', si.StockNumber],
        ['股票类型', si.StockType],
        ['上市日期', si.ListedDate],
        ['吊销信息', d.RevokeInfo],
    ]);
}

function renderGrid(gridId, items, fullWidth) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = items.map(([label, value]) => {
        const isHtml = typeof value === 'string' && value.startsWith('<');
        const displayValue = isHtml ? value : val(value);
        const cls = fullWidth ? ' full-width' : '';
        return `<div class="info-item${cls}">
            <span class="label">${label}</span>
            <span class="value">${displayValue}</span>
        </div>`;
    }).join('');
}

// === Panel 3: 分析结果渲染 ===
function renderAnalysisResult(data) {
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

function renderPriorityBadge(priority) {
    const badge = document.getElementById('priority-badge');
    const map = {
        'P1': { text: '高优先级', class: 'p1' },
        'P2': { text: '中优先级', class: 'p2' },
        'P3': { text: '低优先级', class: 'p3' },
        'discard': { text: '不建议跟进', class: 'discard' }
    };
    const info = map[priority] || { text: priority || '', class: 'p3' };
    badge.textContent = info.text;
    badge.className = 'priority-badge ' + info.class;
}

function renderCompanyOverview(profile) {
    if (!profile) return;
    const content = document.querySelector('#company-overview .card-content');
    content.innerHTML = `
        <div class="company-info">
            <div class="info-item"><span class="label">企业名称</span><span class="value">${profile.company_name || '-'}</span></div>
            <div class="info-item"><span class="label">行业</span><span class="value">${(profile.industry || []).join('、') || '-'}</span></div>
            <div class="info-item"><span class="label">企业类型</span><span class="value">${profile.company_type || '-'}</span></div>
            <div class="info-item"><span class="label">成立年份</span><span class="value">${profile.founded_year || '-'}</span></div>
            <div class="info-item"><span class="label">总部</span><span class="value">${profile.headquarters || '-'}</span></div>
            <div class="info-item"><span class="label">企业规模</span><span class="value">${profile.estimated_size || '-'}</span></div>
            <div class="info-item" style="grid-column: 1 / -1;"><span class="label">主营业务</span><span class="value">${(profile.business_scope || []).join('、') || '-'}</span></div>
            <div class="info-item" style="grid-column: 1 / -1;"><span class="label">企业简介</span><span class="value">${profile.profile_summary || '-'}</span></div>
        </div>`;
}

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
    content.innerHTML = `<ul class="item-list">${developments.map(item => `
        <li>
            <div class="item-title">${item.title || '-'}</div>
            <div class="item-meta"><span>${item.date || '-'}</span> · <span>${typeMap[item.type] || item.type}</span></div>
            <div class="item-desc">${item.summary || ''}</div>
        </li>`).join('')}</ul>`;
}

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
    content.innerHTML = `<ul class="item-list">${signals.map(item => `
        <li>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span class="item-title">${item.signal || '-'}</span>
                <span class="strength-badge ${item.strength}">${item.strength === 'high' ? '强' : item.strength === 'medium' ? '中' : '弱'}</span>
            </div>
            <div class="item-meta">${typeMap[item.signal_type] || item.signal_type}</div>
            <div class="item-desc">${item.inference || ''}</div>
        </li>`).join('')}</ul>`;
}

function renderRecommendedContacts(insights) {
    const content = document.querySelector('#recommended-contacts .card-content');
    if (!insights || !insights.recommended_target_roles || insights.recommended_target_roles.length === 0) {
        content.innerHTML = '<p class="empty-text">暂无推荐联系人</p>';
        return;
    }
    content.innerHTML = `
        <ul class="item-list">${insights.recommended_target_roles.map(item => `
            <li>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div><span class="item-title">${item.role}</span>${item.department ? `<span class="item-meta"> · ${item.department}</span>` : ''}</div>
                    <span style="font-size:12px;color:#888;">优先级 ${item.priority}</span>
                </div>
                <div class="item-desc">${item.reason || ''}</div>
            </li>`).join('')}</ul>
        ${insights.possible_decision_chain && insights.possible_decision_chain.length > 0 ? `
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid #eee;">
                <div style="font-size:13px;color:#666;margin-bottom:6px;">可能决策链</div>
                <div style="font-size:14px;">${insights.possible_decision_chain.join(' → ')}</div>
            </div>` : ''}`;
}

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
    content.innerHTML = `<ul class="item-list">${risks.map(item => `
        <li>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span class="item-title">${item.risk || '-'}</span>
                <span class="level-badge ${item.level}">${item.level === 'high' ? '高' : item.level === 'medium' ? '中' : '低'}</span>
            </div>
            <div class="item-meta">${typeMap[item.risk_type] || item.risk_type}</div>
            <div class="item-desc">${item.description || ''}</div>
        </li>`).join('')}</ul>`;
}

function renderSalesAssessment(assessment) {
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
            <div class="assessment-item"><div class="value">${fitMap[assessment.customer_fit_level] || assessment.customer_fit_level}</div><div class="label">客户匹配度</div></div>
            <div class="assessment-item"><div class="value">${oppMap[assessment.opportunity_level] || assessment.opportunity_level}</div><div class="label">商机等级</div></div>
            <div class="assessment-item"><div class="value">${priorityMap[assessment.follow_up_priority] || assessment.follow_up_priority}</div><div class="label">跟进优先级</div></div>
        </div>
        ${assessment.core_opportunity_scenarios && assessment.core_opportunity_scenarios.length > 0 ? `
            <div style="margin-bottom:12px;">
                <div style="font-size:13px;color:#666;margin-bottom:6px;">核心机会场景</div>
                <div>${assessment.core_opportunity_scenarios.map(s => `<span class="entry-point-tag">${s}</span>`).join('')}</div>
            </div>` : ''}
        <div class="assessment-summary">
            <div style="font-size:13px;color:#666;margin-bottom:4px;">判断摘要</div>
            <div>${assessment.assessment_summary || '-'}</div>
        </div>`;
}

function renderCommunicationStrategy(strategy) {
    const content = document.querySelector('#communication-strategy .card-content');
    if (!strategy) {
        content.innerHTML = '<p class="empty-text">暂无沟通策略</p>';
        return;
    }
    let html = '';
    if (strategy.recommended_entry_points?.length > 0) {
        html += `<div style="margin-bottom:12px;"><div style="font-size:13px;color:#666;margin-bottom:6px;">推荐切入点</div>
            <div class="entry-points">${strategy.recommended_entry_points.map(p => `<span class="entry-point-tag">${p}</span>`).join('')}</div></div>`;
    }
    if (strategy.avoid_points?.length > 0) {
        html += `<div style="margin-bottom:12px;"><div style="font-size:13px;color:#666;margin-bottom:6px;">避免点</div>
            <div>${strategy.avoid_points.map(p => `<span class="avoid-point-tag">${p}</span>`).join('')}</div></div>`;
    }
    if (strategy.opening_message) html += `<div class="script-block"><h4>一句话破冰</h4><p>${strategy.opening_message}</p></div>`;
    if (strategy.wechat_message) html += `<div class="script-block"><h4>微信话术</h4><p>${strategy.wechat_message}</p></div>`;
    if (strategy.phone_script) html += `<div class="script-block"><h4>电话话术</h4><p>${strategy.phone_script}</p></div>`;
    if (strategy.email_message) html += `<div class="script-block"><h4>邮件话术</h4><p>${strategy.email_message}</p></div>`;
    if (strategy.next_step_suggestion) {
        html += `<div style="margin-top:12px;padding:12px;background:#e3f2fd;border-radius:6px;">
            <div style="font-size:13px;color:#1565c0;margin-bottom:4px;">下一步建议</div><div>${strategy.next_step_suggestion}</div></div>`;
    }
    content.innerHTML = html;
}

function renderEvidenceReferences(references) {
    const content = document.querySelector('#evidence-references .card-content');
    if (!references || references.length === 0) {
        content.innerHTML = '<p class="empty-text">暂无证据来源</p>';
        return;
    }
    content.innerHTML = `<ul class="item-list">${references.map(item => `
        <li>
            <div class="item-title">${item.title || '-'}</div>
            <div class="item-meta"><span>${item.source || '-'}</span>${item.date ? ` · ${item.date}` : ''}</div>
            ${item.excerpt ? `<div class="item-desc">${item.excerpt}</div>` : ''}
            ${item.url ? `<a href="${item.url}" target="_blank" style="font-size:12px;color:#1a73e8;">查看原文</a>` : ''}
        </li>`).join('')}</ul>`;
}

// === Panel 4: 智能体问答 ===
function initChat() {
    // 组装 system_prompt：企业信息 + 分析结果
    let prompt = '你是一个企业背调智能助手。以下是该企业的背景信息，请基于这些信息回答用户的问题。\n\n';
    if (collectData) {
        prompt += `## 企业基本信息\n企业名称: ${collectData.accurate_name}\n`;
        const d = collectData.verify_data || {};
        if (d.Status) prompt += `经营状态: ${d.Status}\n`;
        if (d.StartDate) prompt += `成立日期: ${d.StartDate}\n`;
        if (d.RegistCapi) prompt += `注册资本: ${d.RegistCapi}\n`;
        if (d.Scope) prompt += `经营范围: ${d.Scope}\n`;
        if (d.Address) prompt += `地址: ${d.Address}\n`;
        if (d.OperName) prompt += `法定代表人: ${d.OperName}\n`;
        const ind = d.Industry || {};
        if (ind.IndustryName) prompt += `行业: ${ind.IndustryName}\n`;
    }
    if (analysisData) {
        prompt += '\n## AI 分析结果\n';
        prompt += JSON.stringify(analysisData, null, 2);
    }
    chatSystemPrompt = prompt;
    chatMessages = [];

    // 重置聊天 UI
    const messagesEl = document.getElementById('chat-messages');
    messagesEl.innerHTML = `<div class="message assistant">
        <div class="message-content">你好！我已经了解了这家企业的背景信息。你可以问我任何关于该企业的问题，比如合作切入点、风险点、决策链分析等。</div>
    </div>`;

    document.getElementById('panel-chat').style.display = 'block';
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    // 添加用户消息
    chatMessages.push({ role: 'user', content: text });
    appendMessage('user', text);
    input.value = '';

    // 切换按钮状态
    document.getElementById('send-btn').style.display = 'none';
    document.getElementById('stop-btn').style.display = 'inline-block';

    // 创建 assistant 消息容器
    const msgEl = createAssistantMessageElement();
    const contentEl = msgEl.querySelector('.message-content');
    let thinkingEl = null;
    let thinkingContent = '';
    let responseContent = '';
    let hasStartedContent = false;

    chatAbortController = new AbortController();

    try {
        const response = await fetch('/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: chatMessages,
                system_prompt: chatSystemPrompt,
                temperature: 0.7,
                max_tokens: 4096
            }),
            signal: chatAbortController.signal
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // 保留未完成的行

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith('data: ')) continue;
                const dataStr = trimmed.slice(6);

                try {
                    const data = JSON.parse(dataStr);

                    if (data.type === 'thinking') {
                        if (!thinkingEl) {
                            thinkingEl = createThinkingBlock(msgEl);
                        }
                        thinkingContent += data.content;
                        thinkingEl.querySelector('.thinking-content').textContent = thinkingContent;
                    } else if (data.type === 'token') {
                        if (!hasStartedContent && thinkingEl) {
                            thinkingEl.classList.add('collapsed');
                            hasStartedContent = true;
                        }
                        responseContent += data.content;
                        contentEl.innerHTML = responseContent + '<span class="streaming-cursor"></span>';
                        scrollChatToBottom();
                    } else if (data.type === 'done') {
                        break;
                    }
                } catch (e) {
                    // 跳过解析失败的行
                }
            }
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            responseContent += '\n[已停止]';
        } else {
            responseContent += `\n[错误: ${error.message}]`;
        }
    }

    // 移除光标，设置最终内容
    contentEl.innerHTML = responseContent || '[无响应]';
    chatMessages.push({ role: 'assistant', content: responseContent });

    // 恢复按钮状态
    document.getElementById('send-btn').style.display = 'inline-block';
    document.getElementById('stop-btn').style.display = 'none';
    chatAbortController = null;
}

function stopStream() {
    if (chatAbortController) {
        chatAbortController.abort();
    }
}

function clearChat() {
    chatMessages = [];
    const messagesEl = document.getElementById('chat-messages');
    messagesEl.innerHTML = `<div class="message assistant">
        <div class="message-content">对话已清空。你可以继续问我关于该企业的问题。</div>
    </div>`;
}

function appendMessage(role, content) {
    const messagesEl = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    msgDiv.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    messagesEl.appendChild(msgDiv);
    scrollChatToBottom();
}

function createAssistantMessageElement() {
    const messagesEl = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message assistant';
    msgDiv.innerHTML = '<div class="message-content"><span class="streaming-cursor"></span></div>';
    messagesEl.appendChild(msgDiv);
    scrollChatToBottom();
    return msgDiv;
}

function createThinkingBlock(msgEl) {
    const block = document.createElement('div');
    block.className = 'thinking-block';
    block.innerHTML = `
        <div class="thinking-header" onclick="this.parentElement.classList.toggle('collapsed')">
            <span>思考中...</span>
        </div>
        <div class="thinking-content"></div>`;
    msgEl.insertBefore(block, msgEl.querySelector('.message-content'));
    return block;
}

function scrollChatToBottom() {
    const el = document.getElementById('chat-messages');
    el.scrollTop = el.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
