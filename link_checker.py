# -*- coding: utf-8 -*-
"""
链接可访问性检测：对每条日报中的 URL 做 HEAD 请求，判断是否可打开
检测结果会写回数据项的 link_ok 字段，供报告展示（可访问/不可访问）
"""

import urllib.request
import ssl
from urllib.error import URLError, HTTPError

# 超时与 User-Agent，避免被部分站点拒绝（多条链接依次检测，超时不宜过长）
TIMEOUT = 5
USER_AGENT = "Mozilla/5.0 (compatible; AI-Daily-Bot/1.0)"


def _check_url(url):
    """
    检测单个 URL 是否可访问。
    返回 True=可访问, False=不可访问, None=未检测。
    X/Twitter 链接一律不检测（直接返回 None），避免脚本被拒导致误标「不可访问」；链接仍可点击，在浏览器中打开即可。
    """
    if not url or url.startswith("#"):
        return False
    if "x.com" in url or "twitter.com" in url:
        return None  # 不对 X 链接发请求，避免误标；用户在浏览器中点击原文即可打开
    is_x = False  # 仅用于下方异常分支，X 已在上方直接返回
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as r:
                return 200 <= r.status < 400
        except HTTPError as e:
            if is_x and e.code in (403, 429):
                return None  # X 对脚本请求常返回 403/429，标记为未检测
            return 200 <= e.code < 400
    except (URLError, HTTPError, OSError, Exception):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as r:
                return 200 <= r.status < 400
        except HTTPError as e:
            if is_x and e.code in (403, 429):
                return None
            return False
        except Exception:
            return False


def check_influencer_links(influencers):
    """为博主列表的 url 检测可访问性，写入 link_ok"""
    for row in influencers:
        row["link_ok"] = _check_url(row.get("url"))
    return influencers


def check_product_links(products):
    """为新品列表的 link 检测可访问性，写入 link_ok"""
    for row in products:
        row["link_ok"] = _check_url(row.get("link"))
    return products
