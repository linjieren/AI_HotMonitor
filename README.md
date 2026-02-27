# AI 前沿日报监控工具

每天 5 分钟看邮箱，获取 **AI 大佬前沿观点 TOP10** 与 **2026 AI 新品速览 TOP10**，无需手动刷 X、无需维护名单。

## 功能概览

- **自动筛选**：AI 领域最新、最有影响力的博主内容（按互动/权威/时间）；2026 新发布的 AI 产品/工具（按讨论度/创新性/可体验性）
- **结构化日报**：两部分表格（博主 + 新品），按前沿性/实用性排序，HTML 邮件
- **每日定时**：支持每天固定时间（默认早 7 点）自动运行并发邮件
- **可扩展**：当前为「模拟数据 + 框架」，后续可替换为真实 X API，只需改 `data_sources.py` 与 `fetcher.py`

## 快速开始

### 1. 配置邮箱

编辑 `config.py`：

- `SMTP_USER` / `SMTP_PASSWORD`：发件邮箱与 SMTP 授权码（QQ/163 等需在邮箱设置里开启 SMTP 并获取授权码）
- `RECEIVER_EMAIL`：接收日报的邮箱

### 2. 试运行（不配置邮箱也可跑通）

未配置 `config.py` 里的邮箱时，执行 `python main.py` 会把日报生成到当前目录的 `daily_report_YYYY-MM-DD.html`，用浏览器打开即可查看，方便先确认流程。

### 3. 运行方式

```bash
# 进入项目目录
cd /Users/renlinjie/hot监测

# 立即执行一次（抓模拟数据 → 生成日报 → 发邮件）
python main.py

# 每天早 7 点自动执行（前台常驻，可配合 nohup 或系统服务）
python main.py --daily
```

### 4. 每天固定时间自动运行（推荐）

不想常驻进程时，可用系统定时任务：

**macOS / Linux（cron）：**

```bash
crontab -e
# 添加一行（每天早 7 点执行，请改成你的实际路径）
0 7 * * * cd /Users/renlinjie/hot监测 && /usr/bin/python3 main.py
```

**macOS（launchd）：** 可新建 plist 放在 `~/Library/LaunchAgents/`，用 `launchd` 每天 7 点执行 `python main.py`。

## 项目结构

| 文件 | 说明 |
|------|------|
| `config.py` | 邮箱、X 凭证、关键词、定时时间、TOP 数量等配置 |
| `data_sources.py` | 数据源：有 X_BEARER_TOKEN 时走 X API，否则为模拟数据 |
| `x_api.py` | X API v2 封装：Recent Search + 作者信息扩展 |
| `fetcher.py` | 抓取入口，调用数据源得到博主列表与新品列表 |
| `link_checker.py` | 链接可访问性检测（x.com 遇 403/429 标为未检测） |
| `report.py` | 生成日报 HTML（交互式卡片、排序、筛选） |
| `email_sender.py` | 使用 smtplib 发送 HTML 邮件 |
| `main.py` | 主入口：抓取 → 检测链接 → 生成日报 → 发邮件 |
| `app.py` | 网页服务：打开页面即可查看最新日报（不发邮件），可部署到云或本地 |

## 网页部署（每天打开网页看最新日报）

不依赖邮箱，直接在浏览器打开一个网址即可查看最新监测报告。

### 本地运行

```bash
cd /Users/renlinjie/hot监测
pip install -r requirements.txt
python app.py
```

浏览器访问 **http://127.0.0.1:5000** 即可看到当日日报。一小时内重复访问会使用缓存，不重复拉取数据；访问 **http://127.0.0.1:5000/refresh** 可强制刷新数据。

### 部署到云（公网可访问）

1. **Railway / Render / Fly.io 等**  
   - 将本项目推送到 GitHub，在平台中「从 GitHub 部署」。
   - 设置启动命令：`gunicorn -w 1 -b 0.0.0.0:$PORT app:app`（平台会注入 `PORT`）。
   - 在平台「Variables」中配置 `X_BEARER_TOKEN`（可选，不配则用模拟数据）。
   - 部署完成后会得到一个公网 URL，每天打开该 URL 即可看最新日报。

2. **本机长期运行**  
   - 在服务器或本机执行：`gunicorn -w 1 -b 0.0.0.0:5000 app:app`，需外网访问时再配合内网穿透（如 ngrok、frp）或路由器端口转发。

3. **与定时邮件并存**  
   - 继续用 cron 每天执行 `python main.py` 发邮件；网页服务单独运行，两者互不影响。

## 接入 X (Twitter) API

配置 X API 后，日报将自动使用真实推文与博主信息；未配置或请求失败时会回退到模拟数据，日报仍可正常生成。

### 1. 申请开发者与凭证

1. 打开 [developer.x.com](https://developer.x.com/)，用 X 账号登录，申请开发者访问（填写用途说明，一般会通过）。
2. 在开发者门户中创建 **Project** 和 **App**，进入该 App 的 **Keys and tokens**。
3. 生成 **Bearer Token**（用于只读接口：搜索、用户信息）。复制并保存，不要泄露或提交到代码库。

### 2. 配置 Bearer Token

- **方式一（推荐）**：复制 `.env.example` 为 `.env`，在 `.env` 中填入：
  ```bash
  X_BEARER_TOKEN=你的Bearer_Token
  ```
  在运行前加载环境变量（例如在 shell 里 `export $(cat .env | xargs)`，或使用 `python-dotenv` 在代码里加载）。
- **方式二**：在运行前执行 `export X_BEARER_TOKEN=你的Bearer_Token`。

本程序从环境变量 `X_BEARER_TOKEN` 读取（见 `config.py`），未设置时使用模拟数据。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

当前 `requirements.txt` 包含 `tweepy>=4.14.0`，用于调用 X API v2。不安装时程序仍可运行，但会使用模拟数据。

### 4. 运行与回退

- 配置好 `X_BEARER_TOKEN` 并安装 tweepy 后，直接执行 `python main.py`，将自动拉取真实推文并生成日报。
- 若未配置 Token、tweepy 未安装或 X API 请求失败（如限流、网络错误），程序会自动回退到模拟数据，保证日报照常生成。

### 5. 限制说明

- **Recent Search** 仅支持**最近 7 天**的推文，与「优先近 7 天活跃」一致。
- 注意 API 调用频率，日报每日运行一次即可，避免触发 rate limit。

## 依赖说明

- **无 X API 时**：仅需 Python 3 标准库即可运行（使用模拟数据）。
- **接入 X API 时**：需安装 `tweepy>=4.14.0`（见 `requirements.txt`）。

## 注意事项

- 邮箱 SMTP 密码请使用「授权码」，不要填登录密码。
- 首次建议先 `python main.py` 跑通一次，确认能收到邮件再配置 cron 或 `--daily`。
