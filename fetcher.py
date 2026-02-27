# -*- coding: utf-8 -*-
"""
抓取模块：统一入口，当前走模拟数据；后续替换为真实 X API 时只改这里
"""

from data_sources import get_influencers, get_products


def fetch_influencer_posts():
    """
    抓取「AI 大佬前沿观点」数据
    返回列表，每项含：rank, handle, name, followers, publish_time, url, summary, mentions_product
    """
    return get_influencers()


def fetch_new_products():
    """
    抓取「2026 AI 新品」数据
    返回列表，每项含：rank, name, feature, link, team, publish_time, heat
    """
    return get_products()
