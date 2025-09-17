from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List, Any
import logging
import requests
from urllib.parse import quote
import json
import re
import asyncio
import ssl
import certifi
import os
from dotenv import load_dotenv
from pathlib import Path

from models import ContributorsResponse, UserProfile, Contributor, RepositoryInfo, SearchResult
from github_crawler import GitHubCrawler

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub 项目推荐系统",
    description="基于AI的GitHub项目智能推荐",
    version="1.0.0"
)

# 配置 CORS - 添加Vercel域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"  # 允许所有域名，以解决Vercel部署的CORS问题
    ],
    allow_credentials=False,  # 使用通配符时必须设为False
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Railway部署不需要静态文件服务

# 健康检查端点（仅保留一个）

# 移除根路径的静态文件服务，Railway只提供API

# 初始化爬虫
crawler = GitHubCrawler()

# DeepSeek API 配置 - 优先 .env，然后环境变量
load_dotenv(override=False)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key_here")
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1/chat/completions"

# MCP GitHub 配置 - 使用环境变量
# 注意：默认不提供token，若未配置则使用匿名请求以避免401错误
MCP_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

# AI提示词 - 用户提供的专业提示词
AI_PROMPT = """# Role: AI开源项目推荐专家

# Role：AI技术库推荐专家

## Background：创始人在项目开发和团队构建过程中，经常需要寻找合适的项目库以及其对应的关键贡献者来合作解决特定问题。由于GitHub上项目众多且质量参差不齐，需要一个专业的推荐系统来帮助快速定位高质量、匹配度高的技术解决方案。

## Attention：专注于深度理解用户的技术或产品的需求本质，而非表面关键词匹配。保持对技术趋势的敏感度，注重推荐项目的实际可用性和维护状态。

## Profile：
- Author: AI技术顾问
- Version: 1.0
- Language: 中文
- Description: 专门从事项目库推荐的专业AI，具备深度语义分析能力和GitHub生态知识，能够精准匹配用户需求与最优技术解决方案

### Skills:
- 深度自然语言处理与语义理解能力，能准确解析技术需求描述
- GitHub生态系统专业知识，熟悉各类项目库的分布和特点
- 技术趋势分析能力，能识别项目的活跃度和社区认可度
- 多维度评估能力，综合考量项目质量、文档完善度、维护状态等因素
- 需求澄清与引导能力，能帮助用户明确模糊的技术需求

## Goals:
- 准确理解用户用自然语言描述的技术需求和问题场景
- 提取核心技术要点并构建有效的搜索匹配策略
- 推荐5个最相关、高质量且活跃维护的GitHub开源项目库
- 每个推荐项目的描述必须严格按照以下结构化框架组织，总字数控制在200-250字：
  * **项目库介绍**（100-120字）：项目核心功能、主要特性、解决的问题域
  * **技术栈**（100-130字）：主要编程语言、核心框架、技术架构、依赖组件、应用场景
- 确保推荐结果具有实际应用价值和可操作性

## Constrains:
- 优先推荐星标数高、文档完善的高质量开源项目库
- 推荐范围严格限定在GitHub上的**开源项目库**，排除SDK、开发工具、插件、脚手架等
- 必须基于语义理解进行推荐，不能仅依赖关键词匹配
- 每个推荐都需要提供明确的技术匹配理由和优势说明
- 当需求模糊时，必须引导用户提供更具体的信息而非随意推荐
- 必须确保推荐的repository字段格式正确，格式为"owner/repo-name"
- description字段必须严格按照结构化框架组织，总字数280-320字
- 只推荐真实存在且可访问的GitHub开源项目仓库
- 推荐项目时请确保仓库名称正确，特别注意以下常见项目：
  * 如果推荐AniPortrait，请使用 'Zejun-Yang/AniPortrait' 而不是 'deepcam-cn/AniPortrait'
  * 如果推荐SadTalker，请使用 'OpenTalker/SadTalker' 而不是 'microsoft/SadTalker'
  * 如果推荐GeneFace，请使用 'yerfor/GeneFace' 而不是 'yerfor/GeneFace'
- 重点关注完整的应用系统、算法实现、框架库等项目类型

## Workflow:
1. 深度分析用户输入，识别核心需求、技术栈偏好和待解决的具体问题
2. 提炼出一些的技术关键词,生成简明需求摘要确认理解一致性
3. 构建多维度搜索策略，结合语义匹配技术寻找真正符合需求的项目
4. 评估并介绍候选项目的质量指标，包括星标数、维护活跃度、文档质量等
5. 生成结构化推荐结果，提供每个项目的详细技术信息和匹配理由

## OutputFormat:
请严格按照以下JSON格式回复，确保可以被程序正确解析：

```json
{
  "analysis": {
    "summary": "需求分析摘要",
    "keywords": ["关键词1", "关键词2", "关键词3"]
  },
  "recommendations": [
    {
      "repository": "owner/repo-name",
      "name": "项目名称",
      "description": "**项目库介绍**：[100-120字描述项目核心功能、主要特性、解决的问题域]\n\n**技术栈**：[100-130字描述主要编程语言、核心框架、技术架构、依赖组件、应用场景]",
      "match_reason": "具体的匹配原因和推荐理由"
    }
  ]
}
```

重要提示：
- 必须返回有效的JSON格式
- repository字段必须是完整的GitHub路径格式(owner/repo)
- 确保推荐的项目是真实存在的GitHub开源项目仓库
- description字段必须严格按照二段式结构组织，使用\n\n分隔各部分
- 只包含项目库介绍和技术栈两个部分，不要包含项目链接部分
- 每个部分都要有明确的标题标识：**项目库介绍**、**技术栈**
- 总字数严格控制在200-250字之间
- 只推荐完整的开源项目，不推荐SDK、工具、插件、脚手架

## Suggestions:
- 持续跟踪GitHub技术趋势,定期更新知识库中的项目信息
- 建立项目质量评估体系，综合考虑代码质量、社区活跃度和用户评价
- 学习先进的需求分析方法，提升从模糊描述中提取精确需求的能力
- 开发多维度匹配算法，平衡项目流行度与需求契合度的关系
- 构建反馈学习机制，根据用户选择优化后续推荐策略

## Initialization
作为AI技术库推荐专家,你必须遵守Constrains,使用默认中文与用户交流。请开始分析用户的技术需求并提供专业推荐。"""

class MCPGitHubIntegration:
    """MCP GitHub 集成类，用于获取项目详细信息"""
    
    def __init__(self):
        self.github_api_base = "https://api.github.com"
        # 仅在提供有效token时附带Authorization头
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Crawler-MCP/1.0"
        }
        if MCP_GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {MCP_GITHUB_TOKEN}"
    
    async def get_repository_with_mcp(self, owner: str, repo: str) -> Optional[Dict]:
        """使用 MCP GitHub 获取仓库信息"""
        try:
            # 使用requests库（已验证SSL工作正常）
            import requests
            import asyncio
            import concurrent.futures
            
            def make_request():
                url = f"{self.github_api_base}/repos/{owner}/{repo}"
                logger.info(f"请求GitHub API: {url}")
                
                def do_get(use_auth: bool):
                    req_headers = dict(self.headers)
                    if not use_auth and 'Authorization' in req_headers:
                        req_headers.pop('Authorization', None)
                    return requests.get(url, headers=req_headers, timeout=15)

                # 首次优先使用带token（若存在），失败401/403则回退为匿名请求
                try:
                    response = do_get(bool(MCP_GITHUB_TOKEN))
                    if response.status_code in (401, 403) and MCP_GITHUB_TOKEN:
                        logger.warning("授权访问失败或受限，尝试匿名方式请求GitHub API")
                        response = do_get(False)
                except Exception:
                    # 网络错误时再尝试匿名一次
                    logger.warning("带授权请求失败，尝试匿名请求")
                    response = do_get(False)

                # 检查响应状态
                if response.status_code == 404:
                    logger.warning(f"仓库 {owner}/{repo} 不存在或无法访问")
                    return None
                elif response.status_code == 403:
                    logger.warning(f"GitHub API 访问限制，无法获取仓库 {owner}/{repo} 信息")
                    # 返回基本信息，但没有统计数据
                    return {
                        'owner': owner,
                        'name': repo,
                        'full_name': f"{owner}/{repo}",
                        'description': None,
                        'stars': 0,
                        'forks': 0,
                        'language': None,
                        'url': f"https://github.com/{owner}/{repo}",
                        'created_at': None,
                        'updated_at': None,
                        'topics': [],
                        'license': None
                    }

                response.raise_for_status()
                return response.json()
            
            def search_repo_by_name(query_name: str) -> Optional[Dict]:
                """当owner/repo无效时，使用GitHub搜索API按名称检索最匹配仓库"""
                search_url = f"{self.github_api_base}/search/repositories?q={quote(query_name)}&sort=stars&order=desc&per_page=1"
                logger.info(f"回退搜索仓库: {search_url}")
                resp = requests.get(search_url, headers={k:v for k,v in self.headers.items() if k != 'Authorization' or MCP_GITHUB_TOKEN}, timeout=15)
                if resp.status_code == 200:
                    items = resp.json().get('items', [])
                    return items[0] if items else None
                return None
            
            # 在线程池中执行请求以保持异步
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                data = await loop.run_in_executor(executor, make_request)
            
            if data is None:
                # 直接根据repo名进行搜索校正
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        search_data = await loop.run_in_executor(executor, search_repo_by_name, repo)
                    if search_data:
                        corrected = {
                            'owner': search_data.get('owner', {}).get('login'),
                            'name': search_data.get('name'),
                            'full_name': search_data.get('full_name'),
                            'description': search_data.get('description'),
                            'stars': search_data.get('stargazers_count', 0),
                            'forks': search_data.get('forks_count', 0),
                            'language': search_data.get('language'),
                            'url': search_data.get('html_url'),
                            'created_at': search_data.get('created_at'),
                            'updated_at': search_data.get('updated_at'),
                            'topics': search_data.get('topics', []),
                            'license': search_data.get('license', {}).get('name') if search_data.get('license') else None
                        }
                        logger.info(f"基于搜索回退纠正仓库: {corrected['full_name']}")
                        return corrected
                except Exception as e:
                    logger.warning(f"搜索回退失败: {e}")
                return None
                
            result = {
                'owner': data.get('owner', {}).get('login', owner),
                'name': data.get('name', repo),
                'full_name': data.get('full_name', f"{owner}/{repo}"),
                'description': data.get('description'),
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'language': data.get('language'),
                'url': data.get('html_url', f"https://github.com/{owner}/{repo}"),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'topics': data.get('topics', []),
                'license': data.get('license', {}).get('name') if data.get('license') else None
            }
            
            logger.info(f"成功获取仓库 {owner}/{repo} 信息: {result['stars']} stars, {result['forks']} forks")
            return result
                    
        except Exception as e:
            logger.error(f"MCP GitHub API 请求失败: {e}")
            return None

# 初始化 MCP GitHub 集成
mcp_github = MCPGitHubIntegration()

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "GitHub 项目推荐系统",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "API 服务正常运行"}

@app.get("/api/contributors/{owner}/{repo}", response_model=ContributorsResponse)
async def get_contributors(
    owner: str,
    repo: str,
    limit: int = Query(default=10, ge=1, le=100, description="返回贡献者数量限制")
):
    """获取指定仓库的贡献者列表"""
    try:
        logger.info(f"获取仓库 {owner}/{repo} 的贡献者列表，限制: {limit}")
        
        # 使用爬虫获取数据
        repo_info = crawler.get_repository_info(owner, repo)
        contributors_data = crawler.get_contributors(owner, repo, limit)
        
        if not contributors_data:
            raise HTTPException(
                status_code=404,
                detail=f"未找到仓库 {owner}/{repo} 的贡献者信息，请检查仓库是否存在或是否为公开仓库"
            )
        
        # 构造响应
        contributors = []
        for contrib in contributors_data:
            contributor = Contributor(
                username=contrib['username'],
                avatar_url=contrib['avatar_url'],
                contributions=contrib['contributions'],
                profile_url=contrib['profile_url']
            )
            contributors.append(contributor)
        
        repository = RepositoryInfo(
            owner=repo_info['owner'],
            name=repo_info['name'],
            full_name=repo_info['full_name'],
            description=repo_info['description'],
            stars=repo_info['stars'],
            forks=repo_info['forks'],
            language=repo_info['language'],
            url=repo_info.get('url'),
            created_at=repo_info.get('created_at'),
            updated_at=repo_info.get('updated_at')
        )
        
        return ContributorsResponse(
            repository=repository,
            contributors=contributors,
            total_count=len(contributors),
            limit=limit
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取贡献者列表时发生错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取贡献者信息时发生内部错误: {str(e)}"
        )

@app.get("/api/suggestions")
async def get_search_suggestions(q: str = Query(..., description="搜索关键词"), limit: int = Query(default=5, ge=1, le=10)):
    """获取项目搜索建议"""
    try:
        if not q or len(q.strip()) < 2:
            return {"suggestions": []}
        
        logger.info(f"获取搜索建议: '{q}', 限制: {limit}")
        
        # 使用GitHub爬虫搜索仓库
        repositories = crawler.search_repositories(q, limit)
        
        suggestions = []
        for repo in repositories:
            suggestions.append({
                "name": repo['full_name'],
                "description": repo.get('description', '无描述'),
                "stars": repo.get('stars', 0),
                "language": repo.get('language', '未知'),
                "url": repo.get('url', f"https://github.com/{repo['full_name']}")
            })
        
        return {"suggestions": suggestions}
    
    except Exception as e:
        logger.error(f"获取搜索建议时发生错误: {e}")
        return {"suggestions": []}

@app.get("/api/profile/{username}", response_model=UserProfile)
async def get_user_profile(username: str):
    """获取用户详细资料"""
    try:
        logger.info(f"获取用户 {username} 的详细资料")
        
        # 使用爬虫获取用户资料
        profile_data = crawler.get_user_profile(username)
        
        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail=f"未找到用户 {username} 的资料，请检查用户名是否正确"
            )
        
        # 构造响应对象
        profile = UserProfile(
            username=profile_data['username'],
            name=profile_data.get('name'),
            avatar_url=profile_data['avatar_url'],
            bio=profile_data.get('bio'),
            company=profile_data.get('company'),
            location=profile_data.get('location'),
            email=profile_data.get('email'),
            blog=profile_data.get('blog'),
            website=profile_data.get('website'),
            twitter=profile_data.get('twitter'),
            linkedin=profile_data.get('linkedin'),
            mastodon=profile_data.get('mastodon'),
            instagram=profile_data.get('instagram'),
            youtube=profile_data.get('youtube'),
            facebook=profile_data.get('facebook'),
            stackoverflow=profile_data.get('stackoverflow'),
            devto=profile_data.get('devto'),
            medium=profile_data.get('medium'),
            followers=profile_data.get('followers', 0),
            following=profile_data.get('following', 0),
            public_repos=profile_data.get('public_repos', 0),
            created_at=profile_data.get('created_at'),
            updated_at=profile_data.get('updated_at'),
            pronouns=profile_data.get('pronouns'),
            work_info=profile_data.get('work_info'),
            profile_elements=profile_data.get('profile_elements'),
            contact_info=profile_data.get('contact_info'),
            social_links=profile_data.get('social_links'),
            additional_info=profile_data.get('additional_info')
        )
        
        return profile
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户资料时发生错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取用户资料时发生内部错误: {str(e)}"
        )

@app.post("/api/recommendations")
async def get_project_recommendations(request: dict):
    """基于自然语言描述获取GitHub项目推荐"""
    try:
        query = request.get('query', '').strip()
        if not query:
            raise HTTPException(status_code=400, detail="需求描述不能为空")
        
        limit = min(request.get('limit', 5), 10)
        
        logger.info(f"收到项目推荐请求: {query[:50]}..., 限制: {limit}")
        
        # 使用DeepSeek API生成推荐结果
        ai_response = await call_deepseek_api(query, limit)
        
        # 解析AI响应并提取项目信息
        analysis_result = parse_ai_response(ai_response)
        
        # 获取项目详细信息
        detailed_recommendations = await enrich_recommendations(analysis_result['recommendations'])
        
        return {
            "analysis": analysis_result['analysis'],
            "recommendations": detailed_recommendations,
            "total_count": len(detailed_recommendations),
            "query": query
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"生成项目推荐时发生错误: {e}")
        
        # 针对不同类型的错误提供不同的用户友好的错误信息
        if "多次尝试后仍然超时" in error_msg:
            raise HTTPException(
                status_code=408, 
                detail="AI服务响应较慢，请稍后再试或简化您的查询内容。您也可以尝试使用更具体的关键词。"
            )
        elif "Read timed out" in error_msg or "timeout" in error_msg.lower():
            raise HTTPException(
                status_code=408, 
                detail="AI服务连接超时，请稍后再试。建议简化查询内容以获得更快的响应。"
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"服务器内部错误，请稍后重试。错误信息：{error_msg[:100]}"
            )

async def call_deepseek_api(query: str, limit: int = 5) -> str:
    """调用DeepSeek API获取AI推荐，使用用户提供的提示词"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 使用用户提供的专业提示词
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": AI_PROMPT
            },
            {
                "role": "user",
                "content": f"用户需求：{query}\n\n请根据上述需求推荐{limit}个GitHub项目。"
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    # 使用requests库（已验证SSL工作正常）
    import requests
    
    # 在线程池中执行同步请求
    import asyncio
    import concurrent.futures
    
    def make_request_with_retry():
        """带重试机制的请求函数"""
        max_retries = 2
        timeouts = [60, 90]  # 逐次增加超时时间
        
        for attempt in range(max_retries):
            try:
                timeout = timeouts[attempt] if attempt < len(timeouts) else 90
                logger.info(f"DeepSeek API调用尝试 {attempt + 1}/{max_retries}，超时时间: {timeout}秒")
                
                response = requests.post(
                    DEEPSEEK_API_BASE, 
                    json=payload, 
                    headers=headers, 
                    timeout=timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"DeepSeek API第{attempt + 1}次尝试超时: {e}")
                if attempt == max_retries - 1:  # 最后一次尝试
                    raise Exception("多次尝试后仍然超时，请稍后再试或简化您的查询内容")
            except requests.exceptions.RequestException as e:
                logger.error(f"DeepSeek API第{attempt + 1}次尝试失败: {e}")
                if attempt == max_retries - 1:  # 最后一次尝试
                    raise
            
            # 重试前等待一下
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # 指数退避：2秒, 4秒...
    
    # 在线程池中执行请求以保持异步
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        data = await loop.run_in_executor(executor, make_request_with_retry)
    
    if not data or 'choices' not in data or not data['choices']:
        raise Exception("DeepSeek API 返回数据格式异常")
    
    ai_response = data['choices'][0]['message']['content']
    logger.info(f"DeepSeek API调用成功，返回内容长度: {len(ai_response)}")
    return ai_response

def parse_ai_response(ai_response: str) -> dict:
    """解析AI响应，支持JSON和Markdown两种格式"""
    try:
        # 首先尝试直接解析整个响应为JSON
        try:
            json_data = json.loads(ai_response.strip())
            if 'analysis' in json_data and 'recommendations' in json_data:
                # 标准化关键词格式
                keywords = json_data['analysis'].get('keywords', [])
                if isinstance(keywords, str):
                    keywords = [kw.strip() for kw in keywords.replace('、', ',').split(',') if kw.strip()]
                
                logger.info(f"直接JSON解析成功，推荐项目数量: {len(json_data['recommendations'])}")
                return {
                    'analysis': {
                        'summary': json_data['analysis'].get('summary', '基于您的需求进行了分析'),
                        'keywords': keywords[:5]  # 最多5个关键词
                    },
                    'recommendations': json_data['recommendations']
                }
        except json.JSONDecodeError:
            pass
        
        # 如果直接解析失败，尝试解析``json```代码块
        json_match = re.search(r'```json\s*({[\s\S]*?})\s*```', ai_response)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                
                # 验证JSON结构
                if 'analysis' in json_data and 'recommendations' in json_data:
                    # 标准化关键词格式
                    keywords = json_data['analysis'].get('keywords', [])
                    if isinstance(keywords, str):
                        keywords = [kw.strip() for kw in keywords.replace('、', ',').split(',') if kw.strip()]
                    
                    logger.info(f"代码块JSON解析成功，推荐项目数量: {len(json_data['recommendations'])}")
                    return {
                        'analysis': {
                            'summary': json_data['analysis'].get('summary', '基于您的需求进行了分析'),
                            'keywords': keywords[:5]  # 最多5个关键词
                        },
                        'recommendations': json_data['recommendations']
                    }
            except json.JSONDecodeError as e:
                logger.warning(f"代码块JSON解析失败: {e}")
        
        # 如果JSON解析失败，记录原始响应并使用备用解析
        logger.warning(f"JSON解析失败，AI响应内容: {ai_response[:200]}...")
        return {
            'analysis': {
                'summary': '基于您的需求进行了分析',
                'keywords': ['开源', '项目']
            },
            'recommendations': []
        }
        
    except Exception as e:
        logger.error(f"解析AI响应失败: {e}")
        return {
            'analysis': {
                'summary': '需求分析完成',
                'keywords': ['开源', '项目']
            },
            'recommendations': []
        }

async def enrich_recommendations(recommendations: list) -> list:
    """丰富推荐项目的详细信息"""
    enriched = []
    
    for rec in recommendations:
        repo_name = rec.get('repository', '')
        if not repo_name or '/' not in repo_name:
            logger.warning(f"无效的仓库名称: {repo_name}")
            continue
            
        try:
            owner, repo = repo_name.split('/', 1)
            logger.info(f"处理推荐项目: {owner}/{repo}")
            
            # 尝试获取项目详细信息（优先GitHub API，其次网页爬取）
            repo_info = await mcp_github.get_repository_with_mcp(owner, repo)
            # 如果API失败或返回的stars/forks为0，回退到爬虫抓取页面数据
            if not repo_info or (isinstance(repo_info.get('stars', 0), int) and repo_info.get('stars', 0) == 0):
                try:
                    scraped = crawler.get_repository_info(owner, repo)
                    if scraped and scraped.get('stars', 0) or scraped.get('forks', 0):
                        repo_info = {
                            'owner': scraped.get('owner', owner),
                            'name': scraped.get('name', repo),
                            'full_name': scraped.get('full_name', f"{owner}/{repo}"),
                            'description': scraped.get('description'),
                            'stars': scraped.get('stars', 0),
                            'forks': scraped.get('forks', 0),
                            'language': scraped.get('language'),
                            'url': scraped.get('url', f'https://github.com/{owner}/{repo}')
                        }
                        logger.info(f"使用页面爬取补全仓库 {owner}/{repo} 的统计信息: {repo_info['stars']} stars")
                except Exception as se:
                    logger.warning(f"页面爬取仓库统计失败: {se}")

            if repo_info:
                # 成功获取仓库信息
                enriched_item = {
                    'repository': repo_name,
                    'name': repo_info.get('name', repo),
                    'description': rec.get('description', repo_info.get('description', '未提供描述')),
                    'stars': repo_info.get('stars', 0),
                    'forks': repo_info.get('forks', 0),
                    'language': repo_info.get('language', '未知'),
                    'url': repo_info.get('url', f'https://github.com/{repo_name}'),
                    'match_reason': rec.get('match_reason', '推荐匹配'),
                    'topics': repo_info.get('topics', []),
                    'license': repo_info.get('license'),
                    'created_at': repo_info.get('created_at'),
                    'updated_at': repo_info.get('updated_at')
                }
            else:
                # 获取失败，使用AI提供的基本信息
                logger.warning(f"无法获取仓库 {repo_name} 的GitHub信息，使用基本信息")
                enriched_item = {
                    'repository': repo_name,
                    'name': rec.get('name', repo),
                    'description': rec.get('description', '详细信息暂时不可用，请直接访问GitHub页面查看'),
                    'stars': '?',  # 显示问号表示数据不可用
                    'forks': '?',
                    'language': '未知',
                    'url': f'https://github.com/{repo_name}',
                    'match_reason': rec.get('match_reason', '推荐匹配'),
                    'topics': [],
                    'license': None,
                    'created_at': None,
                    'updated_at': None
                }
            
            enriched.append(enriched_item)
            logger.info(f"成功添加推荐项目: {repo_name}")
                
        except Exception as e:
            logger.error(f"处理项目 {repo_name} 时发生错误: {e}")
            # 即使出错也要尝试提供基本信息
            try:
                owner, repo = repo_name.split('/', 1)
                enriched.append({
                    'repository': repo_name,
                    'name': rec.get('name', repo),
                    'description': rec.get('description', '详细信息获取失败'),
                    'stars': '?',
                    'forks': '?',
                    'language': '未知',
                    'url': f'https://github.com/{repo_name}',
                    'match_reason': rec.get('match_reason', '推荐匹配')
                })
            except:
                logger.error(f"跳过无效项目: {repo_name}")
                continue
    
    logger.info(f"总共处理了 {len(enriched)} 个推荐项目")
    return enriched

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)