# -*- coding: utf-8 -*-
"""
配置文件：邮箱、关键词、定时等（新手：改这里就能改发信时间和收件人）
后续替换真实 X 接口时，可在此增加 API Key 等配置
"""

import os

# 若已安装 python-dotenv，自动从项目根目录的 .env 加载环境变量（含 X_BEARER_TOKEN）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ========== X (Twitter) API（可选，不填则使用模拟数据）==========
# 从环境变量或 .env 读取，不要提交到代码库
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")

# ========== 邮箱配置（发日报用）==========
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "your_email@qq.com"
SMTP_PASSWORD = "your_auth_code"
RECEIVER_EMAIL = "your_email@qq.com"

# ========== 监测博主名单（按分类，用于 X API 拉取与报告筛选）==========
# 每类下列出 X handle（不含 @），报告内可按分类筛选
MONITORED_INFLUENCERS = {
    "AI 科学家/顶尖研究者": [
        "AndrewYNg", "ylecun", "karpathy", "JeffDean", "demishassabis", "ilyasut",
        "ShaneLegg", "DrJimFan", "soumithchintala", "OriolVinyalsML", "RichardSocher",
        "EMostaque", "drfeifei", "rasbt", "DanielaAmodei", "antonosika",
    ],
    "OpenAI 核心圈": [
        "sama", "gdb", "mustafasuleyman", "_jasonwei", "alexandr_wang", "AmenaiSabuwala",
    ],
    "AI 创业者/CEO": [
        "alighodsi", "aidangomez", "AravSrinivas", "bradlightcap", "cjpedregal", "drorwe",
        "emollick", "garrytan", "ivanhzhao", "julien_c", "levie", "mikeyk", "minnasong",
        "rauchg", "ryolu_", "satyanadella", "ScottWu46", "vasuman",
    ],
    "硅谷投资人/大佬": [
        "reidhoffman", "pmarca", "naval", "paulg", "jeffreyhuber", "benchmark",
        "nickaturley", "kevinweil", "danshipper", "mntruell", "jasonfried", "amasad",
        "alexgraveley", "c_valenzuelab", "jackclarkSF", "_mohansolo", "kloss_xyz", "rileybrown",
    ],
    "产品/技术/开发者": [
        "hwchase17", "levelsio", "lexfridman", "jackfriks", "MengTo", "steipete",
        "gregisenberg", "corbin_braun", "marclou", "Hesamation", "rryssf_", "egeberkina",
        "AmirMushich", "0xROAS",
    ],
    "内容/趋势/自媒体": [
        "lennysan", "Artedeingenio", "omooretweets", "polynoamial", "saranormous", "ashtom",
        "JonathanRoss321", "8enmann", "tkexpress11", "MS_BASE44", "jeffwsurf", "ctnzr",
        "EXM7777", "eptwts", "godofprompt", "BerntBornich",
    ],
    "科技顶流": ["elonmusk"],
}

# ========== 监控关键词 ==========
KEYWORDS = [
    "AI new product",
    "AI tool launch",
    "创业 AI product",
    "2026 AI frontier",
    "AI 工具 体验",
    "2026最新AI应用",
    "AI新品发布",
]

# ========== 定时任务 ==========
DAILY_HOUR = 7
DAILY_MINUTE = 0

# ========== 数量限制 ==========
# 博主总数（多分类合并后按时间/互动取前 N 条）
TOP_INFLUENCERS_COUNT = 30
TOP_PRODUCTS_COUNT = 10
