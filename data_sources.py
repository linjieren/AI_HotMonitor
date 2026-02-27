# -*- coding: utf-8 -*-
"""
数据源模块：当前为「模拟数据」，后续可替换为真实 X(Twitter) API 调用
设计成「可扩展」：只需实现 get_influencers() 和 get_products() 的实时版本即可
（新手：这里相当于「假数据」，先保证流程跑通；以后换成真 API 时，返回同样格式即可）
"""

from datetime import datetime, timedelta
import random

# 模拟：AI 领域有影响力的博主（账号、粉丝量级、近期内容摘要、帖子全文等）
# avatar 用 UI Avatars 按名字生成；后续接真实 X API 可改为 profile_image_url
MOCK_INFLUENCERS = [
    {"handle": "ylecun", "name": "Yann LeCun", "followers": "1.2M", "summary": "多模态与开源模型进展，强调本地推理与安全。", "post_content": "多模态与开源模型进展显著，但更要强调本地推理与数据安全。开源生态会继续推动边界。"},
    {"handle": "kaborobot", "name": "Kaborobot", "followers": "890K", "summary": "2026 年具身智能与机器人落地场景分析。", "post_content": "2026 年具身智能与机器人的落地场景会从仓储、配送扩展到家庭服务，关键在成本与可靠性。"},
    {"handle": "sama", "name": "Sam Altman", "followers": "3.5M", "summary": "AGI 路线图与 API 生态，新工具发布预告。", "post_content": "AGI 路线图在稳步推进，API 生态和开发者工具会有更多更新，敬请期待接下来的发布。"},
    {"handle": "drfeifei", "name": "Fei-Fei Li", "followers": "1.8M", "summary": "AI 与医疗、教育结合的前沿应用。", "post_content": "AI 与医疗、教育结合的前沿应用正在落地，从诊断辅助到个性化学习，社会影响会越来越大。"},
    {"handle": "goodside", "name": "Riley Goodside", "followers": "520K", "summary": "提示工程与 Agent 实践，新框架评测。", "post_content": "提示工程与 Agent 实践：新框架评测下来，上下文与工具调用设计比单纯堆参数更重要。"},
    {"handle": "sminaev", "name": "Sergey Minaev", "followers": "380K", "summary": "AI 创业与产品冷启动策略。", "post_content": "AI 创业与产品冷启动：先做小场景、验证 PMF，再扩规模。不要一上来就做大模型。"},
    {"handle": "swyx", "name": "swyx", "followers": "310K", "summary": "AI 开发者工具与 2026 技术趋势。", "post_content": "AI 开发者工具与 2026 技术趋势：AI-native IDE、agent 工作流、多模态 API 会成为标配。"},
    {"handle": "lilianweng", "name": "Lilian Weng", "followers": "290K", "summary": "LLM 推理优化与多智能体系统。", "post_content": "LLM 推理优化与多智能体系统：推理成本下降后，多 agent 协作与长期记忆会成重点。"},
    {"handle": "karpathy", "name": "Andrej Karpathy", "followers": "1.1M", "summary": "自动驾驶与端侧 AI，开源项目动态。", "post_content": "自动驾驶与端侧 AI 都在推进，开源项目会持续更新，欢迎关注仓库和讨论。"},
    {"handle": "emilymbender", "name": "Emily M. Bender", "followers": "220K", "summary": "AI 伦理与负责任部署。", "post_content": "AI 伦理与负责任部署不能事后补课，要从数据、评估、披露和问责机制一起设计。"},
]

# 已知 handle -> 显示名称（避免模拟数据中 name 与 handle 错位，如 @gdb 应对应 Greg Brockman）
HANDLE_TO_NAME = {
    "gdb": "Greg Brockman",
    "sama": "Sam Altman",
    "ylecun": "Yann LeCun",
    "karpathy": "Andrej Karpathy",
    "drfeifei": "Fei-Fei Li",
    "AndrewYNg": "Andrew Ng",
    "JeffDean": "Jeff Dean",
    "demishassabis": "Demis Hassabis",
    "elonmusk": "Elon Musk",
    "naval": "Naval Ravikant",
    "pmarca": "Marc Andreessen",
    "reidhoffman": "Reid Hoffman",
    "lexfridman": "Lex Fridman",
}
# 部分 handle 的模拟简介（真实 API 会拉取用户 description）
HANDLE_TO_DESCRIPTION = {
    "gdb": "President & Co-Founder @OpenAI",
    "sama": "CEO of OpenAI",
    "ylecun": "Chief AI Scientist at Meta",
    "karpathy": "AI researcher, former Tesla AI",
}

# 模拟：2026 新发布的 AI 产品/工具
MOCK_PRODUCTS = [
    {"name": "Cline 2026", "feature": "VS Code 内 AI 编程助手，多文件理解与一键重构。", "link": "https://cline.dev", "team": "Cline Team", "heat": "高"},
    {"name": "Replicate Canvas", "feature": "多模型可视化工作流，支持图像/视频/音频。", "link": "https://replicate.com/canvas", "team": "Replicate", "heat": "高"},
    {"name": "Windsurf", "feature": "终端 + 代码补全 + 自然语言命令。", "link": "https://codeium.com/windsurf", "team": "Codeium", "heat": "中高"},
    {"name": "MindOS", "feature": "个人 AI 工作台，任务分解与日程执行。", "link": "https://mindos.com", "team": "MindOS", "heat": "中"},
    {"name": "Cursor Rules 2.0", "feature": "项目级规则与风格约束，团队共享。", "link": "https://cursor.com", "team": "Cursor", "heat": "高"},
    {"name": "v0.dev 2026", "feature": "Vercel 出品，UI 组件与整页生成。", "link": "https://v0.dev", "team": "Vercel", "heat": "高"},
    {"name": "Lovable", "feature": "从描述生成可部署全栈应用。", "link": "https://lovable.dev", "team": "Lovable", "heat": "中"},
    {"name": "Suno v4", "feature": "音乐生成与混音，支持长曲与风格控制。", "link": "https://suno.com", "team": "Suno", "heat": "高"},
    {"name": "Pika 2.0", "feature": "文生视频与图生视频，时长与画质升级。", "link": "https://pika.art", "team": "Pika", "heat": "高"},
    {"name": "Devin 公测", "feature": "自主编程 Agent，多步骤任务与代码库理解。", "link": "https://devin.ai", "team": "Cognition", "heat": "高"},
]


def _random_recent_time(days=7):
    """生成过去 N 天内的随机时间，模拟「近期发布」"""
    now = datetime.now()
    delta = timedelta(days=random.randint(0, days), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return (now - delta).strftime("%Y-%m-%d %H:%M")


def _avatar_url(name, handle):
    """博主头像：模拟用 UI Avatars；真实 API 可改为 profile_image_url"""
    from urllib.parse import quote
    return f"https://ui-avatars.com/api/?name={quote(name)}&size=64&background=eee&color=333"


def _parse_followers(s):
    """把 1.2M、890K 转为数值，供前端排序"""
    if not s:
        return 0
    s = str(s).strip().upper().replace(",", "")
    if s.endswith("M"):
        return int(float(s[:-1]) * 1_000_000)
    if s.endswith("K"):
        return int(float(s[:-1]) * 1_000)
    try:
        return int(float(s))
    except ValueError:
        return 0


def _format_followers(n):
    """把粉丝数整数格式化为 1.2M、890K 等形式"""
    if n is None or n < 0:
        return "0"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}K".replace(".0K", "K")
    return str(n)


def _get_mock_influencers():
    """返回模拟的博主列表（无 X API 或请求失败时使用），按 config.MONITORED_INFLUENCERS 分类；name 与 handle 一一对应"""
    from config import MONITORED_INFLUENCERS, TOP_INFLUENCERS_COUNT
    results = []
    seed = 0
    for cat_name, handles in MONITORED_INFLUENCERS.items():
        for h in handles[:4]:
            seed += 1
            name = HANDLE_TO_NAME.get(h) or HANDLE_TO_NAME.get(h.lower()) or h
            base = MOCK_INFLUENCERS[seed % len(MOCK_INFLUENCERS)] if MOCK_INFLUENCERS else {}
            long_summary = (base.get("post_content") or base.get("summary") or "AI 与前沿技术观点与行业动态。")[:100]
            post_content = base.get("post_content") or long_summary
            results.append({
                "rank": 0,
                "handle": h,
                "name": name,
                "followers": f"{random.randint(50, 3000)}K",
                "followers_num": random.randint(50000, 3000000),
                "publish_time": _random_recent_time(7),
                "url": f"https://x.com/{h}/status/mock_{h}",
                "summary": long_summary[:100],
                "post_content": post_content,
                "mentions_product": random.choice([True, False]),
                "avatar_url": _avatar_url(name, h),
                "category": cat_name,
                "description": HANDLE_TO_DESCRIPTION.get(h) or HANDLE_TO_DESCRIPTION.get(h.lower()) or "AI 与科技领域创作者。",
                "profile_url": "",
                "joined_at": "2010-07" if h == "gdb" else "",
                "following_count": random.randint(10, 500),
                "like_count": random.randint(200, 15000),
                "retweet_count": random.randint(20, 2000),
                "reply_count": random.randint(10, 800),
            })
    results.sort(key=lambda x: x["publish_time"], reverse=True)
    results = results[:TOP_INFLUENCERS_COUNT]
    for i, r in enumerate(results, 1):
        r["rank"] = i
    return results


def _get_mock_products():
    """返回模拟的新品列表（无 X API 或解析结果不足时使用）"""
    heat_map = {"高": 3, "中高": 2, "中": 1}
    results = []
    for i, prod in enumerate(MOCK_PRODUCTS):
        results.append({
            "rank": i + 1,
            "name": prod["name"],
            "feature": prod["feature"],
            "link": prod["link"],
            "team": prod.get("team", ""),
            "publish_time": _random_recent_time(14),
            "heat": prod.get("heat", "中"),
            "heat_score": heat_map.get(prod.get("heat", "中"), 1),
            "category": "AI新品",
        })
    return results


def get_influencers():
    """
    获取「AI 大佬前沿观点」列表，按 config.MONITORED_INFLUENCERS 分类监测。
    若已配置 X_BEARER_TOKEN 则按分类调用 X API 拉取真实推文；否则返回模拟数据。
    """
    from config import X_BEARER_TOKEN, TOP_INFLUENCERS_COUNT, MONITORED_INFLUENCERS

    if not (X_BEARER_TOKEN and X_BEARER_TOKEN.strip()):
        return _get_mock_influencers()

    # handle -> category（API 返回的 username 可能小写）
    handle_to_cat = {}
    for cat_name, handles in MONITORED_INFLUENCERS.items():
        for h in handles:
            handle_to_cat[h.lower()] = cat_name

    x_api = __import__("x_api", fromlist=["fetch_tweets_by_query"])
    product_keywords = ("tool", "product", "launch", "新品", "发布", "new", "app")
    results = []
    for cat_name, handles in MONITORED_INFLUENCERS.items():
        if not handles:
            continue
        # 每类一条查询（避免超过 512 字符限制）
        query = " OR ".join(f"from:{h}" for h in handles)
        query = f"({query}) -is:retweet"
        try:
            tweets, users_by_id = x_api.fetch_tweets_by_query(query, max_results=100)
        except Exception:
            continue
        for tweet in tweets or []:
            author_id = getattr(tweet, "author_id", None) or ""
            user = users_by_id.get(str(author_id)) if author_id else None
            if not user:
                continue
            username = (getattr(user, "username", None) or "").strip()
            if not username:
                continue
            category = handle_to_cat.get(username.lower()) or cat_name
            name = getattr(user, "name", None) or username or ""
            text = (getattr(tweet, "text", None) or "").strip()
            if not text:
                continue
            metrics = getattr(user, "public_metrics", None) or {}
            followers_count = (metrics.get("followers_count") or 0) if isinstance(metrics, dict) else getattr(metrics, "followers_count", 0)
            following_count = (metrics.get("following_count") or 0) if isinstance(metrics, dict) else getattr(metrics, "following_count", 0)
            created_at = getattr(tweet, "created_at", None)
            publish_time = created_at.strftime("%Y-%m-%d %H:%M") if created_at and hasattr(created_at, "strftime") else _random_recent_time(7)
            tweet_id = getattr(tweet, "id", None) or ""
            url = f"https://x.com/{username}/status/{tweet_id}" if username and tweet_id else ""
            # #region agent log
            try:
                _log_path = "/Users/renlinjie/hot监测/.cursor/debug-06c7b3.log"
                _preview = (text[:50] + "…") if len(text) > 50 else text
                _url_has_id = str(tweet_id) in (url or "") if tweet_id else False
                _payload = {"sessionId": "06c7b3", "hypothesisId": "A,C", "location": "data_sources.py:get_influencers", "message": "influencer row from tweet", "data": {"tweet_id": str(tweet_id), "url": url, "url_contains_tweet_id": _url_has_id, "text_preview": _preview, "username": username}, "timestamp": __import__("time").time() * 1000}
                open(_log_path, "a", encoding="utf-8").write(__import__("json").dumps(_payload, ensure_ascii=False) + "\n")
            except Exception:
                pass
            # #endregion
            avatar_url = getattr(user, "profile_image_url", None) or _avatar_url(name, username)
            description = (getattr(user, "description", None) or "").strip()
            profile_url_raw = getattr(user, "url", None)
            if profile_url_raw and hasattr(profile_url_raw, "strip"):
                profile_url = profile_url_raw.strip()
            elif profile_url_raw and isinstance(profile_url_raw, str):
                profile_url = profile_url_raw
            else:
                profile_url = ""
            user_created = getattr(user, "created_at", None)
            joined_at = user_created.strftime("%Y-%m") if user_created and hasattr(user_created, "strftime") else ""
            mentions_product = any(kw in text.lower() for kw in product_keywords)
            t_metrics = getattr(tweet, "public_metrics", None) or {}
            like_count = (t_metrics.get("like_count") or 0) if isinstance(t_metrics, dict) else getattr(t_metrics, "like_count", 0)
            retweet_count = (t_metrics.get("retweet_count") or 0) if isinstance(t_metrics, dict) else getattr(t_metrics, "retweet_count", 0)
            reply_count = (t_metrics.get("reply_count") or 0) if isinstance(t_metrics, dict) else getattr(t_metrics, "reply_count", 0)
            summary_100 = (text[:100] + "…") if len(text) > 100 else text
            results.append({
                "rank": 0,
                "handle": username,
                "name": name,
                "followers": _format_followers(followers_count),
                "followers_num": int(followers_count),
                "following_count": int(following_count),
                "publish_time": publish_time,
                "url": url,
                "summary": summary_100,
                "post_content": text,
                "mentions_product": mentions_product,
                "avatar_url": avatar_url,
                "category": category,
                "description": description,
                "profile_url": profile_url,
                "joined_at": joined_at,
                "_created_at": created_at,
                "like_count": int(like_count),
                "retweet_count": int(retweet_count),
                "reply_count": int(reply_count),
            })
    results.sort(key=lambda x: x.get("publish_time", ""), reverse=True)
    for r in results:
        r.pop("_created_at", None)
    results = results[:TOP_INFLUENCERS_COUNT]
    # #region agent log
    try:
        _log_path = "/Users/renlinjie/hot监测/.cursor/debug-06c7b3.log"
        for i, r in enumerate(results[:5]):
            _payload = {"sessionId": "06c7b3", "hypothesisId": "B", "location": "data_sources.py:get_influencers_after_sort", "message": "influencer after sort", "data": {"rank": i + 1, "url": r.get("url"), "post_content_preview": (r.get("post_content") or "")[:50], "handle": r.get("handle")}, "timestamp": __import__("time").time() * 1000}
            open(_log_path, "a", encoding="utf-8").write(__import__("json").dumps(_payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # #endregion
    for i, r in enumerate(results, 1):
        r["rank"] = i
    return results


def get_products():
    """
    获取「2026 AI 新品速览」列表
    若已配置 X_BEARER_TOKEN 则用关键词搜「产品/发布」相关推文，解析链接与正文构造列表；否则返回模拟数据。
    """
    from config import X_BEARER_TOKEN, KEYWORDS, TOP_PRODUCTS_COUNT

    if not (X_BEARER_TOKEN and X_BEARER_TOKEN.strip()):
        return _get_mock_products()

    # 用产品相关关键词搜推文（取前几个关键词组合）
    product_keywords = [k for k in KEYWORDS if k and ("product" in k.lower() or "tool" in k.lower() or "发布" in k or "新品" in k)]
    if not product_keywords:
        product_keywords = ["AI tool launch", "AI new product"]
    query = " OR ".join(f'"{w}"' for w in product_keywords[:3])
    query = f"({query}) -is:retweet has:links"
    try:
        tweets, users_by_id = __import__("x_api", fromlist=["fetch_tweets_by_query"]).fetch_tweets_by_query(
            query, max_results=100
        )
    except Exception:
        return _get_mock_products()

    seen_urls = set()
    results = []
    for tweet in tweets:
        entities = getattr(tweet, "entities", None) or {}
        urls = (entities.get("urls") or []) if isinstance(entities, dict) else []
        text = (getattr(tweet, "text", None) or "").strip()
        created_at = getattr(tweet, "created_at", None)
        publish_time = created_at.strftime("%Y-%m-%d %H:%M") if created_at and hasattr(created_at, "strftime") else _random_recent_time(14)
        metrics = getattr(tweet, "public_metrics", None) or {}
        like_count = (metrics.get("like_count") or 0) if isinstance(metrics, dict) else getattr(metrics, "like_count", 0)
        retweet_count = (metrics.get("retweet_count") or 0) if isinstance(metrics, dict) else getattr(metrics, "retweet_count", 0)
        engagement = like_count + retweet_count

        for u in urls:
            link = u.get("expanded_url") or u.get("url") if isinstance(u, dict) else getattr(u, "expanded_url", None) or getattr(u, "url", "")
            if not link or link in seen_urls or "twitter.com" in link or "x.com" in link:
                continue
            seen_urls.add(link)
            try:
                from urllib.parse import urlparse
                name = urlparse(link).netloc.replace("www.", "") or (text[:30] + "…")
            except Exception:
                name = text[:30] + "…" if len(text) > 30 else text or "AI 产品"
            # #region agent log
            try:
                _log_path = "/Users/renlinjie/hot监测/.cursor/debug-06c7b3.log"
                _feat = (text[:80] + "…") if len(text) > 80 else text
                _payload = {"sessionId": "06c7b3", "hypothesisId": "D", "location": "data_sources.py:get_products", "message": "product row", "data": {"link": link, "feature_preview": _feat[:50], "tweet_text_len": len(text)}, "timestamp": __import__("time").time() * 1000}
                open(_log_path, "a", encoding="utf-8").write(__import__("json").dumps(_payload, ensure_ascii=False) + "\n")
            except Exception:
                pass
            # #endregion
            results.append({
                "rank": 0,
                "name": name,
                "feature": (text[:80] + "…") if len(text) > 80 else text,
                "link": link,
                "team": "",
                "publish_time": publish_time,
                "heat": "中",
                "heat_score": 1,
                "category": "AI新品",
                "_engagement": engagement,
            })
    results.sort(key=lambda x: x["_engagement"], reverse=True)
    for r in results:
        r.pop("_engagement", None)
    results = results[:TOP_PRODUCTS_COUNT]
    for i, r in enumerate(results, 1):
        r["rank"] = i
    return results if results else _get_mock_products()
