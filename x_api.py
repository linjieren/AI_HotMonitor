# -*- coding: utf-8 -*-
"""
X (Twitter) API v2 封装：Recent Search + 作者信息扩展
Bearer Token 为空或请求失败时返回空结果，便于上层回退到模拟数据
"""

import logging

logger = logging.getLogger(__name__)


def fetch_tweets_by_query(query, max_results=100):
    """
    使用 Recent Search 按关键词或 from:用户 搜索最近 7 天推文，并带作者信息。
    :param query: 搜索表达式，如 "AI" 或 "from:ylecun OR from:sama"
    :param max_results: 单次最多返回条数，10–100
    :return: (tweets_list, users_by_id)
      - tweets_list: 推文对象列表，每项有 id, text, created_at, author_id 等
      - users_by_id: dict，author_id -> 用户对象（含 username, name, profile_image_url, public_metrics）
    失败或未配置 Token 时返回 ([], {})
    """
    try:
        import tweepy
    except ImportError:
        logger.warning("tweepy 未安装，无法调用 X API，将使用模拟数据")
        return [], {}

    from config import X_BEARER_TOKEN
    if not (X_BEARER_TOKEN and X_BEARER_TOKEN.strip()):
        logger.debug("未配置 X_BEARER_TOKEN，使用模拟数据")
        return [], {}

    try:
        client = tweepy.Client(bearer_token=X_BEARER_TOKEN.strip())
        response = client.search_recent_tweets(
            query=query,
            max_results=min(max(10, max_results), 100),
            tweet_fields=["created_at", "public_metrics", "entities"],
            expansions=["author_id"],
            user_fields=["profile_image_url", "public_metrics", "name", "username", "description", "url", "created_at"],
            sort_order="recency",
        )
    except Exception as e:
        logger.warning("X API 请求失败: %s，将使用模拟数据", e)
        return [], {}

    if not response.data:
        return [], {}

    tweets_list = list(response.data)
    users_by_id = {}
    if response.includes and "users" in response.includes:
        for u in response.includes["users"]:
            users_by_id[str(u.id)] = u

    return tweets_list, users_by_id
