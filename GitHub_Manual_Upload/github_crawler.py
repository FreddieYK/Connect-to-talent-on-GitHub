import requests
import re
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
import logging
import urllib.parse

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubCrawler:
    """GitHub爬虫类，用于获取仓库和用户信息"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """获取仓库基本信息"""
        url = f"https://github.com/{owner}/{repo}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 获取仓库描述
            description_elem = soup.find('p', class_='f4 my-3')
            description = description_elem.text.strip() if description_elem else None
            
            # 获取star数量 - 使用多种选择器策略
            stars = 0
            # 策略1: 通过href属性查找
            stars_elem = soup.find('a', {'href': f'/{owner}/{repo}/stargazers'})
            if stars_elem:
                stars_text = stars_elem.text.strip()
                stars = self._parse_count(stars_text)
            else:
                # 策略2: 通过id属性查找
                stars_elem = soup.find('a', {'id': 'repo-stars-counter-star'})
                if stars_elem:
                    stars_text = stars_elem.text.strip()
                    stars = self._parse_count(stars_text)
                else:
                    # 策略3: 通过包含stargazers的链接查找
                    stars_elem = soup.find('a', href=re.compile(r'/stargazers$'))
                    if stars_elem:
                        stars_text = stars_elem.text.strip()
                        stars = self._parse_count(stars_text)
            
            # 获取fork数量 - 使用多种选择器策略
            forks = 0
            # 策略1: 通过href属性查找
            forks_elem = soup.find('a', {'href': f'/{owner}/{repo}/forks'})
            if forks_elem:
                forks_text = forks_elem.text.strip()
                forks = self._parse_count(forks_text)
            else:
                # 策略2: 通过id属性查找
                forks_elem = soup.find('a', {'id': 'repo-network-counter'})
                if forks_elem:
                    forks_text = forks_elem.text.strip()
                    forks = self._parse_count(forks_text)
                else:
                    # 策略3: 通过包含forks的链接查找
                    forks_elem = soup.find('a', href=re.compile(r'/forks$'))
                    if forks_elem:
                        forks_text = forks_elem.text.strip()
                        forks = self._parse_count(forks_text)
            
            # 获取主要语言
            language_elem = soup.find('span', class_='color-fg-default text-bold mr-1')
            language = language_elem.text.strip() if language_elem else None
            
            return {
                'owner': owner,
                'name': repo,
                'full_name': f"{owner}/{repo}",
                'description': description,
                'stars': stars,
                'forks': forks,
                'language': language
            }
        
        except Exception as e:
            logger.error(f"获取仓库信息失败: {e}")
            return {
                'owner': owner,
                'name': repo,
                'full_name': f"{owner}/{repo}",
                'description': None,
                'stars': 0,
                'forks': 0,
                'language': None
            }
    
    def get_contributors(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """获取仓库贡献者列表"""
        logger.info(f"开始获取 {owner}/{repo} 的贡献者信息")
        
        # 方法 1: 尝试使用 GitHub API (无需认证的公开API)
        contributors = self._try_github_api(owner, repo, limit)
        if contributors:
            logger.info(f"通过 GitHub API 成功获取 {len(contributors)} 个贡献者")
            return contributors
        
        # 方法 2: 解析 Contributors 页面
        contributors = self._parse_contributors_page(owner, repo, limit)
        if contributors:
            logger.info(f"通过页面解析成功获取 {len(contributors)} 个贡献者")
            return contributors
        
        # 方法 3: 从 Commits 页面提取贡献者
        contributors = self._extract_from_commits(owner, repo, limit)
        if contributors:
            logger.info(f"通过 Commits 页面成功获取 {len(contributors)} 个贡献者")
            return contributors
        
        logger.warning(f"所有方法都失败，返回空列表")
        return []
    
    def _try_github_api(self, owner: str, repo: str, limit: int) -> List[Dict]:
        """尝试使用 GitHub 公开 API 获取贡献者"""
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page={limit}"
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-Crawler/1.0'
            }
            
            response = self.session.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                contributors = []
                
                for contributor in data:
                    contributors.append({
                        'username': contributor['login'],
                        'avatar_url': contributor['avatar_url'],
                        'contributions': contributor['contributions'],
                        'profile_url': contributor['html_url']
                    })
                
                return contributors
            
        except Exception as e:
            logger.warning(f"GitHub API 请求失败: {e}")
        
        return []
    
    def _parse_contributors_page(self, owner: str, repo: str, limit: int) -> List[Dict]:
        """解析 GitHub Contributors 页面"""
        try:
            url = f"https://github.com/{owner}/{repo}/graphs/contributors"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            contributors = []
            
            # 多种选择器尝试
            selectors = [
                'li.contrib-person',
                'div.contrib-person', 
                'div[data-test-selector="contrib-person"]',
                'a[href*="/commits?author="]',
                '.js-navigation-item',
                '[data-hovercard-type="user"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    logger.info(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                    contributors = self._extract_contributors_from_elements(elements, limit)
                    if contributors:
                        return contributors
            
            # 如果上面都没有成功，尝试查找 JavaScript数据
            contributors = self._extract_from_page_data(soup, limit)
            if contributors:
                return contributors
                
        except Exception as e:
            logger.error(f"解析 Contributors 页面失败: {e}")
        
        return []
    
    def _extract_contributors_from_elements(self, elements, limit: int) -> List[Dict]:
        """从 HTML元素中提取贡献者信息"""
        contributors = []
        
        for i, element in enumerate(elements[:limit]):
            try:
                # 获取用户名
                username = self._extract_username(element)
                if not username:
                    continue
                
                # 获取头像
                avatar_url = self._extract_avatar(element, username)
                
                # 获取贡献次数
                contributions = self._extract_contributions(element, i)
                
                contributors.append({
                    'username': username,
                    'avatar_url': avatar_url,
                    'contributions': contributions,
                    'profile_url': f"https://github.com/{username}"
                })
                
            except Exception as e:
                logger.warning(f"解析第 {i} 个贡献者时出错: {e}")
                continue
        
        return contributors
    
    def _extract_username(self, element) -> str:
        """从元素中提取用户名"""
        # 多种方式尝试提取用户名
        methods = [
            lambda el: el.get('data-login'),
            lambda el: el.find('a', href=re.compile(r'^/[^/]+$')),
            lambda el: el.find('a', href=re.compile(r'/commits\?author=')),
            lambda el: el.find('img', alt=re.compile(r'^@')),
            lambda el: el.find('[data-hovercard-type="user"]'),
        ]
        
        for method in methods:
            try:
                result = method(element)
                if result:
                    if isinstance(result, str):
                        return result
                    elif hasattr(result, 'get'):
                        # 处理 href 属性
                        href = result.get('href', '')
                        if '/commits?author=' in href:
                            return href.split('author=')[1].split('&')[0]
                        elif href.startswith('/'):
                            return href.strip('/').split('/')[0]
                        # 处理 alt 属性
                        alt = result.get('alt', '')
                        if alt.startswith('@'):
                            return alt[1:]
            except:
                continue
        
        return ''
    
    def _extract_avatar(self, element, username: str) -> str:
        """提取头像 URL"""
        try:
            img = element.find('img')
            if img and img.get('src'):
                return img.get('src')
        except:
            pass
        
        # 返回默认头像
        return f'https://github.com/{username}.png'
    
    def _extract_contributions(self, element, index: int) -> int:
        """提取贡献次数"""
        try:
            # 多种方式查找贡献数
            patterns = [
                r'(\d+(?:,\d+)*)\s*commit',
                r'(\d+(?:,\d+)*)\s*次提交',
                r'(\d+(?:,\d+)*)',
            ]
            
            text = element.get_text()
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return int(match.group(1).replace(',', ''))
        except:
            pass
        
        # 如果无法获取具体数字，根据排名给出估算值
        return max(1000 - index * 50, 10)
    
    def _extract_from_page_data(self, soup, limit: int) -> List[Dict]:
        """从页面数据中提取贡献者信息"""
        try:
            # 查找可能包含贡献者数据的script标签
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'contributors' in script.string.lower():
                    # 这里可以解析JavaScript中的数据
                    # 由于复杂性，这里简化处理
                    pass
        except:
            pass
        
        return []
    
    def _extract_from_commits(self, owner: str, repo: str, limit: int) -> List[Dict]:
        """从 Commits 页面提取贡献者信息"""
        try:
            url = f"https://github.com/{owner}/{repo}/commits"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            contributors_dict = {}
            
            # 查找提交记录
            commit_items = soup.find_all(['div', 'li'], class_=re.compile(r'commit.*item|Box-row'))
            
            for commit in commit_items[:50]:  # 查看最近50个提交
                try:
                    # 查找作者信息
                    author_link = commit.find('a', href=re.compile(r'^/[^/]+$'))
                    if author_link:
                        username = author_link.get('href').strip('/')
                        if username and username not in contributors_dict:
                            avatar_elem = commit.find('img', alt=re.compile(r'^@'))
                            avatar_url = avatar_elem.get('src') if avatar_elem else f'https://github.com/{username}.png'
                            
                            contributors_dict[username] = {
                                'username': username,
                                'avatar_url': avatar_url,
                                'contributions': 0,
                                'profile_url': f"https://github.com/{username}"
                            }
                        
                        if username in contributors_dict:
                            contributors_dict[username]['contributions'] += 1
                
                except Exception as e:
                    continue
            
            # 按贡献次数排序
            contributors_list = sorted(
                contributors_dict.values(), 
                key=lambda x: x['contributions'], 
                reverse=True
            )
            
            return contributors_list[:limit]
            
        except Exception as e:
            logger.error(f"从 Commits 页面提取失败: {e}")
        
        return []
    
    def _get_contributors_fallback(self, owner: str, repo: str, limit: int) -> List[Dict]:
        """备用方法获取贡献者 - 不再使用"""
        logger.warning("所有方法都失败，请检查仓库是否存在或是否为公开仓库")
        return []
    
    def get_user_profile(self, username: str) -> Dict:
        """获取用户个人资料详细信息"""
        url = f"https://github.com/{username}"
        logger.info(f"开始获取用户 {username} 的详细资料")
        
        try:
            response = self.session.get(url, timeout=15)  # 增加超时时间
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"成功获取 {username} 的页面内容")
            
            # 初始化用户资料结构
            profile = self._initialize_profile_structure(username)
            
            # 获取基本信息
            self._extract_basic_info(soup, profile)
            
            # 获取统计信息
            self._extract_user_stats(soup, profile)
            
            # 获取详细联系信息和社交链接
            contact_info = self._extract_comprehensive_contact_info(soup)
            
            # 将联系信息整合到主资料中
            self._merge_contact_info_to_profile(profile, contact_info)
            
            # 获取额外信息
            self._extract_additional_profile_data(soup, profile)
            
            logger.info(f"成功获取 {username} 的完整资料")
            return profile
        
        except Exception as e:
            logger.error(f"获取用户资料失败: {e}")
            return self._get_fallback_profile(username)
    
    def _get_contact_info(self, soup: BeautifulSoup) -> Dict:
        """获取详细的联系信息和社交链接"""
        contact_info = {
            'company': None,
            'location': None,
            'email': None,
            'blog': None,
            'twitter': None,
            'linkedin': None,
            'mastodon': None,
            'github_username': None,
            'website': None,
            'social_links': {},
            'contact_links': {},
            'all_links': [],
            'raw_profile_text': ''
        }
        
        try:
            # 多种方式查找个人资料区域
            profile_selectors = [
                'div.js-profile-editable-area',
                'div[data-test-selector="profile-bio"]',
                '.vcard-details',
                '.js-profile-editable-replace',
                '.user-profile-nav',
                '.Layout-sidebar .BorderGrid-cell',
                '.js-sticky .BorderGrid-cell'
            ]
            
            profile_details = None
            for selector in profile_selectors:
                profile_details = soup.select_one(selector)
                if profile_details:
                    logger.info(f"找到个人资料区域，使用选择器: {selector}")
                    break
            
            # 如果没找到特定区域，使用整个页面
            if not profile_details:
                profile_details = soup
                logger.info("使用整个页面作为个人资料区域")
            
            # 保存原始文本用于调试
            contact_info['raw_profile_text'] = profile_details.get_text()[:500] if profile_details else ''
            
            # 获取所有链接并分类
            all_links = profile_details.find_all('a', href=True) if profile_details else []
            logger.info(f"找到 {len(all_links)} 个链接")
            
            for link in all_links:
                href = link.get('href', '').strip()
                text = link.get_text().strip()
                
                # 跳过空链接和相对链接
                if not href or href.startswith('#') or href.startswith('/'):
                    continue
                
                # 记录所有链接
                contact_info['all_links'].append({
                    'url': href,
                    'text': text,
                    'title': link.get('title', '')
                })
                
                # 分类不同类型的链接
                href_lower = href.lower()
                
                # 社交媒体平台识别
                if 'twitter.com' in href_lower or 'x.com' in href_lower:
                    contact_info['twitter'] = href
                    contact_info['social_links']['twitter'] = href
                    # 提取用户名
                    username = href.split('/')[-1] if '/' in href else ''
                    if username:
                        contact_info['social_links']['twitter_username'] = username
                    logger.info(f"找到 Twitter 链接: {href} (用户名: {username})")
                    
                elif 'linkedin.com' in href_lower:
                    contact_info['linkedin'] = href
                    contact_info['social_links']['linkedin'] = href
                    # 提取LinkedIn用户名或公司名
                    if '/in/' in href_lower:
                        username = href.split('/in/')[-1].split('/')[0] if '/in/' in href else ''
                        contact_info['social_links']['linkedin_username'] = username
                    elif '/company/' in href_lower:
                        company = href.split('/company/')[-1].split('/')[0] if '/company/' in href else ''
                        contact_info['social_links']['linkedin_company'] = company
                    logger.info(f"找到 LinkedIn 链接: {href}")
                    
                elif any(platform in href_lower for platform in ['mastodon', 'mas.to', 'fosstodon', 'mstdn']):
                    contact_info['mastodon'] = href
                    contact_info['social_links']['mastodon'] = href
                    # 提取Mastodon用户名和实例
                    if '@' in href:
                        parts = href.split('@')
                        if len(parts) >= 2:
                            contact_info['social_links']['mastodon_username'] = parts[-2]
                            contact_info['social_links']['mastodon_instance'] = parts[-1]
                    logger.info(f"找到 Mastodon 链接: {href}")
                    
                # 其他社交平台
                elif 'github.com' in href_lower and '/github.com/' in href:
                    # GitHub个人页面
                    username = href.split('github.com/')[-1].split('/')[0] if 'github.com/' in href else ''
                    if username and username not in ['orgs', 'organizations']:
                        contact_info['github_username'] = username
                        contact_info['social_links']['github'] = href
                        logger.info(f"找到 GitHub 用户: {username}")
                        
                elif any(platform in href_lower for platform in ['instagram.com', 'facebook.com', 'youtube.com', 'tiktok.com']):
                    platform_name = None
                    if 'instagram.com' in href_lower:
                        platform_name = 'instagram'
                    elif 'facebook.com' in href_lower:
                        platform_name = 'facebook'
                    elif 'youtube.com' in href_lower:
                        platform_name = 'youtube'
                    elif 'tiktok.com' in href_lower:
                        platform_name = 'tiktok'
                    
                    if platform_name:
                        contact_info['social_links'][platform_name] = href
                        logger.info(f"找到 {platform_name.title()} 链接: {href}")
                        
                # 专业平台
                elif any(platform in href_lower for platform in ['stackoverflow.com', 'dev.to', 'medium.com', 'hashnode']):
                    platform_name = None
                    if 'stackoverflow.com' in href_lower:
                        platform_name = 'stackoverflow'
                    elif 'dev.to' in href_lower:
                        platform_name = 'devto'
                    elif 'medium.com' in href_lower:
                        platform_name = 'medium'
                    elif 'hashnode' in href_lower:
                        platform_name = 'hashnode'
                    
                    if platform_name:
                        contact_info['social_links'][platform_name] = href
                        logger.info(f"找到 {platform_name.title()} 链接: {href}")
                        
                # 邮箱
                elif 'mailto:' in href_lower:
                    email = href.replace('mailto:', '')
                    contact_info['email'] = email
                    contact_info['contact_links']['email'] = href
                    logger.info(f"找到邮箱: {email}")
                    
                # 个人网站/博客
                elif any(domain in href_lower for domain in ['.dev', '.io', '.com', '.org', '.net', '.me', '.co', '.blog']):
                    # 排除已知的社交平台
                    excluded_domains = [
                        'github.com', 'twitter.com', 'x.com', 'linkedin.com', 'instagram.com', 
                        'facebook.com', 'youtube.com', 'tiktok.com', 'stackoverflow.com',
                        'medium.com', 'dev.to', 'mastodon', 'fosstodon'
                    ]
                    
                    if not any(excluded in href_lower for excluded in excluded_domains):
                        if not contact_info['blog']:
                            contact_info['blog'] = href
                            contact_info['website'] = href
                            contact_info['contact_links']['website'] = href
                            logger.info(f"找到个人网站: {href}")
                        else:
                            # 如果已有主网站，添加为额外链接
                            contact_info['social_links']['additional_website'] = href
                            logger.info(f"找到额外网站: {href}")
            
            # 使用多种选择器查找带有图标的信息项
            info_selectors = [
                'li.vcard-detail',
                '.vcard-detail',
                'li[itemprop]',
                '.js-profile-editable-area li',
                '.BorderGrid-cell li',
                '[data-test-selector="profile-bio"] li'
            ]
            
            info_items = []
            for selector in info_selectors:
                items = profile_details.select(selector) if profile_details else []
                info_items.extend(items)
                if items:
                    logger.info(f"使用选择器 {selector} 找到 {len(items)} 个信息项")
            
            # 去重
            seen_items = set()
            unique_items = []
            for item in info_items:
                item_text = item.get_text().strip()
                if item_text and item_text not in seen_items:
                    unique_items.append(item)
                    seen_items.add(item_text)
            
            logger.info(f"处理 {len(unique_items)} 个唯一信息项")
            
            for item in unique_items:
                item_text = item.get_text().strip()
                logger.info(f"处理信息项: {item_text}")
                
                # 检查SVG图标类型
                svg_elem = item.find('svg')
                if svg_elem:
                    # 通过SVG的class或aria-label判断类型
                    svg_classes = ' '.join(svg_elem.get('class', []))
                    aria_label = svg_elem.get('aria-label', '').lower()
                    
                    # 公司信息
                    if any(keyword in svg_classes.lower() for keyword in ['organization', 'building']) or 'organization' in aria_label:
                        if item_text and not contact_info['company']:
                            contact_info['company'] = item_text
                            logger.info(f"找到公司信息: {item_text}")
                    
                    # 位置信息
                    elif any(keyword in svg_classes.lower() for keyword in ['location', 'geo']) or 'location' in aria_label:
                        if item_text and not contact_info['location']:
                            contact_info['location'] = item_text
                            logger.info(f"找到位置信息: {item_text}")
                    
                    # 邮箱信息
                    elif any(keyword in svg_classes.lower() for keyword in ['mail', 'email']) or 'mail' in aria_label:
                        email_link = item.find('a', href=lambda x: x and 'mailto:' in x)
                        if email_link:
                            email = email_link.get('href').replace('mailto:', '')
                            contact_info['email'] = email
                            contact_info['contact_links']['email'] = email_link.get('href')
                            logger.info(f"找到邮箱信息: {email}")
                    
                    # 网站/博客
                    elif any(keyword in svg_classes.lower() for keyword in ['link', 'globe']) or 'link' in aria_label:
                        website_link = item.find('a', href=True)
                        if website_link and not contact_info['blog']:
                            url = website_link.get('href')
                            contact_info['blog'] = url
                            contact_info['website'] = url
                            contact_info['contact_links']['website'] = url
                            logger.info(f"找到网站信息: {url}")
                
                # 备用方法：通过文本内容判断
                if not any([contact_info.get('company'), contact_info.get('location')]):
                    # 如果包含@符号且不是邮箱，可能是公司
                    if '@' in item_text and 'mailto:' not in str(item):
                        if not contact_info['company']:
                            contact_info['company'] = item_text
                            logger.info(f"通过@符号识别公司: {item_text}")
                    # 如果包含地理位置关键词
                    elif any(geo_word in item_text.lower() for geo_word in ['university', '大学', 'city', '市', 'country', '国']):
                        if not contact_info['location']:
                            contact_info['location'] = item_text
                            logger.info(f"通过关键词识别位置: {item_text}")
            
            # 额外的备用解析策略
            self._apply_fallback_strategies(soup, contact_info)
        
        except Exception as e:
            logger.warning(f"解析联系信息时出错: {e}")
        
        # 记录最终结果
        logger.info(f"联系信息解析完成: company={contact_info.get('company')}, location={contact_info.get('location')}, email={contact_info.get('email')}, social_links={len(contact_info.get('social_links', {}))}")
        
        return contact_info
    
    def _apply_fallback_strategies(self, soup: BeautifulSoup, contact_info: Dict):
        """应用备用解析策略"""
        try:
            # 策略1: 通过aria-label属性查找信息
            aria_elements = soup.find_all(attrs={'aria-label': True})
            for elem in aria_elements:
                aria_label = elem.get('aria-label', '').lower()
                elem_text = elem.get_text().strip()
                
                if 'location' in aria_label and elem_text and not contact_info.get('location'):
                    contact_info['location'] = elem_text
                    logger.info(f"通过aria-label找到位置: {elem_text}")
                elif 'organization' in aria_label and elem_text and not contact_info.get('company'):
                    contact_info['company'] = elem_text
                    logger.info(f"通过aria-label找到公司: {elem_text}")
                elif 'email' in aria_label or 'mail' in aria_label:
                    email_link = elem.find('a', href=lambda x: x and 'mailto:' in x)
                    if email_link and not contact_info.get('email'):
                        email = email_link.get('href').replace('mailto:', '')
                        contact_info['email'] = email
                        logger.info(f"通过aria-label找到邮箱: {email}")
            
            # 策略2: 查找包含特定文本模式的元素
            all_text = soup.get_text()
            
            # 查找邮箱模式
            if not contact_info.get('email'):
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                email_matches = re.findall(email_pattern, all_text)
                if email_matches:
                    # 过滤掉常见的无效邮箱
                    valid_emails = [email for email in email_matches 
                                  if not any(invalid in email.lower() for invalid in 
                                           ['example.com', 'test.com', 'noreply', 'no-reply'])]
                    if valid_emails:
                        contact_info['email'] = valid_emails[0]
                        logger.info(f"通过正则表达式找到邮箱: {valid_emails[0]}")
            
            # 策略3: 查找特定的CSS类名
            css_class_mappings = {
                'location': ['user-location', 'profile-location', 'vcard-location'],
                'company': ['user-company', 'profile-company', 'vcard-organization'],
                'email': ['user-email', 'profile-email', 'vcard-email'],
                'website': ['user-website', 'profile-website', 'vcard-url']
            }
            
            for info_type, class_names in css_class_mappings.items():
                if contact_info.get(info_type):
                    continue
                    
                for class_name in class_names:
                    elements = soup.find_all(class_=lambda x: x and class_name in str(x))
                    for elem in elements:
                        elem_text = elem.get_text().strip()
                        if elem_text:
                            if info_type == 'email' and '@' in elem_text:
                                contact_info['email'] = elem_text
                                logger.info(f"通过CSS类名找到邮箱: {elem_text}")
                                break
                            elif info_type in ['location', 'company'] and len(elem_text) > 2:
                                contact_info[info_type] = elem_text
                                logger.info(f"通过CSS类名找到{info_type}: {elem_text}")
                                break
                            elif info_type == 'website':
                                link = elem.find('a', href=True)
                                if link and not contact_info.get('blog'):
                                    url = link.get('href')
                                    contact_info['blog'] = url
                                    contact_info['website'] = url
                                    logger.info(f"通过CSS类名找到网站: {url}")
                                    break
            
            # 策略4: 查找data属性
            data_elements = soup.find_all(attrs=lambda x: any(attr.startswith('data-') for attr in x.keys()) if x else False)
            for elem in data_elements:
                for attr, value in elem.attrs.items():
                    if attr.startswith('data-') and isinstance(value, str):
                        attr_lower = attr.lower()
                        value_lower = value.lower()
                        
                        if 'location' in attr_lower or 'location' in value_lower:
                            elem_text = elem.get_text().strip()
                            if elem_text and not contact_info.get('location'):
                                contact_info['location'] = elem_text
                                logger.info(f"通过data属性找到位置: {elem_text}")
                        elif 'company' in attr_lower or 'organization' in attr_lower:
                            elem_text = elem.get_text().strip()
                            if elem_text and not contact_info.get('company'):
                                contact_info['company'] = elem_text
                                logger.info(f"通过data属性找到公司: {elem_text}")
            
            # 策略5: 查找微格式数据
            microformat_selectors = {
                'location': ['[itemprop="address"]', '[itemprop="location"]', '.p-locality', '.h-adr'],
                'company': ['[itemprop="worksFor"]', '[itemprop="affiliation"]', '.p-org', '.h-card .p-org'],
                'email': ['[itemprop="email"]', '.u-email'],
                'website': ['[itemprop="url"]', '.u-url']
            }
            
            for info_type, selectors in microformat_selectors.items():
                if contact_info.get(info_type):
                    continue
                    
                for selector in selectors:
                    elements = soup.select(selector)
                    for elem in elements:
                        if info_type == 'email':
                            if elem.name == 'a' and elem.get('href', '').startswith('mailto:'):
                                email = elem.get('href').replace('mailto:', '')
                                contact_info['email'] = email
                                logger.info(f"通过微格式找到邮箱: {email}")
                                break
                        elif info_type == 'website':
                            if elem.name == 'a' and elem.get('href'):
                                url = elem.get('href')
                                if not contact_info.get('blog'):
                                    contact_info['blog'] = url
                                    contact_info['website'] = url
                                    logger.info(f"通过微格式找到网站: {url}")
                                    break
                        else:
                            elem_text = elem.get_text().strip()
                            if elem_text:
                                contact_info[info_type] = elem_text
                                logger.info(f"通过微格式找到{info_type}: {elem_text}")
                                break
        
        except Exception as e:
            logger.warning(f"备用解析策略执行失败: {e}")
    
    def _get_user_stats(self, soup: BeautifulSoup) -> Dict:
        """获取用户统计信息"""
        stats = {
            'followers': 0,
            'following': 0,
            'public_repos': 0
        }
        
        try:
            # 多种方式查找 followers
            followers_selectors = [
                'a[href*="?tab=followers"]',
                'a[href*="followers"]',
                '[data-tab-item="followers"]',
                '.js-profile-tab[data-tab-item="followers"]'
            ]
            
            for selector in followers_selectors:
                followers_elem = soup.select_one(selector)
                if followers_elem:
                    followers_text = followers_elem.get_text().strip()
                    logger.info(f"找到 followers 元素，原始文本: '{followers_text}'")
                    stats['followers'] = self._parse_count(followers_text)
                    logger.info(f"followers 解析结果: {stats['followers']}")
                    break
            
            # 多种方式查找 following
            following_selectors = [
                'a[href*="?tab=following"]',
                'a[href*="following"]',
                '[data-tab-item="following"]',
                '.js-profile-tab[data-tab-item="following"]'
            ]
            
            for selector in following_selectors:
                following_elem = soup.select_one(selector)
                if following_elem:
                    following_text = following_elem.get_text().strip()
                    logger.info(f"找到 following 元素，原始文本: '{following_text}'")
                    stats['following'] = self._parse_count(following_text)
                    logger.info(f"following 解析结果: {stats['following']}")
                    break
            
            # 多种方式查找 repositories
            repos_selectors = [
                'a[href*="?tab=repositories"]',
                'a[href*="repositories"]',
                '[data-tab-item="repositories"]',
                '.js-profile-tab[data-tab-item="repositories"]'
            ]
            
            for selector in repos_selectors:
                repos_elem = soup.select_one(selector)
                if repos_elem:
                    repos_text = repos_elem.get_text().strip()
                    logger.info(f"找到 repositories 元素，原始文本: '{repos_text}'")
                    stats['public_repos'] = self._parse_count(repos_text)
                    logger.info(f"repositories 解析结果: {stats['public_repos']}")
                    break
            
            # 备用方法：查找数字文本
            if stats['followers'] == 0 or stats['following'] == 0 or stats['public_repos'] == 0:
                self._parse_stats_from_text(soup, stats)
        
        except Exception as e:
            logger.warning(f"解析用户统计信息时出错: {e}")
        
        logger.info(f"最终统计信息: {stats}")
        return stats
    
    def _parse_stats_from_text(self, soup: BeautifulSoup, stats: Dict):
        """备用方法：从文本中解析统计信息"""
        try:
            # 查找包含数字的所有文本
            all_text = soup.get_text()
            
            # 查找 followers 模式
            followers_patterns = [
                r'(\d+(?:\.\d+)?[kKmMbB]?)\s*[Ff]ollowers?',
                r'[Ff]ollowers?[^\d]*(\d+(?:\.\d+)?[kKmMbB]?)',
                r'(\d+(?:\.\d+)?[kKmMbB]?)\s*关注者'
            ]
            
            for pattern in followers_patterns:
                match = re.search(pattern, all_text)
                if match and stats['followers'] == 0:
                    followers_text = match.group(1)
                    stats['followers'] = self._parse_count(followers_text)
                    logger.info(f"从文本中解析到 followers: '{followers_text}' -> {stats['followers']}")
                    break
            
            # 查找 following 模式
            following_patterns = [
                r'(\d+(?:\.\d+)?[kKmMbB]?)\s*[Ff]ollowing',
                r'[Ff]ollowing[^\d]*(\d+(?:\.\d+)?[kKmMbB]?)',
                r'(\d+(?:\.\d+)?[kKmMbB]?)\s*关注中'
            ]
            
            for pattern in following_patterns:
                match = re.search(pattern, all_text)
                if match and stats['following'] == 0:
                    following_text = match.group(1)
                    stats['following'] = self._parse_count(following_text)
                    logger.info(f"从文本中解析到 following: '{following_text}' -> {stats['following']}")
                    break
        
        except Exception as e:
            logger.warning(f"备用解析方法失败: {e}")
    
    def _parse_profile_elements(self, container) -> Dict:
        """解析个人资料容器中的详细信息"""
        elements = {
            'raw_html': str(container),
            'extracted_info': {},
            'contact_methods': [],
            'social_accounts': [],
            'additional_links': []
        }
        
        try:
            # 获取所有有用的信息
            for elem in container.find_all(['div', 'span', 'a', 'li'], recursive=True):
                elem_text = elem.text.strip() if elem.text else ''
                elem_class = ' '.join(elem.get('class', []))
                
                # 公司信息
                if 'octicon-organization' in elem_class or 'organization' in elem_class:
                    if elem_text and elem_text not in elements['extracted_info'].get('company', ''):
                        elements['extracted_info']['company'] = elem_text
                
                # 位置信息
                elif 'octicon-location' in elem_class or 'location' in elem_class:
                    if elem_text and elem_text not in elements['extracted_info'].get('location', ''):
                        elements['extracted_info']['location'] = elem_text
                
                # 邮箱信息
                elif 'octicon-mail' in elem_class or 'mail' in elem_class:
                    email_link = elem.find('a', href=lambda x: x and 'mailto:' in x)
                    if email_link:
                        email = email_link.get('href').replace('mailto:', '')
                        elements['extracted_info']['email'] = email
                        elements['contact_methods'].append({
                            'type': 'email',
                            'value': email,
                            'display': email
                        })
                
                # 博客/网站
                elif 'octicon-link' in elem_class or 'link' in elem_class:
                    website_link = elem.find('a', href=True)
                    if website_link:
                        url = website_link.get('href')
                        elements['extracted_info']['website'] = url
                        elements['additional_links'].append({
                            'type': 'website',
                            'url': url,
                            'display': website_link.text.strip() or url
                        })
                
                # Twitter/X 链接
                elif elem.name == 'a' and elem.get('href'):
                    href = elem.get('href')
                    if 'twitter.com' in href or 'x.com' in href:
                        elements['social_accounts'].append({
                            'platform': 'twitter',
                            'url': href,
                            'username': href.split('/')[-1] if '/' in href else ''
                        })
                    elif 'linkedin.com' in href:
                        elements['social_accounts'].append({
                            'platform': 'linkedin',
                            'url': href,
                            'username': href.split('/')[-1] if '/' in href else ''
                        })
                    elif 'mastodon' in href or 'mas.to' in href:
                        elements['social_accounts'].append({
                            'platform': 'mastodon',
                            'url': href,
                            'username': href.split('/')[-1] if '/' in href else ''
                        })
            
            # 查找所有的 vcard-detail 项目
            vcard_items = container.find_all(['li', 'div'], class_=lambda x: x and 'vcard-detail' in str(x))
            for item in vcard_items:
                item_text = item.text.strip()
                if item_text:
                    # 检查是否包含链接
                    link = item.find('a', href=True)
                    if link:
                        elements['additional_links'].append({
                            'type': 'general',
                            'url': link.get('href'),
                            'display': item_text
                        })
                    else:
                        # 纯文本信息
                        if '公司' in item_text or 'Company' in item_text:
                            elements['extracted_info']['company'] = item_text
                        elif '位置' in item_text or 'Location' in item_text:
                            elements['extracted_info']['location'] = item_text
        
        except Exception as e:
            logger.warning(f"解析个人资料元素时出错: {e}")
        
        return elements
    
    def _parse_count(self, text: str) -> int:
        """解析计数字符串（如 1.2k, 45等）"""
        if not text:
            return 0
            
        # 清理文本
        text = text.strip().lower()
        
        logger.info(f"原始文本: '{text}'")
        
        # 使用正则表达式匹配数字+可选单位的模式
        # 匹配: 数字(可包含小数点) + 可选的单位(k/m/b)
        match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*([kmb]?)(?:\s|$)', text)
        
        if not match:
            # 如果没有匹配到，尝试提取纯数字
            number_match = re.search(r'([0-9]+(?:\.[0-9]+)?)', text)
            if number_match:
                try:
                    result = int(float(number_match.group(1)))
                    logger.info(f"解析纯数字: '{text}' -> {result}")
                    return result
                except ValueError:
                    pass
            logger.warning(f"无法解析数字: '{text}'")
            return 0
        
        number_str = match.group(1)
        unit = match.group(2)
        
        logger.info(f"匹配结果: 数字='{number_str}', 单位='{unit}'")
        
        try:
            number = float(number_str)
            
            # 定义单位乘数
            multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
            
            if unit and unit in multipliers:
                result = int(number * multipliers[unit])
                logger.info(f"解析带单位: {number} * {multipliers[unit]} = {result}")
                return result
            else:
                result = int(number)
                logger.info(f"解析纯数字: {number} -> {result}")
                return result
                
        except (ValueError, TypeError) as e:
            logger.warning(f"解析数字失败: {e}")
            return 0
    
    def search_repositories(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索GitHub仓库"""
        logger.info(f"搜索仓库: '{query}', 限制: {limit}")
        
        try:
            # 使用 GitHub API 搜索仓库
            search_url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': min(limit, 30)  # GitHub API 最大限制
            }
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-Crawler/1.0'
            }
            
            response = self.session.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                repositories = []
                
                for repo in data.get('items', []):
                    repositories.append({
                        'owner': repo['owner']['login'],
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo.get('description'),
                        'stars': repo.get('stargazers_count', 0),
                        'forks': repo.get('forks_count', 0),
                        'language': repo.get('language'),
                        'url': repo['html_url'],
                        'created_at': repo.get('created_at'),
                        'updated_at': repo.get('updated_at')
                    })
                
                logger.info(f"搜索到 {len(repositories)} 个仓库")
                return repositories
            
            elif response.status_code == 403:
                logger.warning(f"GitHub API 限制，尝试网页搜索")
                return self._search_repositories_web(query, limit)
            
            else:
                logger.warning(f"GitHub API 请求失败: {response.status_code}")
                return self._search_repositories_web(query, limit)
        
        except Exception as e:
            logger.error(f"API 搜索失败: {e}，尝试网页搜索")
            return self._search_repositories_web(query, limit)
    
    def _search_repositories_web(self, query: str, limit: int) -> List[Dict]:
        """通过网页搜索GitHub仓库"""
        try:
            # 使用 GitHub 网页搜索
            search_url = "https://github.com/search"
            params = {
                'q': query,
                'type': 'repositories',
                's': 'stars',
                'o': 'desc'
            }
            
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            repositories = []
            
            # 查找搜索结果
            repo_items = soup.find_all('div', class_=lambda x: x and 'repo-list-item' in str(x))[:limit]
            
            for item in repo_items:
                try:
                    # 获取仓库名称
                    title_link = item.find('a', href=True)
                    if not title_link:
                        continue
                    
                    href = title_link.get('href')
                    if not href.startswith('/'):
                        continue
                    
                    parts = href.strip('/').split('/')
                    if len(parts) < 2:
                        continue
                    
                    owner = parts[0]
                    name = parts[1]
                    
                    # 获取描述
                    desc_elem = item.find('p', class_=lambda x: x and 'mb-1' in str(x))
                    description = desc_elem.text.strip() if desc_elem else None
                    
                    # 获取 stars 数
                    stars = 0
                    star_elem = item.find('a', href=lambda x: x and 'stargazers' in str(x))
                    if star_elem:
                        star_text = star_elem.text.strip()
                        stars = self._parse_count(star_text)
                    
                    # 获取语言
                    lang_elem = item.find('span', {'itemprop': 'programmingLanguage'})
                    language = lang_elem.text.strip() if lang_elem else None
                    
                    repositories.append({
                        'owner': owner,
                        'name': name,
                        'full_name': f"{owner}/{name}",
                        'description': description,
                        'stars': stars,
                        'forks': 0,  # 网页解析难以获取准确 forks 数
                        'language': language,
                        'url': f"https://github.com{href}",
                        'created_at': None,
                        'updated_at': None
                    })
                
                except Exception as e:
                    logger.warning(f"解析搜索结果项失败: {e}")
                    continue
            
            logger.info(f"网页搜索到 {len(repositories)} 个仓库")
            return repositories
        
        except Exception as e:
            logger.error(f"网页搜索失败: {e}")
            return []
    
    def _parse_contributions(self, text: str) -> int:
        """解析贡献次数文本"""
        # 提取数字
        numbers = re.findall(r'\d+(?:,\d+)*', text)
        if numbers:
            # 移除逗号并转换为整数
            return int(numbers[0].replace(',', ''))
        return 0
    
    def _initialize_profile_structure(self, username: str) -> Dict:
        """初始化用户资料结构"""
        return {
            'username': username,
            'name': None,
            'avatar_url': f'https://github.com/{username}.png',  # 默认头像
            'bio': None,
            'company': None,
            'location': None,
            'email': None,
            'blog': None,
            'website': None,
            'twitter': None,
            'linkedin': None,
            'mastodon': None,
            'instagram': None,
            'youtube': None,
            'facebook': None,
            'stackoverflow': None,
            'devto': None,
            'medium': None,
            'followers': 0,
            'following': 0,
            'public_repos': 0,
            'created_at': None,
            'updated_at': None,
            'pronouns': None,
            'work_info': None,
            'profile_elements': {},
            'contact_info': {},
            'social_links': {},
            'additional_info': {}
        }
    
    def _extract_basic_info(self, soup: BeautifulSoup, profile: Dict):
        """提取基本信息"""
        username = profile['username']
        
        # 获取头像 - 多种方式尝试
        avatar_selectors = [
            f'img[alt="@{username}"]',
            'img.avatar-user',
            'img[src*="avatars"]',
            '.avatar img'
        ]
        
        for selector in avatar_selectors:
            avatar_elem = soup.select_one(selector)
            if avatar_elem and avatar_elem.get('src'):
                profile['avatar_url'] = avatar_elem.get('src')
                logger.info(f"找到头像: {profile['avatar_url']}")
                break
        
        # 获取姓名 - 多种方式尝试
        name_selectors = [
            'span.p-name',
            'h1.vcard-names',
            '[itemprop="name"]',
            '.h-card .p-name'
        ]
        
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                profile['name'] = name_elem.text.strip()
                logger.info(f"找到姓名: {profile['name']}")
                break
        
        # 获取代词 (pronouns)
        pronouns_selectors = [
            'span.user-profile-pronouns',
            '[data-pronouns]',
            '.pronouns'
        ]
        
        for selector in pronouns_selectors:
            pronouns_elem = soup.select_one(selector)
            if pronouns_elem:
                profile['pronouns'] = pronouns_elem.text.strip()
                logger.info(f"找到代词: {profile['pronouns']}")
                break
        
        # 获取简介 - 多种方式尝试
        bio_selectors = [
            'div.p-note.user-profile-bio',
            'div[data-bio]',
            '[itemprop="description"]',
            '.user-profile-bio'
        ]
        
        for selector in bio_selectors:
            bio_elem = soup.select_one(selector)
            if bio_elem:
                bio_text = bio_elem.text.strip()
                if bio_text:
                    profile['bio'] = bio_text
                    logger.info(f"找到简介: {profile['bio'][:50]}...")
                    break
        
        # 获取工作信息
        work_selectors = [
            'div.user-profile-work',
            '[data-work]',
            '.work-info'
        ]
        
        for selector in work_selectors:
            work_elem = soup.select_one(selector)
            if work_elem:
                work_text = work_elem.text.strip()
                if work_text:
                    profile['work_info'] = work_text
                    logger.info(f"找到工作信息: {profile['work_info']}")
                    break
    
    def _extract_user_stats(self, soup: BeautifulSoup, profile: Dict):
        """提取用户统计信息"""
        stats = self._get_user_stats(soup)
        profile.update(stats)
        logger.info(f"统计信息: followers={stats['followers']}, following={stats['following']}, repos={stats['public_repos']}")
    
    def _extract_comprehensive_contact_info(self, soup: BeautifulSoup) -> Dict:
        """提取全面的联系信息和社交链接"""
        contact_info = {
            # 基本联系信息
            'company': None,
            'location': None,
            'email': None,
            'phone': None,
            'website': None,
            'blog': None,
            
            # 社交媒体平台
            'twitter': None,
            'linkedin': None,
            'mastodon': None,
            'instagram': None,
            'facebook': None,
            'youtube': None,
            'tiktok': None,
            
            # 专业平台
            'github': None,
            'stackoverflow': None,
            'devto': None,
            'medium': None,
            'hashnode': None,
            
            # 组织化数据
            'social_accounts': [],
            'contact_methods': [],
            'additional_links': [],
            'all_links': [],
            'raw_data': {}
        }
        
        try:
            # 获取个人资料区域
            profile_area = self._find_profile_area(soup)
            
            # 提取所有链接并分类
            self._extract_and_classify_links(profile_area, contact_info)
            
            # 提取带有图标的信息项
            self._extract_profile_info_items(profile_area, contact_info)
            
            # 应用备用解析策略
            self._apply_comprehensive_fallback_strategies(soup, contact_info)
            
            logger.info(f"联系信息提取完成: 社交平台={len([k for k,v in contact_info.items() if v and k in ['twitter','linkedin','instagram','facebook','youtube']])}, 联系方式={len([k for k,v in contact_info.items() if v and k in ['email','phone','website','blog']])}")
            
        except Exception as e:
            logger.warning(f"提取联系信息时出错: {e}")
        
        return contact_info
    
    def _find_profile_area(self, soup: BeautifulSoup):
        """查找个人资料区域"""
        profile_selectors = [
            'div.js-profile-editable-area',
            'div[data-test-selector="profile-bio"]',
            '.vcard-details',
            '.js-profile-editable-replace',
            '.user-profile-nav',
            '.Layout-sidebar .BorderGrid-cell',
            '.js-sticky .BorderGrid-cell',
            '.Layout-sidebar',
            '.profile-sidebar'
        ]
        
        for selector in profile_selectors:
            profile_area = soup.select_one(selector)
            if profile_area:
                logger.info(f"找到个人资料区域，使用选择器: {selector}")
                return profile_area
        
        # 如果没找到特定区域，使用整个页面
        logger.info("使用整个页面作为个人资料区域")
        return soup
    
    def _extract_and_classify_links(self, profile_area, contact_info: Dict):
        """提取并分类所有链接"""
        all_links = profile_area.find_all('a', href=True) if profile_area else []
        logger.info(f"找到 {len(all_links)} 个链接")
        
        for link in all_links:
            href = link.get('href', '').strip()
            text = link.get_text().strip()
            title = link.get('title', '')
            
            # 跳过空链接和相对链接
            if not href or href.startswith('#'):
                continue
            
            # 处理相对链接
            if href.startswith('/'):
                if href.startswith('//'):
                    href = 'https:' + href
                else:
                    # GitHub 内部链接，跳过
                    continue
            
            # 记录所有链接
            link_info = {
                'url': href,
                'text': text,
                'title': title,
                'platform': None,
                'type': None
            }
            
            # 分类链接
            platform_info = self._classify_link(href)
            if platform_info:
                link_info.update(platform_info)
                
                # 更新对应的联系信息字段
                platform = platform_info['platform']
                if platform in contact_info:
                    contact_info[platform] = href
                
                # 添加到对应的列表中
                if platform_info['type'] == 'social':
                    contact_info['social_accounts'].append(link_info)
                elif platform_info['type'] == 'contact':
                    contact_info['contact_methods'].append(link_info)
                else:
                    contact_info['additional_links'].append(link_info)
            
            contact_info['all_links'].append(link_info)
    
    def _classify_link(self, href: str) -> Dict:
        """分类链接类型"""
        href_lower = href.lower()
        
        # 社交媒体平台映射
        social_platforms = {
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'mastodon': ['mastodon', 'mas.to', 'fosstodon', 'mstdn'],
            'instagram': ['instagram.com'],
            'facebook': ['facebook.com', 'fb.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'tiktok': ['tiktok.com'],
            'github': ['github.com'],
            'stackoverflow': ['stackoverflow.com', 'stackexchange.com'],
            'devto': ['dev.to'],
            'medium': ['medium.com'],
            'hashnode': ['hashnode.com', 'hashnode.dev']
        }
        
        # 检查社交平台
        for platform, domains in social_platforms.items():
            if any(domain in href_lower for domain in domains):
                return {
                    'platform': platform,
                    'type': 'social',
                    'username': self._extract_username_from_url(href, platform)
                }
        
        # 邮箱链接
        if 'mailto:' in href_lower:
            return {
                'platform': 'email',
                'type': 'contact',
                'value': href.replace('mailto:', '')
            }
        
        # 电话链接
        if 'tel:' in href_lower:
            return {
                'platform': 'phone',
                'type': 'contact',
                'value': href.replace('tel:', '')
            }
        
        # 个人网站/博客
        if any(domain in href_lower for domain in ['.dev', '.io', '.com', '.org', '.net', '.me', '.co', '.blog', '.site']):
            # 排除已知的社交平台
            excluded_domains = [
                'github.com', 'twitter.com', 'x.com', 'linkedin.com', 'instagram.com',
                'facebook.com', 'youtube.com', 'tiktok.com', 'stackoverflow.com',
                'medium.com', 'dev.to', 'mastodon'
            ]
            
            if not any(excluded in href_lower for excluded in excluded_domains):
                return {
                    'platform': 'website',
                    'type': 'contact',
                    'value': href
                }
        
        return None
    
    def _extract_username_from_url(self, url: str, platform: str) -> str:
        """从 URL 中提取用户名"""
        try:
            if platform == 'twitter':
                return url.split('/')[-1] if '/' in url else ''
            elif platform == 'linkedin':
                if '/in/' in url:
                    return url.split('/in/')[-1].split('/')[0]
                elif '/company/' in url:
                    return url.split('/company/')[-1].split('/')[0]
            elif platform == 'github':
                parts = url.split('github.com/')[-1].split('/')
                return parts[0] if parts and parts[0] not in ['orgs', 'organizations'] else ''
            elif platform in ['instagram', 'facebook', 'youtube', 'tiktok']:
                return url.split('/')[-1] if '/' in url else ''
            elif platform == 'mastodon':
                if '@' in url:
                    parts = url.split('@')
                    return f"@{parts[-2]}@{parts[-1]}" if len(parts) >= 2 else ''
            else:
                return url.split('/')[-1] if '/' in url else ''
        except Exception:
            return ''
    
    def _extract_profile_info_items(self, profile_area, contact_info: Dict):
        """提取带有图标的信息项"""
        if not profile_area:
            return
            
        info_selectors = [
            'li.vcard-detail',
            '.vcard-detail',
            'li[itemprop]',
            '.js-profile-editable-area li',
            '.BorderGrid-cell li',
            '[data-test-selector="profile-bio"] li',
            '.user-profile-bio li'
        ]
        
        info_items = []
        for selector in info_selectors:
            items = profile_area.select(selector)
            info_items.extend(items)
            if items:
                logger.info(f"使用选择器 {selector} 找到 {len(items)} 个信息项")
        
        # 去重
        seen_items = set()
        unique_items = []
        for item in info_items:
            item_text = item.get_text().strip()
            if item_text and item_text not in seen_items:
                unique_items.append(item)
                seen_items.add(item_text)
        
        for item in unique_items:
            self._parse_profile_info_item(item, contact_info)
    
    def _parse_profile_info_item(self, item, contact_info: Dict):
        """解析单个信息项"""
        item_text = item.get_text().strip()
        
        # 检查 SVG 图标类型
        svg_elem = item.find('svg')
        if svg_elem:
            svg_classes = ' '.join(svg_elem.get('class', []))
            aria_label = svg_elem.get('aria-label', '').lower()
            
            # 公司信息
            if any(keyword in svg_classes.lower() for keyword in ['organization', 'building']) or 'organization' in aria_label:
                if item_text and not contact_info.get('company'):
                    contact_info['company'] = item_text
                    logger.info(f"找到公司信息: {item_text}")
            
            # 位置信息
            elif any(keyword in svg_classes.lower() for keyword in ['location', 'geo']) or 'location' in aria_label:
                if item_text and not contact_info.get('location'):
                    contact_info['location'] = item_text
                    logger.info(f"找到位置信息: {item_text}")
            
            # 邮箱信息
            elif any(keyword in svg_classes.lower() for keyword in ['mail', 'email']) or 'mail' in aria_label:
                email_link = item.find('a', href=lambda x: x and 'mailto:' in x)
                if email_link and not contact_info.get('email'):
                    email = email_link.get('href').replace('mailto:', '')
                    contact_info['email'] = email
                    logger.info(f"找到邮箱信息: {email}")
            
            # 网站/博客
            elif any(keyword in svg_classes.lower() for keyword in ['link', 'globe', 'url']) or 'link' in aria_label:
                website_link = item.find('a', href=True)
                if website_link and not contact_info.get('website'):
                    url = website_link.get('href')
                    if not any(excluded in url.lower() for excluded in ['github.com', 'twitter.com', 'linkedin.com']):
                        contact_info['website'] = url
                        contact_info['blog'] = url
                        logger.info(f"找到网站信息: {url}")
    
    def _apply_comprehensive_fallback_strategies(self, soup: BeautifulSoup, contact_info: Dict):
        """应用全面的备用解析策略"""
        try:
            # 策略 1: 通过 aria-label 属性查找信息
            self._extract_by_aria_labels(soup, contact_info)
            
            # 策略 2: 通过正则表达式查找邮箱
            self._extract_email_by_regex(soup, contact_info)
            
            # 策略 3: 通过 CSS 类名查找信息
            self._extract_by_css_classes(soup, contact_info)
            
            # 策略 4: 通过微格式数据查找
            self._extract_by_microformats(soup, contact_info)
            
        except Exception as e:
            logger.warning(f"备用解析策略执行失败: {e}")
    
    def _extract_by_aria_labels(self, soup: BeautifulSoup, contact_info: Dict):
        """通过 aria-label 属性查找信息"""
        aria_elements = soup.find_all(attrs={'aria-label': True})
        for elem in aria_elements:
            aria_label = elem.get('aria-label', '').lower()
            elem_text = elem.get_text().strip()
            
            if 'location' in aria_label and elem_text and not contact_info.get('location'):
                contact_info['location'] = elem_text
            elif 'organization' in aria_label and elem_text and not contact_info.get('company'):
                contact_info['company'] = elem_text
            elif ('email' in aria_label or 'mail' in aria_label):
                email_link = elem.find('a', href=lambda x: x and 'mailto:' in x)
                if email_link and not contact_info.get('email'):
                    contact_info['email'] = email_link.get('href').replace('mailto:', '')
    
    def _extract_email_by_regex(self, soup: BeautifulSoup, contact_info: Dict):
        """通过正则表达式查找邮箱"""
        if contact_info.get('email'):
            return
            
        all_text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, all_text)
        
        if email_matches:
            # 过滤掉常见的无效邮箱
            valid_emails = [email for email in email_matches 
                          if not any(invalid in email.lower() for invalid in 
                                   ['example.com', 'test.com', 'noreply', 'no-reply', 'placeholder'])]
            if valid_emails:
                contact_info['email'] = valid_emails[0]
    
    def _extract_by_css_classes(self, soup: BeautifulSoup, contact_info: Dict):
        """通过 CSS 类名查找信息"""
        css_mappings = {
            'location': ['user-location', 'profile-location', 'vcard-location'],
            'company': ['user-company', 'profile-company', 'vcard-organization'],
            'email': ['user-email', 'profile-email', 'vcard-email'],
            'website': ['user-website', 'profile-website', 'vcard-url']
        }
        
        for info_type, class_names in css_mappings.items():
            if contact_info.get(info_type):
                continue
                
            for class_name in class_names:
                elements = soup.find_all(class_=lambda x: x and class_name in str(x))
                for elem in elements:
                    elem_text = elem.get_text().strip()
                    if elem_text:
                        if info_type == 'email' and '@' in elem_text:
                            contact_info['email'] = elem_text
                            break
                        elif info_type in ['location', 'company'] and len(elem_text) > 2:
                            contact_info[info_type] = elem_text
                            break
                        elif info_type == 'website':
                            link = elem.find('a', href=True)
                            if link:
                                contact_info['website'] = link.get('href')
                                contact_info['blog'] = link.get('href')
                                break
    
    def _extract_by_microformats(self, soup: BeautifulSoup, contact_info: Dict):
        """通过微格式数据查找"""
        microformat_selectors = {
            'location': ['[itemprop="address"]', '[itemprop="location"]', '.p-locality', '.h-adr'],
            'company': ['[itemprop="worksFor"]', '[itemprop="affiliation"]', '.p-org', '.h-card .p-org'],
            'email': ['[itemprop="email"]', '.u-email'],
            'website': ['[itemprop="url"]', '.u-url']
        }
        
        for info_type, selectors in microformat_selectors.items():
            if contact_info.get(info_type):
                continue
                
            for selector in selectors:
                elements = soup.select(selector)
                for elem in elements:
                    if info_type == 'email':
                        if elem.name == 'a' and elem.get('href', '').startswith('mailto:'):
                            contact_info['email'] = elem.get('href').replace('mailto:', '')
                            break
                    elif info_type == 'website':
                        if elem.name == 'a' and elem.get('href'):
                            contact_info['website'] = elem.get('href')
                            contact_info['blog'] = elem.get('href')
                            break
                    else:
                        elem_text = elem.get_text().strip()
                        if elem_text:
                            contact_info[info_type] = elem_text
                            break
    
    def _merge_contact_info_to_profile(self, profile: Dict, contact_info: Dict):
        """将联系信息整合到主资料中"""
        # 直接字段映射
        direct_mappings = [
            'company', 'location', 'email', 'website', 'blog',
            'twitter', 'linkedin', 'mastodon', 'instagram', 'facebook',
            'youtube', 'stackoverflow', 'devto', 'medium'
        ]
        
        for field in direct_mappings:
            if contact_info.get(field) and not profile.get(field):
                profile[field] = contact_info[field]
        
        # 存储完整的联系信息
        profile['contact_info'] = contact_info
        
        # 创建社交链接字典
        profile['social_links'] = {
            platform: contact_info[platform] 
            for platform in ['twitter', 'linkedin', 'mastodon', 'instagram', 'facebook', 'youtube', 'stackoverflow', 'devto', 'medium']
            if contact_info.get(platform)
        }
    
    def _extract_additional_profile_data(self, soup: BeautifulSoup, profile: Dict):
        """提取额外的资料数据"""
        additional_info = {}
        
        try:
            # 查找加入日期
            join_date = self._extract_join_date(soup)
            if join_date:
                additional_info['join_date'] = join_date
                profile['created_at'] = join_date
            
            # 查找贡献历史
            contribution_info = self._extract_contribution_info(soup)
            if contribution_info:
                additional_info['contributions'] = contribution_info
            
            # 查找组织信息
            organizations = self._extract_organizations(soup)
            if organizations:
                additional_info['organizations'] = organizations
            
            # 查找置顶仓库
            pinned_repos = self._extract_pinned_repositories(soup)
            if pinned_repos:
                additional_info['pinned_repositories'] = pinned_repos
            
        except Exception as e:
            logger.warning(f"提取额外资料数据时出错: {e}")
        
        profile['additional_info'] = additional_info
    
    def _extract_join_date(self, soup: BeautifulSoup) -> str:
        """提取加入 GitHub 的日期"""
        join_selectors = [
            'time[datetime]',
            '[data-date]',
            '.join-date'
        ]
        
        for selector in join_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get('datetime') or elem.get('data-date') or elem.text.strip()
        
        # 备用：查找文本中的日期模式
        text = soup.get_text()
        date_patterns = [
            r'Joined GitHub on ([A-Za-z]+ \d{1,2}, \d{4})',
            r'Joined on ([A-Za-z]+ \d{1,2}, \d{4})',
            r'Member since ([A-Za-z]+ \d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_contribution_info(self, soup: BeautifulSoup) -> Dict:
        """提取贡献信息"""
        contribution_info = {}
        
        # 查找贡献图表
        contribution_graph = soup.select_one('.js-yearly-contributions')
        if contribution_graph:
            # 提取贡献总数
            total_text = contribution_graph.get_text()
            total_match = re.search(r'(\d+(?:,\d+)*) contributions?', total_text)
            if total_match:
                contribution_info['total_contributions'] = int(total_match.group(1).replace(',', ''))
        
        return contribution_info
    
    def _extract_organizations(self, soup: BeautifulSoup) -> List[Dict]:
        """提取组织信息"""
        organizations = []
        
        org_elements = soup.select('.avatar-group-item, .org-avatar')
        for org_elem in org_elements:
            org_link = org_elem.find('a', href=True)
            if org_link:
                href = org_link.get('href')
                if href.startswith('/'):
                    org_name = href.strip('/').split('/')[0]
                    img_elem = org_elem.find('img')
                    avatar_url = img_elem.get('src') if img_elem else None
                    
                    organizations.append({
                        'name': org_name,
                        'url': f"https://github.com{href}",
                        'avatar_url': avatar_url
                    })
        
        return organizations
    
    def _extract_pinned_repositories(self, soup: BeautifulSoup) -> List[Dict]:
        """提取置顶仓库信息"""
        pinned_repos = []
        
        pinned_elements = soup.select('.pinned-item-list-item')
        for pinned_elem in pinned_elements:
            repo_link = pinned_elem.select_one('a[href*="/"]')
            if repo_link:
                href = repo_link.get('href')
                repo_name = href.strip('/').split('/')[-1] if href else None
                
                desc_elem = pinned_elem.select_one('.pinned-item-desc')
                description = desc_elem.text.strip() if desc_elem else None
                
                lang_elem = pinned_elem.select_one('[itemprop="programmingLanguage"]')
                language = lang_elem.text.strip() if lang_elem else None
                
                if repo_name:
                    pinned_repos.append({
                        'name': repo_name,
                        'url': f"https://github.com{href}" if href else None,
                        'description': description,
                        'language': language
                    })
        
        return pinned_repos
    
    def _get_fallback_profile(self, username: str) -> Dict:
        """获取备用资料结构"""
        return {
            'username': username,
            'name': None,
            'avatar_url': f'https://github.com/{username}.png',
            'bio': None,
            'company': None,
            'location': None,
            'email': None,
            'blog': None,
            'website': None,
            'twitter': None,
            'linkedin': None,
            'mastodon': None,
            'instagram': None,
            'youtube': None,
            'facebook': None,
            'stackoverflow': None,
            'devto': None,
            'medium': None,
            'followers': 0,
            'following': 0,
            'public_repos': 0,
            'created_at': None,
            'updated_at': None,
            'pronouns': None,
            'work_info': None,
            'profile_elements': {},
            'contact_info': {},
            'social_links': {},
            'additional_info': {}
        }