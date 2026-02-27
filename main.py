# -*- coding: utf-8 -*-
"""
主入口：一键生成日报并发送邮件
支持「立即执行」和「每天固定时间执行」（如早 7 点）
"""

import sys
import time
from datetime import datetime, timedelta

# 本项目的模块
from fetcher import fetch_influencer_posts, fetch_new_products
from report import build_daily_report
from email_sender import send_report
from link_checker import check_influencer_links, check_product_links
from config import DAILY_HOUR, DAILY_MINUTE


def run_once():
    """执行一次：抓数据 → 检测链接可访问性 → 生成日报 → 发邮件"""
    # 1. 抓取（当前为模拟数据；后续可在此替换为真实 X API）
    influencers = fetch_influencer_posts()
    products = fetch_new_products()

    # 2. 检测每条链接是否可打开，结果写入 link_ok
    print("正在检测链接可访问性…")
    check_influencer_links(influencers)
    check_product_links(products)

    # 3. 生成日报
    date_str = datetime.now().strftime("%Y-%m-%d")
    subject, html_body = build_daily_report(influencers, products, date_str)

    # 4. 发送邮件（若未配置邮箱则只保存到本地，方便试运行）
    from config import SMTP_USER
    if "your_email" in SMTP_USER or not SMTP_USER or SMTP_USER == "your_email@qq.com":
        out_path = f"daily_report_{date_str}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_body)
        print(f"[{datetime.now().isoformat()}] 未配置邮箱，日报已保存到：{out_path}")
    else:
        send_report(subject, html_body)
        print(f"[{datetime.now().isoformat()}] 日报已发送：{subject}")
    return subject


def run_daily_at(hour=7, minute=0):
    """
    每天在指定时间运行一次（如早 7:00）
    用简单循环 + sleep 实现，不依赖 schedule 库，依赖更少
    """
    last_run_date = None  # 上次执行日期，避免同一天重复发
    while True:
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if now >= target:
            target = target + timedelta(days=1)  # 明天同一时刻
        delta = (target - now).total_seconds()
        print(f"下次运行时间：{target.strftime('%Y-%m-%d %H:%M')}（距现在 {delta / 3600:.1f} 小时）")
        time.sleep(min(max(delta, 0), 3600))  # 最多睡 1 小时再检查
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        target_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # 已过今日目标时间 且 今天还没执行过 → 执行一次
        if now >= target_today and last_run_date != today_str:
            run_once()
            last_run_date = today_str


if __name__ == "__main__":
    # 无参数：立即执行一次
    # 参数 --daily：每天 DAILY_HOUR:DAILY_MINUTE 执行（默认早 7 点）
    if len(sys.argv) > 1 and sys.argv[1] == "--daily":
        print("已启动每日定时任务（早 {}:{}）".format(DAILY_HOUR, str(DAILY_MINUTE).zfill(2)))
        run_daily_at(DAILY_HOUR, DAILY_MINUTE)
    else:
        run_once()
