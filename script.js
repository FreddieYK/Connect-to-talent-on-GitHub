// 全局变量
let currentSearchTimeout = null;
let currentRequest = null;

// API配置 - 支持多环境
const API_BASE_URL = (() => {
    // 生产环境：使用环境变量或默认后端地址
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        return window.BACKEND_URL || 'https://fredd-backend-production.up.railway.app';
    }
    // 开发环境
    return 'http://localhost:8000';
})();

// DOM元素
const elements = {
    // 分析页面元素
    searchInput: document.getElementById('search-input'),
    searchBtn: document.getElementById('search-btn'),
    contributorLimit: document.getElementById('contributor-limit'),
    searchSuggestions: document.getElementById('search-suggestions'),
    resultsSection: document.getElementById('results-section'),
    loadingOverlay: document.getElementById('loading-overlay'),
    errorModal: document.getElementById('error-modal'),
    successToast: document.getElementById('success-toast'),
    
    // 推荐页面元素
    recommendInput: document.getElementById('recommend-input'),
    recommendBtn: document.getElementById('recommend-btn'),
    charCount: document.getElementById('char-count'),
    recommendationsSection: document.getElementById('recommendations-section'),
    recommendationsContainer: document.getElementById('recommendations-container'),
    analysisInfo: document.getElementById('analysis-info'),
    analysisSummary: document.getElementById('analysis-summary'),
    analysisKeywords: document.getElementById('analysis-keywords'),
    
    // 项目信息元素
    projectName: document.getElementById('project-name'),
    projectDescription: document.getElementById('project-description'),
    projectStars: document.getElementById('project-stars'),
    projectForks: document.getElementById('project-forks'),
    projectLanguage: document.getElementById('project-language'),
    
    // 贡献者元素
    contributorsContainer: document.getElementById('contributors-container'),
    viewToggleBtns: document.querySelectorAll('.view-btn')
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeAnimations();
    setupSearchSuggestions();
});

    // 事件监听器初始化
function initializeEventListeners() {
    // 搜索相关事件
    if (elements.searchInput) {
        elements.searchInput.addEventListener('input', handleSearchInput);
        elements.searchInput.addEventListener('keypress', handleSearchKeypress);
    }
    if (elements.searchBtn) {
        elements.searchBtn.addEventListener('click', handleSearch);
    }
    
    // 推荐相关事件
    if (elements.recommendInput) {
        elements.recommendInput.addEventListener('input', handleRecommendInput);
        elements.recommendInput.addEventListener('keypress', handleRecommendKeypress);
    }
    if (elements.recommendBtn) {
        elements.recommendBtn.addEventListener('click', handleRecommend);
    }
    
    // 贡献者数量输入框事件
    if (elements.contributorLimit) {
        elements.contributorLimit.addEventListener('input', handleContributorLimitInput);
        elements.contributorLimit.addEventListener('blur', handleContributorLimitBlur);
    }
    
    // 视图切换事件
    elements.viewToggleBtns.forEach(btn => {
        btn.addEventListener('click', handleViewToggle);
    });
    
    // 点击外部关闭搜索建议
    document.addEventListener('click', function(e) {
        if (elements.searchInput && elements.searchSuggestions && 
            !elements.searchInput.contains(e.target) && !elements.searchSuggestions.contains(e.target)) {
            hideSearchSuggestions();
        }
    });
    
    // ESC键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
}

// 动画初始化
function initializeAnimations() {
    // 添加页面加载动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease-in-out';
        document.body.style.opacity = '1';
    }, 100);
    
    // 粒子动画增强
    createFloatingParticles();
}

// 创建浮动粒子
function createFloatingParticles() {
    const particleContainer = document.querySelector('.background-animation');
    
    // 检查容器是否存在，如果不存在则跳过粒子创建
    if (!particleContainer) {
        console.warn('Background animation container not found, skipping particle creation');
        return;
    }
    
    // 添加更多粒子
    for (let i = 0; i < 10; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (4 + Math.random() * 4) + 's';
        particleContainer.appendChild(particle);
    }
}

// 搜索输入处理
function handleSearchInput(e) {
    const query = e.target.value.trim();
    
    // 清除之前的搜索建议超时
    if (currentSearchTimeout) {
        clearTimeout(currentSearchTimeout);
    }
    
    if (query.length >= 2) {
        // 延迟搜索建议，避免频繁请求
        currentSearchTimeout = setTimeout(() => {
            fetchSearchSuggestions(query);
        }, 300);
    } else {
        hideSearchSuggestions();
    }
}

// 贡献者数量输入处理
function handleContributorLimitInput(e) {
    const value = parseInt(e.target.value);
    const input = e.target;
    
    // 移除之前的错误状态
    input.classList.remove('error');
    
    // 实时验证
    if (e.target.value && (isNaN(value) || value < 1 || value > 100)) {
        input.classList.add('error');
    }
}

// 贡献者数量输入框失去焦点处理
function handleContributorLimitBlur(e) {
    const value = parseInt(e.target.value);
    const input = e.target;
    
    // 如果为空或无效，设置为默认值
    if (!e.target.value || isNaN(value) || value < 1) {
        e.target.value = '10';
        input.classList.remove('error');
    } else if (value > 100) {
        e.target.value = '100';
        input.classList.remove('error');
        showWarning('最大只能显示 100 名贡献者');
    } else {
        // 确保是整数
        e.target.value = value.toString();
        input.classList.remove('error');
    }
}

// 搜索键盘事件
function handleSearchKeypress(e) {
    // Enter 键执行搜索
    if (e.key === 'Enter') {
        e.preventDefault();
        
        // 如果有选中的建议，使用选中的建议
        const selectedSuggestion = elements.searchSuggestions?.querySelector('.suggestion-item.selected');
        if (selectedSuggestion) {
            const suggestionName = selectedSuggestion.querySelector('.suggestion-name').textContent;
            selectSuggestion(suggestionName);
        } else {
            hideSearchSuggestions();
            handleSearch();
        }
    }
    // Escape 键隐藏建议
    else if (e.key === 'Escape') {
        hideSearchSuggestions();
    }
    // 上下箭头在建议中导航
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        handleSuggestionNavigation(e);
    }
}

// 建议导航（键盘上下选择）
function handleSuggestionNavigation(e) {
    if (!elements.searchSuggestions || elements.searchSuggestions.style.display === 'none') {
        return;
    }
    
    e.preventDefault();
    const items = elements.searchSuggestions.querySelectorAll('.suggestion-item');
    if (items.length === 0) return;
    
    let currentIndex = -1;
    items.forEach((item, index) => {
        if (item.classList.contains('selected')) {
            currentIndex = index;
        }
        item.classList.remove('selected');
    });
    
    if (e.key === 'ArrowDown') {
        currentIndex = (currentIndex + 1) % items.length;
    } else if (e.key === 'ArrowUp') {
        currentIndex = currentIndex <= 0 ? items.length - 1 : currentIndex - 1;
    }
    
    if (currentIndex >= 0 && currentIndex < items.length) {
        items[currentIndex].classList.add('selected');
        items[currentIndex].scrollIntoView({ block: 'nearest' });
    }
}

// 执行搜索
async function handleSearch() {
    const query = elements.searchInput.value.trim();
    
    if (!query) {
        showError('请输入要搜索的GitHub项目名称');
        return;
    }
    
    // 支持仅输入“仓库名”的情况：自动通过建议接口补全 owner/repo
    let owner = '';
    let repo = '';
    if (!query.includes('/')) {
        try {
            const resolveResp = await fetch(`${API_BASE_URL}/api/suggestions?q=${encodeURIComponent(query)}&limit=1`);
            if (resolveResp.ok) {
                const resolveData = await resolveResp.json();
                const best = (resolveData.suggestions || [])[0];
                const full = best && (best.name || best.full_name);
                if (full && full.includes('/')) {
                    [owner, repo] = full.split('/');
                } else {
                    showError('未找到匹配的仓库，请输入更准确的名称');
                    return;
                }
            } else {
                showError('建议服务不可用，请稍后重试或输入 用户名/项目名');
                return;
            }
        } catch (e) {
            showError('网络错误：无法获取仓库建议');
            return;
        }
    } else {
        [owner, repo] = query.split('/');
    }
    if (!owner || !repo) {
        showError('请输入正确的项目名称或 用户名/项目名');
        return;
    }
    
    const limitValue = elements.contributorLimit.value.trim();
    const limit = parseInt(limitValue) || 10;
    
    // 验证数量范围
    if (limit < 1 || limit > 100) {
        showError('贡献者数量必须在 1-100 之间');
        elements.contributorLimit.focus();
        return;
    }
    
    // 隐藏搜索建议
    hideSearchSuggestions();
    
    // 显示加载动画
    showLoading();
    
    try {
        // 取消之前的请求
        if (currentRequest) {
            currentRequest.abort();
        }
        
        // 创建新的请求控制器
        const controller = new AbortController();
        currentRequest = controller;
        
        // 更新加载步骤
        updateLoadingStep(0);
        
        // 获取贡献者数据
        const response = await fetch(`${API_BASE_URL}/api/contributors/${owner}/${repo}?limit=${limit}`, {
            signal: controller.signal
        });
        
        updateLoadingStep(1);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        updateLoadingStep(2);
        
        // 短暂延迟以显示完成状态
        setTimeout(() => {
            hideLoading();
            displayResults(data);
            showSuccess('数据分析完成！');
        }, 500);
        
    } catch (error) {
        hideLoading();
        
        if (error.name === 'AbortError') {
            return; // 请求被取消，不显示错误
        }
        
        console.error('Search error:', error);
        
        let errorMessage = '获取数据时发生错误';
        
        if (error.message.includes('404')) {
            errorMessage = '未找到指定的GitHub项目，请检查项目名称是否正确';
        } else if (error.message.includes('403')) {
            errorMessage = 'API访问受限，请稍后重试';
        } else if (error.message.includes('500')) {
            errorMessage = '服务器内部错误，请稍后重试';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = '网络连接错误，请检查网络连接';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showError(errorMessage);
    } finally {
        currentRequest = null;
    }
}

// 获取搜索建议
async function fetchSearchSuggestions(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/suggestions?q=${encodeURIComponent(query)}&limit=5`);
        
        if (!response.ok) {
            return;
        }
        
        const data = await response.json();
        displaySearchSuggestions(data.suggestions || []);
        
    } catch (error) {
        console.warn('Failed to fetch suggestions:', error);
        hideSearchSuggestions();
    }
}

// 显示搜索建议
function displaySearchSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) {
        hideSearchSuggestions();
        return;
    }
    
    const html = suggestions.map(suggestion => {
        const description = suggestion.description && suggestion.description.length > 60 
            ? suggestion.description.substring(0, 60) + '...'
            : (suggestion.description || '暂无描述');
        
        return `
            <div class="suggestion-item" onclick="selectSuggestion('${escapeHtml(suggestion.name || suggestion.full_name)}')"
                 onmousedown="event.preventDefault()">
                <div class="suggestion-header">
                    <div class="suggestion-name">${escapeHtml(suggestion.name || suggestion.full_name)}</div>
                    <div class="suggestion-stats">
                        ${suggestion.stars > 0 ? `<span class="suggestion-stars"><i class="fas fa-star"></i> ${formatNumber(suggestion.stars)}</span>` : ''}
                        ${suggestion.language ? `<span class="suggestion-language">${escapeHtml(suggestion.language)}</span>` : ''}
                    </div>
                </div>
                <div class="suggestion-description">${escapeHtml(description)}</div>
            </div>
        `;
    }).join('');
    
    elements.searchSuggestions.innerHTML = html;
    elements.searchSuggestions.style.display = 'block';
}

// 选择搜索建议
function selectSuggestion(fullName) {
    elements.searchInput.value = fullName;
    hideSearchSuggestions();
    
    // 等待一个简短的延迟后自动执行搜索
    setTimeout(() => {
        handleSearch();
    }, 150);
}

// 隐藏搜索建议
function hideSearchSuggestions() {
    elements.searchSuggestions.style.display = 'none';
}

// 设置搜索建议
function setupSearchSuggestions() {
    // 预设一些热门项目建议
    const popularProjects = [
        'microsoft/vscode',
        'facebook/react',
        'vuejs/vue',
        'angular/angular',
        'nodejs/node',
        'tensorflow/tensorflow',
        'pytorch/pytorch',
        'kubernetes/kubernetes'
    ];
    
    elements.searchInput.addEventListener('focus', function() {
        if (!this.value.trim()) {
            const suggestions = popularProjects.slice(0, 5).map(project => ({
                full_name: project,
                description: '热门开源项目'
            }));
            displaySearchSuggestions(suggestions);
        }
    });
}

// 显示结果
function displayResults(data) {
    // 显示项目信息
    displayProjectInfo(data.repository);
    
    // 显示贡献者列表
    displayContributors(data.contributors);
    
    // 显示结果区域
    elements.resultsSection.style.display = 'block';
    
    // 滚动到结果区域
    elements.resultsSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// 显示项目信息
function displayProjectInfo(repository) {
    elements.projectName.textContent = repository.full_name;
    elements.projectDescription.textContent = repository.description || '暂无描述';
    elements.projectStars.textContent = formatNumber(repository.stars);
    elements.projectForks.textContent = formatNumber(repository.forks);
    elements.projectLanguage.textContent = repository.language || '未知';
}

// 显示贡献者
function displayContributors(contributors) {
    const html = contributors.map((contributor, index) => 
        createContributorCard(contributor, index + 1)
    ).join('');
    
    elements.contributorsContainer.innerHTML = html;
    
    // 为卡片添加延迟动画
    const cards = elements.contributorsContainer.querySelectorAll('.contributor-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // 异步获取每个贡献者的关注者数据
    loadContributorsFollowersData(contributors);
}

// 异步加载贡献者的关注者数据
async function loadContributorsFollowersData(contributors) {
    logger.info('开始加载贡献者关注者数据...');
    
    // 并发请求，但限制数量避免过多请求
    const promises = contributors.slice(0, 10).map(async (contributor, index) => {
        try {
            // 添加小延迟避免同时发起太多请求
            await new Promise(resolve => setTimeout(resolve, index * 200));
            
            const response = await fetch(`${API_BASE_URL}/api/profile/${contributor.username}`);
            
            if (response.ok) {
                const profile = await response.json();
                updateContributorFollowers(contributor.username, profile.followers);
                logger.info(`更新 ${contributor.username} 的关注者数: ${profile.followers}`);
            } else {
                logger.warning(`获取 ${contributor.username} 的资料失败: ${response.status}`);
                updateContributorFollowers(contributor.username, 0);
            }
        } catch (error) {
            logger.error(`获取 ${contributor.username} 的关注者数据失败:`, error);
            updateContributorFollowers(contributor.username, 0);
        }
    });
    
    // 等待所有请求完成
    await Promise.allSettled(promises);
    logger.info('所有贡献者的关注者数据加载完成');
}

// 更新贡献者卡片中的关注者数据
function updateContributorFollowers(username, followers) {
    const followersElement = document.getElementById(`followers-${username}`);
    if (followersElement) {
        // 移除加载动画并更新数据
        followersElement.innerHTML = formatNumber(followers);
        
        // 添加一个小动画效果
        followersElement.style.transition = 'all 0.3s ease';
        followersElement.style.transform = 'scale(1.1)';
        followersElement.style.color = 'var(--primary-color)';
        
        setTimeout(() => {
            followersElement.style.transform = 'scale(1)';
            followersElement.style.color = '';
        }, 300);
    }
}

// 添加日志输出函数
const logger = {
    info: (message, ...args) => console.log(`[INFO] ${message}`, ...args),
    warning: (message, ...args) => console.warn(`[WARNING] ${message}`, ...args),
    error: (message, ...args) => console.error(`[ERROR] ${message}`, ...args)
};

// 创建贡献者卡片
function createContributorCard(contributor, rank) {
    const rankClass = rank <= 3 ? `rank-${rank}` : '';
    
    return `
        <div class="contributor-card" onclick="openContributorProfile('${contributor.username}')">
            <div class="contributor-rank ${rankClass}">${rank}</div>
            <div class="contributor-header">
                <img 
                    src="${contributor.avatar_url}" 
                    alt="${contributor.username}" 
                    class="contributor-avatar"
                    onerror="this.src='https://github.com/identicons/${contributor.username}.png'"
                >
                <div class="contributor-info">
                    <h4>${escapeHtml(contributor.username)}</h4>
                    <p>@${escapeHtml(contributor.username)}</p>
                </div>
            </div>
            <div class="contributor-stats">
                <div class="stat-box">
                    <span class="stat-number">${formatNumber(contributor.contributions)}</span>
                    <span class="stat-text">提交次数</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number" id="followers-${contributor.username}">
                        <i class="fas fa-spinner fa-spin" style="font-size: 12px; color: var(--text-muted);"></i>
                    </span>
                    <span class="stat-text">关注者</span>
                </div>
            </div>
        </div>
    `;
}

// 打开贡献者详细资料
async function openContributorProfile(username) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/profile/${username}`);
        
        if (!response.ok) {
            throw new Error('获取用户资料失败');
        }
        
        const profile = await response.json();
        hideLoading();
        showContributorModal(profile);
        
    } catch (error) {
        hideLoading();
        showError('获取用户详细信息失败：' + error.message);
    }
}

// 显示贡献者模态框
function showContributorModal(profile) {
    const modalHtml = `
        <div class="modal" id="contributor-modal" style="display: block;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${escapeHtml(profile.name || profile.username)}</h3>
                    <button class="modal-close" onclick="closeModal('contributor-modal')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                        <img 
                            src="${profile.avatar_url}" 
                            alt="${profile.username}" 
                            style="width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--border-color);"
                        >
                        <div>
                            <h4 style="margin: 0;">${escapeHtml(profile.name || profile.username)}</h4>
                            <p style="margin: 5px 0; color: var(--text-muted);">@${escapeHtml(profile.username)}</p>
                            ${profile.pronouns ? `<p style="margin: 5px 0; color: var(--text-muted); font-style: italic;">${escapeHtml(profile.pronouns)}</p>` : ''}
                            ${profile.bio ? `<p style="margin: 10px 0;">${escapeHtml(profile.bio)}</p>` : ''}
                            ${profile.work_info ? `<p style="margin: 10px 0; color: var(--text-muted);"><i class="fas fa-briefcase"></i> ${escapeHtml(profile.work_info)}</p>` : ''}
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div class="stat-box">
                            <span class="stat-number">${formatNumber(profile.followers)}</span>
                            <span class="stat-text">关注者</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number">${formatNumber(profile.following)}</span>
                            <span class="stat-text">关注中</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number">${formatNumber(profile.public_repos)}</span>
                            <span class="stat-text">公开仓库</span>
                        </div>
                        ${profile.additional_info?.contributions?.total_contributions ? `
                        <div class="stat-box">
                            <span class="stat-number">${formatNumber(profile.additional_info.contributions.total_contributions)}</span>
                            <span class="stat-text">总贡献</span>
                        </div>
                        ` : ''}
                    </div>
                    
                    ${generateContactSection(profile)}
                    ${generateSocialSection(profile)}
                    ${generateAdditionalInfoSection(profile)}
                    
                    <div style="margin-top: 20px; text-align: center;">
                        <a href="https://github.com/${profile.username}" target="_blank" 
                           style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; 
                                  background: var(--primary-color); color: white; text-decoration: none; 
                                  border-radius: 8px; font-weight: 500;">
                            <i class="fab fa-github"></i>
                            查看GitHub主页
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 添加到页面
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// 生成联系信息部分
function generateContactSection(profile) {
    const contactItems = [];
    
    if (profile.company) {
        contactItems.push(`<p><i class="fas fa-building"></i> ${escapeHtml(profile.company)}</p>`);
    }
    if (profile.location) {
        contactItems.push(`<p><i class="fas fa-map-marker-alt"></i> ${escapeHtml(profile.location)}</p>`);
    }
    if (profile.email) {
        contactItems.push(`<p><i class="fas fa-envelope"></i> <a href="mailto:${profile.email}">${escapeHtml(profile.email)}</a></p>`);
    }
    if (profile.blog || profile.website) {
        const url = profile.blog || profile.website;
        contactItems.push(`<p><i class="fas fa-link"></i> <a href="${url}" target="_blank">${escapeHtml(url)}</a></p>`);
    }
    if (profile.created_at || profile.additional_info?.join_date) {
        const joinDate = profile.created_at || profile.additional_info.join_date;
        contactItems.push(`<p><i class="fas fa-calendar-alt"></i> 加入于 ${escapeHtml(joinDate)}</p>`);
    }
    
    if (contactItems.length > 0) {
        return `
            <div style="border-top: 1px solid var(--border-color); padding-top: 20px; margin-bottom: 20px;">
                <h4><i class="fas fa-address-card"></i> 联系信息</h4>
                ${contactItems.join('')}
            </div>
        `;
    }
    
    return '';
}

// 生成社交媒体部分
function generateSocialSection(profile) {
    const socialItems = [];
    
    const socialPlatforms = {
        'twitter': { icon: 'fab fa-twitter', name: 'Twitter', color: '#1DA1F2' },
        'linkedin': { icon: 'fab fa-linkedin', name: 'LinkedIn', color: '#0077B5' },
        'mastodon': { icon: 'fab fa-mastodon', name: 'Mastodon', color: '#6364FF' },
        'instagram': { icon: 'fab fa-instagram', name: 'Instagram', color: '#E4405F' },
        'facebook': { icon: 'fab fa-facebook', name: 'Facebook', color: '#1877F2' },
        'youtube': { icon: 'fab fa-youtube', name: 'YouTube', color: '#FF0000' },
        'stackoverflow': { icon: 'fab fa-stack-overflow', name: 'Stack Overflow', color: '#F58025' },
        'devto': { icon: 'fab fa-dev', name: 'Dev.to', color: '#0A0A0A' },
        'medium': { icon: 'fab fa-medium', name: 'Medium', color: '#12100E' }
    };
    
    for (const [platform, config] of Object.entries(socialPlatforms)) {
        if (profile[platform] || profile.social_links?.[platform]) {
            const url = profile[platform] || profile.social_links[platform];
            const username = profile.contact_info?.social_accounts?.find(acc => acc.platform === platform)?.username || '';
            
            socialItems.push(`
                <a href="${url}" target="_blank" class="social-link" 
                   style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; 
                          margin: 4px; border-radius: 6px; text-decoration: none; 
                          background: ${config.color}15; color: ${config.color}; 
                          border: 1px solid ${config.color}30; transition: all 0.2s;" 
                   onmouseover="this.style.background='${config.color}25'" 
                   onmouseout="this.style.background='${config.color}15'">
                    <i class="${config.icon}"></i>
                    <span>${config.name}${username ? ` (${username})` : ''}</span>
                </a>
            `);
        }
    }
    
    if (socialItems.length > 0) {
        return `
            <div style="border-top: 1px solid var(--border-color); padding-top: 20px; margin-bottom: 20px;">
                <h4><i class="fas fa-share-alt"></i> 社交媒体</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    ${socialItems.join('')}
                </div>
            </div>
        `;
    }
    
    return '';
}

// 生成额外信息部分
function generateAdditionalInfoSection(profile) {
    const sections = [];
    
    // 组织信息
    if (profile.additional_info?.organizations?.length > 0) {
        const orgItems = profile.additional_info.organizations.map(org => `
            <div style="display: flex; align-items: center; gap: 8px; margin: 8px 0;">
                ${org.avatar_url ? `<img src="${org.avatar_url}" alt="${org.name}" style="width: 24px; height: 24px; border-radius: 4px;">` : '<i class="fas fa-building"></i>'}
                <a href="${org.url}" target="_blank" style="color: var(--primary-color); text-decoration: none;">${escapeHtml(org.name)}</a>
            </div>
        `).join('');
        
        sections.push(`
            <div style="margin-bottom: 20px;">
                <h5><i class="fas fa-users"></i> 组织</h5>
                ${orgItems}
            </div>
        `);
    }
    
    // 置顶仓库
    if (profile.additional_info?.pinned_repositories?.length > 0) {
        const repoItems = profile.additional_info.pinned_repositories.map(repo => `
            <div style="border: 1px solid var(--border-color); border-radius: 6px; padding: 12px; margin: 8px 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <i class="fas fa-book"></i>
                    <a href="${repo.url}" target="_blank" style="color: var(--primary-color); text-decoration: none; font-weight: 500;">${escapeHtml(repo.name)}</a>
                    ${repo.language ? `<span style="background: var(--bg-tertiary); padding: 2px 6px; border-radius: 12px; font-size: 12px;">${escapeHtml(repo.language)}</span>` : ''}
                </div>
                ${repo.description ? `<p style="margin: 0; color: var(--text-muted); font-size: 14px;">${escapeHtml(repo.description)}</p>` : ''}
            </div>
        `).join('');
        
        sections.push(`
            <div style="margin-bottom: 20px;">
                <h5><i class="fas fa-thumbtack"></i> 置顶仓库</h5>
                ${repoItems}
            </div>
        `);
    }
    
    if (sections.length > 0) {
        return `
            <div style="border-top: 1px solid var(--border-color); padding-top: 20px;">
                ${sections.join('')}
            </div>
        `;
    }
    
    return '';
}

// 视图切换处理
function handleViewToggle(e) {
    const view = e.target.closest('.view-btn').dataset.view;
    
    // 更新按钮状态
    elements.viewToggleBtns.forEach(btn => btn.classList.remove('active'));
    e.target.closest('.view-btn').classList.add('active');
    
    // 切换视图
    if (view === 'list') {
        elements.contributorsContainer.classList.add('list-view');
    } else {
        elements.contributorsContainer.classList.remove('list-view');
    }
}

// 更新加载步骤
function updateLoadingStep(stepIndex) {
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach((step, index) => {
        if (index <= stepIndex) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

// 显示加载动画
function showLoading() {
    elements.loadingOverlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// 隐藏加载动画
function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// 显示错误信息
function showError(message) {
    document.getElementById('error-message').textContent = message;
    elements.errorModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// 关闭错误模态框
function closeError() {
    elements.errorModal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// 显示成功提示
function showSuccess(message) {
    document.getElementById('success-message').textContent = message;
    elements.successToast.style.display = 'flex';
    
    // 3秒后自动隐藏
    setTimeout(() => {
        elements.successToast.style.display = 'none';
    }, 3000);
}

// 显示警告提示
function showWarning(message) {
    // 创建警告提示元素（如果不存在）
    let warningToast = document.getElementById('warning-toast');
    if (!warningToast) {
        warningToast = document.createElement('div');
        warningToast.id = 'warning-toast';
        warningToast.className = 'warning-toast';
        warningToast.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span id="warning-message"></span>
        `;
        document.body.appendChild(warningToast);
    }
    
    document.getElementById('warning-message').textContent = message;
    warningToast.style.display = 'flex';
    
    // 3秒后自动隐藏
    setTimeout(() => {
        warningToast.style.display = 'none';
    }, 3000);
}

// 关闭所有模态框
function closeAllModals() {
    const modals = document.querySelectorAll('.modal, .error-modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
    document.body.style.overflow = 'auto';
}

// 关闭指定模态框
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
    document.body.style.overflow = 'auto';
}

// 显示关于模态框
function showAbout() {
    document.getElementById('about-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// 显示帮助模态框
function showHelp() {
    document.getElementById('help-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// 工具函数

// 格式化数字
function formatNumber(num) {
    // 处理 undefined、null 或非数字值
    if (num === undefined || num === null || isNaN(num)) {
        return '0';
    }
    
    // 确保是数字类型
    const number = Number(num);
    
    if (number >= 1000000) {
        return (number / 1000000).toFixed(1) + 'M';
    } else if (number >= 1000) {
        return (number / 1000).toFixed(1) + 'K';
    } else {
        return number.toString();
    }
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// 添加键盘快捷键支持
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K 聚焦搜索框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        elements.searchInput.focus();
        elements.searchInput.select();
    }
    
    // Ctrl/Cmd + Enter 执行搜索
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleSearch();
    }
});

// 添加页面可见性变化处理
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // 页面不可见时取消正在进行的请求
        if (currentRequest) {
            currentRequest.abort();
            currentRequest = null;
        }
    }
});

// 添加错误处理
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (currentRequest) {
        currentRequest.abort();
    }
    
    if (currentSearchTimeout) {
        clearTimeout(currentSearchTimeout);
    }
});

// 检查API连接状态
async function checkApiStatus() {
    try {
        // 创建带超时的fetch请求
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
        
        const response = await fetch(`${API_BASE_URL}/api/health`, {
            signal: controller.signal,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            console.log('API服务连接正常');
            return true;
        } else {
            console.warn(`API服务响应异常: ${response.status}`);
            return false;
        }
    } catch (error) {
        console.error('API连接检查失败:', error);
        if (error.name === 'AbortError') {
            console.warn('API连接超时');
        }
        return false;
    }
}

// 页面加载完成后检查API状态
window.addEventListener('load', async function() {
    console.log('正在检查API连接状态...');
    console.log('API_BASE_URL:', API_BASE_URL);
    
    const apiStatus = await checkApiStatus();
    if (!apiStatus) {
        console.error('API服务连接失败');
        showWarning(`网络连接错误：无法连接到后端服务 (${API_BASE_URL})。请检查：\n1. 网络连接是否正常\n2. 后端服务是否运行\n3. API地址是否正确`);
    } else {
        console.log('API服务连接成功');
    }
});

// 添加服务工作者支持（PWA）
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // 这里可以注册service worker
        // navigator.serviceWorker.register('/sw.js');
    });
}

// ====================== Tab切换功能 ======================

// Tab切换函数
function switchTab(tabName) {
    // 隐藏所有Tab内容
    const allTabContents = document.querySelectorAll('.tab-content');
    allTabContents.forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
    });
    
    // 移除所有Tab按钮的激活状态
    const allTabButtons = document.querySelectorAll('.nav-tab');
    allTabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 显示目标Tab内容
    const targetTab = document.getElementById(`${tabName}-tab`);
    if (targetTab) {
        targetTab.style.display = 'block';
        targetTab.classList.add('active');
    }
    
    // 激活对应的Tab按钮
    const targetButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (targetButton) {
        targetButton.classList.add('active');
    }
    
    // 更新页面标题
    if (tabName === 'analyzer') {
        document.title = 'GitHub 项目分析工具 - 发现开源力量';
    } else if (tabName === 'recommender') {
        document.title = 'AI 项目推荐系统 - 智能推荐GitHub项目';
    }
}

// ====================== 项目推荐功能 ======================

// 推荐输入处理
function handleRecommendInput(e) {
    const text = e.target.value;
    const charCount = text.length;
    const maxChars = 500;
    
    // 更新字符计数
    if (elements.charCount) {
        elements.charCount.textContent = `${charCount}/${maxChars}`;
        
        // 根据字符数量改变颜色
        elements.charCount.className = 'char-count';
        if (charCount > maxChars * 0.8) {
            elements.charCount.classList.add('warning');
        }
        if (charCount > maxChars * 0.9) {
            elements.charCount.classList.add('danger');
        }
    }
    
    // 限制字符数量
    if (charCount > maxChars) {
        e.target.value = text.substring(0, maxChars);
        if (elements.charCount) {
            elements.charCount.textContent = `${maxChars}/${maxChars}`;
            elements.charCount.className = 'char-count danger';
        }
    }
}

// 推荐键盘事件
function handleRecommendKeypress(e) {
    // Enter 键执行推荐（支持 Shift+Enter 换行）
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleRecommend();
    }
    // Ctrl/Cmd + Enter 也可以执行推荐
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleRecommend();
    }
}

// 设置快速查询
function setQuickQuery(query) {
    if (elements.recommendInput) {
        elements.recommendInput.value = query;
        elements.recommendInput.focus();
        
        // 触发input事件以更新字符计数
        const event = new Event('input', { bubbles: true });
        elements.recommendInput.dispatchEvent(event);
    }
}

// 执行项目推荐
async function handleRecommend() {
    const query = elements.recommendInput ? elements.recommendInput.value.trim() : '';
    
    if (!query) {
        showError('请描述您的技术需求');
        return;
    }
    
    // 移除字符数量限制，支持任意长度输入
    // 对于非常短的输入，AI也能提供有用的推荐
    
    // 显示加载动画
    showLoading();
    updateLoadingTitle('正在分析需求...');
    
    try {
        // 取消之前的请求
        if (currentRequest) {
            currentRequest.abort();
        }
        
        // 创建新的请求控制器
        const controller = new AbortController();
        currentRequest = controller;
        
        updateLoadingTitle('正在搜索匹配的项目...');
        
        // 调用推荐API
        const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                limit: 5
            }),
            signal: controller.signal
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        updateLoadingTitle('正在生成推荐结果...');
        
        // 短暂延迟以显示完成状态
        setTimeout(() => {
            hideLoading();
            displayRecommendations(data);
            showSuccess('推荐生成完成！');
        }, 500);
        
    } catch (error) {
        hideLoading();
        
        if (error.name === 'AbortError') {
            return; // 请求被取消，不显示错误
        }
        
        console.error('Recommendation error:', error);
        
        let errorMessage = '获取推荐时发生错误';
        
        if (error.message.includes('500')) {
            errorMessage = '服务器内部错误，请稍后重试';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = '网络连接错误，请检查网络连接';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showError(errorMessage);
    } finally {
        currentRequest = null;
    }
}

// 显示推荐结果
function displayRecommendations(data) {
    if (!elements.recommendationsContainer) {
        return;
    }
    
    // 隐藏需求分析结果（根据用户要求）
    if (elements.analysisInfo) {
        elements.analysisInfo.style.display = 'none';
    }
    
    // 显示推荐项目
    if (data.recommendations && data.recommendations.length > 0) {
        const html = data.recommendations.map((project, index) => 
            createRecommendationCard(project, index + 1)
        ).join('');
        
        elements.recommendationsContainer.innerHTML = html;
        
        // 为卡片添加延迟动画
        const cards = elements.recommendationsContainer.querySelectorAll('.recommendation-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.2}s`;
        });
    } else {
        elements.recommendationsContainer.innerHTML = `
            <div class="recommendations-empty">
                <i class="fas fa-search"></i>
                <h3>暂无推荐结果</h3>
                <p>请尝试使用不同的关键词描述您的需求</p>
            </div>
        `;
    }
    
    // 显示推荐结果区域
    if (elements.recommendationsSection) {
        elements.recommendationsSection.style.display = 'block';
        
        // 滚动到结果区域
        elements.recommendationsSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 显示需求分析信息
function displayAnalysisInfo(analysis) {
    if (analysis.summary && elements.analysisSummary) {
        elements.analysisSummary.textContent = analysis.summary;
    }
    
    if (analysis.keywords && elements.analysisKeywords) {
        const keywordsHtml = analysis.keywords.map(keyword => 
            `<span class="keyword-tag">${escapeHtml(keyword)}</span>`
        ).join('');
        elements.analysisKeywords.innerHTML = keywordsHtml;
    }
}

// 创建推荐项目卡片
function createRecommendationCard(project, rank) {
    const repoUrl = `https://github.com/${project.repository}`;
    
    // 处理描述文本，将\n\n转换为实际换行
    const formattedDescription = (project.description || '暂无描述')
        .replace(/\\n\\n/g, '\n\n')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    return `
        <div class="recommendation-card">
            <div class="recommendation-header">
                <div class="recommendation-icon">
                    <i class="fab fa-github"></i>
                </div>
                <div class="recommendation-info">
                    <h3 class="recommendation-title">
                        <span class="project-name-clickable" onclick="analyzeProject('${project.repository}')" title="点击分析项目贡献者">
                            ${escapeHtml(project.name || project.repository.split('/')[1])}
                        </span>
                        <a href="${repoUrl}" target="_blank" class="repo-link" onclick="event.stopPropagation()">
                            <i class="fab fa-github"></i>
                            ${escapeHtml(project.repository)}
                        </a>
                    </h3>
                </div>
            </div>
            <div class="recommendation-description">
                ${formattedDescription}
            </div>
            <div class="recommendation-stats">
                ${project.stars ? `
                <div class="recommendation-stat">
                    <i class="fas fa-star"></i>
                    <span class="stat-value">${formatNumber(project.stars)}</span>
                    <span class="stat-label">Stars</span>
                </div>
                ` : ''}
                ${project.forks ? `
                <div class="recommendation-stat">
                    <i class="fas fa-code-branch"></i>
                    <span class="stat-value">${formatNumber(project.forks)}</span>
                    <span class="stat-label">Forks</span>
                </div>
                ` : ''}
                ${project.language ? `
                <div class="recommendation-stat">
                    <i class="fas fa-code"></i>
                    <span class="stat-value">${escapeHtml(project.language)}</span>
                    <span class="stat-label">Language</span>
                </div>
                ` : ''}
                <div class="recommendation-stat">
                    <i class="fas fa-medal"></i>
                    <span class="stat-value">#${rank}</span>
                    <span class="stat-label">推荐</span>
                </div>
            </div>
        </div>
    `;
}

// 更新加载标题
function updateLoadingTitle(title) {
    const loadingTitle = document.querySelector('.loading-title');
    if (loadingTitle) {
        loadingTitle.textContent = title || '正在加载...';
    }
}

// ====================== 项目交互分析功能 ======================

// 分析项目函数 - 从推荐页面跳转到分析页面
function analyzeProject(repository) {
    try {
        // 切换到项目分析Tab
        switchTab('analyzer');
        
        // 填入项目名称
        if (elements.searchInput) {
            elements.searchInput.value = repository;
            elements.searchInput.focus();
        }
        
        // 添加视觉反馈，显示正在分析
        if (elements.searchInput) {
            elements.searchInput.style.border = '2px solid var(--primary-color)';
            elements.searchInput.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1)';
            
            // 1秒后恢复样式
            setTimeout(() => {
                elements.searchInput.style.border = '';
                elements.searchInput.style.boxShadow = '';
            }, 1000);
        }
        
        // 稍微延迟后自动执行搜索，让用户看到切换过程
        setTimeout(() => {
            handleSearch();
        }, 300);
        
        // 显示成功提示
        showSuccess(`正在分析项目 ${repository} 的贡献者信息...`);
        
    } catch (error) {
        console.error('分析项目失败:', error);
        showError('切换到项目分析页面失败，请手动切换并输入项目名称');
    }
}