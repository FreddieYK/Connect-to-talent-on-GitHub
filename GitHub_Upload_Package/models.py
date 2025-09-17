from typing import List, Optional
from pydantic import BaseModel


class Contributor(BaseModel):
    """贡献者信息模型"""
    username: str
    avatar_url: str
    contributions: int
    profile_url: str


class ContactInfo(BaseModel):
    """联系信息模型"""
    # 基本联系信息
    company: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    blog: Optional[str] = None
    
    # 社交媒体平台
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    mastodon: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    
    # 专业平台
    github: Optional[str] = None
    stackoverflow: Optional[str] = None
    devto: Optional[str] = None
    medium: Optional[str] = None
    hashnode: Optional[str] = None
    
    # 组织化数据
    social_accounts: List[dict] = []
    contact_methods: List[dict] = []
    additional_links: List[dict] = []
    extracted_info: Optional[dict] = None
    raw_data: Optional[dict] = None


class UserProfile(BaseModel):
    """用户个人资料模型"""
    username: str
    name: Optional[str] = None
    avatar_url: str
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    blog: Optional[str] = None
    website: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    mastodon: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    facebook: Optional[str] = None
    stackoverflow: Optional[str] = None
    devto: Optional[str] = None
    medium: Optional[str] = None
    followers: int = 0
    following: int = 0
    public_repos: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pronouns: Optional[str] = None
    work_info: Optional[str] = None
    profile_elements: Optional[dict] = None
    contact_info: Optional[ContactInfo] = None
    social_links: Optional[dict] = None
    additional_info: Optional[dict] = None


class RepositoryInfo(BaseModel):
    """仓库信息模型"""
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    language: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # 新增字段
    topics: Optional[List[str]] = []
    license: Optional[str] = None


class SearchResult(BaseModel):
    """搜索结果模型"""
    repositories: List[RepositoryInfo]
    total_count: int = 0
    query: str = ""


class ContributorsResponse(BaseModel):
    """贡献者列表响应模型"""
    repository: RepositoryInfo
    contributors: List[Contributor]
    total_count: int
    limit: int