# -*- coding: utf-8 -*-
"""
网页服务：打开页面即可查看最新 AI 前沿日报（不发邮件）
支持本地运行与部署到云平台，每日打开网页即看到最新监测数据
"""

import os
from datetime import datetime

# 缓存时间（分钟）：在此时间内重复打开页面不重新拉取数据，避免频繁请求 X API
CACHE_MINUTES = 60

# 内存缓存： (html_body, 生成时间)
_report_cache = None


def _generate_report():
    """拉取数据 → 检测链接 → 生成日报 HTML，不发邮件"""
    from fetcher import fetch_influencer_posts, fetch_new_products
    from report import build_daily_report
    from link_checker import check_influencer_links, check_product_links

    influencers = fetch_influencer_posts()
    products = fetch_new_products()
    check_influencer_links(influencers)
    check_product_links(products)
    date_str = datetime.now().strftime("%Y-%m-%d")
    _, html_body = build_daily_report(influencers, products, date_str)
    return html_body


def get_report_html(force_refresh=False):
    """获取日报 HTML，带缓存；force_refresh=True 时强制重新生成"""
    global _report_cache
    now = datetime.now()
    if not force_refresh and _report_cache is not None:
        html, gen_time = _report_cache
        delta_min = (now - gen_time).total_seconds() / 60
        if delta_min < CACHE_MINUTES:
            return html
    html = _generate_report()
    _report_cache = (html, now)
    return html


def create_app():
    from flask import Flask, Response
    app = Flask(__name__)

    @app.route("/")
    def index():
        html = get_report_html(force_refresh=False)
        return Response(html, mimetype="text/html; charset=utf-8")

    @app.route("/refresh")
    def refresh():
        """强制刷新：重新拉取数据并生成日报"""
        html = get_report_html(force_refresh=True)
        return Response(html, mimetype="text/html; charset=utf-8")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
