# 网页部署说明：每天打开网页看最新日报

按下面任选一种方式，即可通过浏览器访问最新 AI 前沿日报（无需收邮件）。

---

## 方式一：本机运行（仅自己电脑访问）

```bash
cd /Users/renlinjie/hot监测
pip install -r requirements.txt
python app.py
```

浏览器打开：**http://127.0.0.1:5000**  
- 首次打开会拉取数据并生成日报（约几秒～几十秒）。  
- 一小时内再次打开使用缓存，不重复请求。  
- 要看最新数据：点击页面头部的 **「刷新数据」** 按钮，或访问 **http://127.0.0.1:5000/refresh**。

---

## 方式二：部署到 Render（免费，公网可访问）

### 第一步：准备 GitHub 仓库

- 将本项目推送到 GitHub（仓库名如 `AI_HotMonitor` 等均可）。
- 确保仓库里有 `requirements.txt`、`app.py`、`config.py`、`fetcher.py`、`report.py` 等必要文件。

### 第二步：在 Render 创建 Web Service

1. 打开 [render.com](https://render.com)，注册/登录。
2. 点击 **New → Web Service**。
3. 连接 GitHub，选择你的仓库（如 `AI_HotMonitor`），点击 **Connect**。
4. 按下面表格逐项填写（可直接复制粘贴）：

| 配置项 | 填写内容 |
|--------|----------|
| **Name** | 随意，如 `ai-daily-report` |
| **Region** | 选离你近的（如 Singapore） |
| **Branch** | 一般为 `main` 或 `master` |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python -m gunicorn -w 1 -b 0.0.0.0:$PORT app:app` |
| **Instance Type** | 免费选 **Free** 即可 |

5. **Environment Variables**（可选）：
   - 点击 **Add Environment Variable**。
   - Key：`X_BEARER_TOKEN`
   - Value：从 [X Developer Portal](https://developer.x.com/) 复制的 Bearer Token（要用真实 X 数据时必填；不填则用模拟数据）。
6. 点击 **Create Web Service**，等待 Build 和 Deploy 完成（约 2～5 分钟）。
7. 部署成功后，在页面顶部会显示 **Your service is live at https://xxx.onrender.com**，在浏览器打开该链接即可看到日报。

### 若出现 `gunicorn: command not found`

- 将 **Start Command** 改为：`python -m gunicorn -w 1 -b 0.0.0.0:$PORT app:app`（不要用单独的 `gunicorn` 命令）。

注意：免费实例一段时间无访问会休眠，首次打开可能较慢；点击页头「刷新数据」或访问 `/refresh` 可强制更新数据。

**Render 加载过长 / 失败时自检清单：**

| 检查项 | 正确做法 |
|--------|----------|
| **Start Command** | 推荐 `python -m gunicorn -w 1 -b 0.0.0.0:$PORT app:app`（避免 `gunicorn: command not found`）。不能是 `gunicorn app:app`（缺少 `-b 0.0.0.0:$PORT` 会导致不监听端口，页面一直转圈或 503）。 |
| **Environment Variables** | 在 Render 控制台 → 你的 Web Service → Environment 中添加变量：Key = `X_BEARER_TOKEN`，Value = 你的 Bearer Token（从 X Developer Portal 复制，不要有多余空格或换行）。不填也可运行，但会使用模拟数据。 |
| **requirements.txt** | 需包含：`flask`、`gunicorn`、`tweepy`、`python-dotenv`。本项目已包含，无需修改。 |
| **Build Command** | `pip install -r requirements.txt`（或留空，Render 有时会自动识别）。 |

免费实例冷启动约 30 秒～1 分钟属正常；首次打开首页会拉取数据并生成报告，再等几秒到几十秒也属正常。

### Render 配置参数（直接复制到控制台）

在 Render 的 **Build & Deploy** 里，请**严格按下面填写**（不要多写 `$` 或换行）：

```
Build Command:
pip install -r requirements.txt

Start Command:
python -m gunicorn -w 1 -b 0.0.0.0:$PORT app:app
```

- **Root Directory**：留空（项目在仓库根目录时）。
- **Environment**：如需真实 X 数据，添加 Key `X_BEARER_TOKEN`，Value 填你的 Bearer Token。
- **requirements.txt**：必须包含且仅保留以下 4 行依赖（无重复、无行内注释）：
  - `tweepy>=4.14.0`
  - `python-dotenv>=1.0.0`
  - `flask>=2.3.0`
  - `gunicorn>=21.0.0`

若之前配置失败，请先同步本仓库最新的 `requirements.txt` 到 GitHub，再在 Render 里用上述 Build/Start Command 重新部署。

---

## 方式三：部署到 Railway

1. 将项目推送到 **GitHub**。
2. 打开 [railway.app](https://railway.app)，用 GitHub 登录，**New Project → Deploy from GitHub**，选本仓库。
3. 在项目设置里添加 **Variable**：`X_BEARER_TOKEN` = 你的 Token（可选）。
4. Railway 会自动识别 `Procfile` 并执行 `web: gunicorn ...`。
5. 在 **Settings → Networking** 中生成公网域名，之后访问该域名即可。

---

## 方式四：本机 + 内网穿透（无云账号时）

在本机运行 `python app.py` 后，用内网穿透把 5000 端口暴露到公网：

- **ngrok**：`ngrok http 5000`，会得到一个 `https://xxx.ngrok.io` 临时网址。
- **cpolar / frp** 等：按各自文档配置，得到固定或临时域名。

每天打开该网址即可查看日报（需本机与穿透服务同时在线）。

---

## 与邮件日报的关系

- **main.py**：生成日报并**发邮件**（适合配合 cron 每天 7 点跑）。
- **app.py**：只提供**网页查看**，不发邮件；可单独部署，也可与 main.py 并存（cron 发邮件 + 随时打开网页看）。

两者共用同一套数据源与报告逻辑，仅输出方式不同。
