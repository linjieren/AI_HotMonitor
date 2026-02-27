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

1. 将本项目推送到 **GitHub**（新建仓库并 push）。
2. 打开 [render.com](https://render.com)，注册/登录，点击 **New → Web Service**。
3. 连接你的 GitHub 仓库，选择本项目所在仓库。
4. 配置（必填项）：
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**（必须带 `$PORT`，否则 Render 无法转发流量）：`gunicorn -w 1 -b 0.0.0.0:$PORT app:app`  
     注意：不能只填 `gunicorn app:app`，否则应用不会监听 Render 提供的端口，页面会一直加载失败。
   - **Environment Variables**：添加 `X_BEARER_TOKEN`，值为你在 X Developer Portal 复制的 Bearer Token（可选，不填则用模拟数据）。
5. 点击 **Create Web Service**，等待部署完成。
6. 在 Render 控制台会得到一个 URL（如 `https://xxx.onrender.com`），每天打开该链接即可看最新日报。

注意：免费实例一段时间无访问会休眠，首次打开可能较慢；点击页头「刷新数据」或访问 `/refresh` 可强制更新数据。

**Render 加载过长 / 失败时自检清单：**

| 检查项 | 正确做法 |
|--------|----------|
| **Start Command** | 必须为 `gunicorn -w 1 -b 0.0.0.0:$PORT app:app`。不能是 `gunicorn app:app`（缺少 `-b 0.0.0.0:$PORT` 会导致不监听 Render 的端口，页面一直转圈或 503）。 |
| **Environment Variables** | 在 Render 控制台 → 你的 Web Service → Environment 中添加变量：Key = `X_BEARER_TOKEN`，Value = 你的 Bearer Token（从 X Developer Portal 复制，不要有多余空格或换行）。不填也可运行，但会使用模拟数据。 |
| **requirements.txt** | 需包含：`flask`、`gunicorn`、`tweepy`、`python-dotenv`。本项目已包含，无需修改。 |
| **Build Command** | `pip install -r requirements.txt`（或留空，Render 有时会自动识别）。 |

免费实例冷启动约 30 秒～1 分钟属正常；首次打开首页会拉取数据并生成报告，再等几秒到几十秒也属正常。

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
