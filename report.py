# -*- coding: utf-8 -*-
"""
日报生成：交互式 HTML 报告（卡片布局、排序、筛选、帖子内嵌展示、链接可访问性标注）
适合在浏览器中打开查看；邮件中可能仅显示静态内容。
"""

from datetime import datetime


def _escape(s):
    """简单转义，避免 HTML 注入"""
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _time_sort_key(t):
    """把 'YYYY-MM-DD HH:MM' 转为可排序的字符串"""
    if not t:
        return "0000-00-00 00:00"
    return str(t)[:16].strip()


def build_daily_report(influencers, products, date_str=None):
    """
    生成交互式日报 HTML
    :param influencers: 博主列表（含 avatar_url, post_content, link_ok 等）
    :param products: 新品列表（含 link_ok 等）
    :param date_str: 日期，默认今天
    :return: (subject, html_body)
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    subject = f"【AI前沿日报】{date_str}"
    influencers = sorted(influencers, key=lambda x: x.get("rank", 99))
    products = sorted(products, key=lambda x: x.get("rank", 99))
    total = len(influencers) + len(products)
    # 博主分类及计数（用于筛选按钮）
    from collections import Counter
    cat_counts = Counter(row.get("category") or "其他" for row in influencers)
    cat_order = [c for c in cat_counts.keys() if c]
    cat_order = sorted(cat_order, key=lambda c: -cat_counts[c])

    # 顶部：标题 + 日期 + 数据概览
    html = [
        '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>{_escape(subject)}</title>',
        _styles(),
        "</head><body>",
        '<header class="report-header">',
        '<div class="report-title">📊 AI 前沿日报</div>',
        f'<div class="report-date">{_escape(date_str)}</div>',
        f'<div class="report-meta">生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")} · 每日自动更新 · <a href="/refresh" class="btn-refresh">刷新数据</a></div>',
        "</header>",
        '<section class="overview">',
        f'<div class="overview-card"><span class="overview-num">{total}</span> 总数据条目</div>',
        f'<div class="overview-card"><span class="overview-num">{len(cat_order) + 1}</span> 数据分类</div>',
        "</section>",
        '<section class="controls">',
        '<div class="control-group"><span class="control-label">排序:</span>',
        '<button type="button" class="btn-sort active" data-sort="default">默认排序</button>',
        '<button type="button" class="btn-sort" data-sort="time">最新发布</button>',
        '<button type="button" class="btn-sort" data-sort="followers">粉丝量↓</button>',
        '<button type="button" class="btn-sort" data-sort="heat">热度↓</button>',
        '</div>',
        '<div class="control-group"><span class="control-label">分类:</span>',
        f'<button type="button" class="btn-filter active" data-filter="all">全部({total})</button>',
    ]
    for c in cat_order:
        html.append(f'<button type="button" class="btn-filter" data-filter="{_escape(c)}">{_escape(c)}({cat_counts[c]})</button>')
    html.append(f'<button type="button" class="btn-filter" data-filter="AI新品">AI新品({len(products)})</button>')
    html.append('</div></section>')
    html.append('<div id="card-list" class="card-list">')

    # 博主卡片：姓名与 handle 对应，展示简介/基本信息，内容要点 50-100 字
    for i, row in enumerate(influencers):
        link_ok = row.get("link_ok", None)
        post_url = row.get("url", "#")
        post_content = _escape(row.get("post_content") or row.get("summary", ""))
        # #region agent log
        if i < 5:
            try:
                _log_path = "/Users/renlinjie/hot监测/.cursor/debug-06c7b3.log"
                _raw_content = (row.get("post_content") or row.get("summary") or "")[:50]
                _payload = {"sessionId": "06c7b3", "hypothesisId": "E", "location": "report.py:build_daily_report", "message": "render influencer row", "data": {"index": i, "post_url": post_url, "post_content_preview": _raw_content, "handle": row.get("handle")}, "timestamp": __import__("time").time() * 1000}
                open(_log_path, "a", encoding="utf-8").write(__import__("json").dumps(_payload, ensure_ascii=False) + "\n")
            except Exception:
                pass
        # #endregion
        summary_100 = _escape(row.get("summary") or "")[:105]
        profile_url = f"https://x.com/{_escape(row.get('handle', ''))}"
        time_val = _time_sort_key(row.get("publish_time"))
        likes = _format_engagement(row.get("like_count", 0))
        retweets = _format_engagement(row.get("retweet_count", 0))
        replies = _format_engagement(row.get("reply_count", 0))
        cat = _escape(row.get("category") or "其他")
        description = _escape((row.get("description") or "").strip())
        profile_link = (row.get("profile_url") or "").strip()
        joined_at = (row.get("joined_at") or "").strip()
        following = row.get("following_count")
        card_meta_extra = []
        if description:
            card_meta_extra.append(f'<p class="card-description">{description}</p>')
        if profile_link:
            card_meta_extra.append(f'<a class="card-profile-link" href="{_escape(profile_link)}" target="_blank" rel="noopener">🔗 {_escape(profile_link[:40])}{"…" if len(profile_link) > 40 else ""}</a>')
        if joined_at:
            card_meta_extra.append(f'<span class="card-joined">加入 {_escape(joined_at)}</span>')
        if following is not None:
            try:
                card_meta_extra.append(f'<span class="card-following">关注 {_format_engagement(int(following))}</span>')
            except (TypeError, ValueError):
                pass
        html.append(
            f'<article class="card card-influencer" data-category="{cat}" data-rank="{row.get("rank", 0)}" '
            f'data-time="{_escape(time_val)}" data-followers="{row.get("followers_num", 0)}" data-heat="0">'
            f'<div class="card-badge">#{row.get("rank", i+1)}</div>'
            f'<div class="card-body">'
            f'<div class="card-head">'
            f'<a href="{profile_url}" target="_blank" rel="noopener" class="card-avatar-wrap"><img class="card-avatar" src="{_escape(row.get("avatar_url", ""))}" alt="" width="48" height="48"></a>'
            f'<div class="card-meta">'
            f'<span class="card-name">{_escape(row.get("name", ""))}</span>'
            f'<a class="card-handle" href="{profile_url}" target="_blank" rel="noopener">@{_escape(row.get("handle", ""))}</a>'
            f'<span class="card-followers">👥 {_escape(row.get("followers", ""))}</span>'
            f'<span class="card-time">🕐 {_escape(row.get("publish_time", ""))}</span>'
            + ("".join(card_meta_extra))
            + f'</div></div>'
            f'<div class="card-summary-block"><strong>内容要点</strong><p class="card-summary">{summary_100}</p></div>'
            f'<div class="card-actions">'
            f'<span class="action-item"><span class="action-icon">♥</span> {likes}</span>'
            f'<span class="action-item"><span class="action-icon">↻</span> {retweets}</span>'
            f'<span class="action-item"><span class="action-icon">💬</span> {replies}</span>'
            f'<span class="action-item action-link"><a href="{_escape(post_url)}" target="_blank" rel="noopener">跳转原文</a></span>'
            f'<span class="action-item link-status">{_link_badge_only(link_ok)}</span>'
            f'</div>'
            f'<div class="card-footer">'
            f'<span class="tag-mention">{"提及新品" if row.get("mentions_product") else "—"}</span>'
            f'</div></div></article>'
        )

    # 新品卡片：同样采用交互式卡片，下方为体验链接 + 团队/热度
    for i, row in enumerate(products):
        link_ok = row.get("link_ok", None)
        exp_url = row.get("link", "#")
        time_val = _time_sort_key(row.get("publish_time"))
        html.append(
            f'<article class="card card-product" data-category="AI新品" data-rank="{row.get("rank", 0)}" '
            f'data-time="{_escape(time_val)}" data-followers="0" data-heat="{row.get("heat_score", 1)}">'
            f'<div class="card-badge">#{row.get("rank", i+1)}</div>'
            f'<div class="card-body">'
            f'<div class="card-head"><div class="card-meta">'
            f'<span class="card-name">{_escape(row.get("name", ""))}</span>'
            f'<span class="card-time">🕐 {_escape(row.get("publish_time", ""))}</span>'
            f'</div></div>'
            f'<p class="card-feature">{_escape(row.get("feature", ""))}</p>'
            f'<div class="card-actions">'
            f'<span class="action-item action-link"><a href="{_escape(exp_url)}" target="_blank" rel="noopener" class="btn-experience">体验产品</a></span>'
            f'<span class="action-item link-status">{_link_badge_only(link_ok)}</span>'
            f'<span class="action-item card-team">团队: {_escape(row.get("team", ""))}</span>'
            f'<span class="action-item card-heat">热度: {_escape(row.get("heat", ""))}</span>'
            f'</div>'
            f'<div class="card-footer"></div></div></article>'
        )

    html.append("</div>")
    html.append(_script())
    html.append('<p class="footer-note">— 本日报由 AI 前沿监控工具自动生成，链接已做可访问性检测。X 原文链接不检测，请在浏览器中点击「原文」打开。若为示例数据，原文为占位链接，配置 X API 后重新生成即可获得可打开的 X 推文链接。</p>')
    html.append("</body></html>")
    return subject, "".join(html)


def _format_engagement(n):
    """互动数格式化：过万显示 1.2w"""
    if n is None or n < 0:
        return "0"
    if n >= 10000:
        return f"{n / 10000:.1f}w".replace(".0w", "w")
    if n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)


def _link_badge(link_ok, url, text):
    """生成带可访问性标注的链接"""
    if link_ok is True:
        badge = '<span class="link-ok">可访问</span>'
    elif link_ok is False:
        badge = '<span class="link-fail">不可访问</span>'
    else:
        badge = '<span class="link-unknown">未检测</span>'
    return f'<a href="{_escape(url)}" target="_blank" rel="noopener">{_escape(text)}</a> {badge}'


def _link_badge_only(link_ok):
    """仅返回可访问性标注（无链接）"""
    if link_ok is True:
        return '<span class="link-ok">可访问</span>'
    if link_ok is False:
        return '<span class="link-fail">不可访问</span>'
    return '<span class="link-unknown">未检测</span>'


def _styles():
    return """
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif; max-width: 920px; margin: 0 auto; padding: 20px; color: #1a1a1a; background: #f0f2f5; }
  .report-header { text-align: center; margin-bottom: 24px; padding: 20px; background: linear-gradient(135deg, #1a237e 0%, #283593 100%); color: #fff; border-radius: 12px; }
  .report-title { font-size: 1.5rem; font-weight: 700; letter-spacing: 0.02em; }
  .report-date { opacity: 0.9; margin-top: 6px; font-size: 0.95rem; }
  .report-meta { font-size: 0.8rem; opacity: 0.8; margin-top: 4px; }
  .btn-refresh { display: inline-block; margin-left: 6px; padding: 4px 10px; background: #1a237e; color: #fff; border-radius: 6px; text-decoration: none; font-size: 0.85rem; }
  .btn-refresh:hover { background: #283593; color: #fff; }
  .overview { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
  .overview-card { background: #fff; padding: 14px 22px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.06); font-size: 0.95rem; }
  .overview-num { font-weight: 700; color: #1a237e; margin-right: 4px; }
  .controls { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; margin-bottom: 20px; padding: 14px 18px; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
  .control-group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .control-label { font-weight: 600; color: #444; font-size: 0.9rem; }
  .btn-sort, .btn-filter { padding: 8px 14px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fff; cursor: pointer; font-size: 0.88rem; transition: all 0.2s; }
  .btn-sort:hover, .btn-filter:hover { background: #f5f5f5; border-color: #1a237e; color: #1a237e; }
  .btn-sort.active, .btn-filter.active { background: #1a237e; color: #fff; border-color: #1a237e; }
  .card-list { display: flex; flex-direction: column; gap: 18px; }
  .card { position: relative; background: #fff; border-radius: 12px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,.06); transition: box-shadow 0.2s; }
  .card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.1); }
  .card-badge { position: absolute; top: 14px; right: 14px; background: #1a237e; color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
  .card-avatar-wrap { display: block; }
  .card-avatar { border-radius: 50%; object-fit: cover; display: block; }
  .card-head { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 12px; }
  .card-meta { display: flex; flex-direction: column; gap: 4px; }
  .card-name { font-weight: 600; font-size: 1rem; }
  .card-handle { color: #1a237e; text-decoration: none; font-size: 0.9rem; }
  .card-handle:hover { text-decoration: underline; }
  .card-followers, .card-time { font-size: 0.85rem; color: #666; }
  .card-description { margin: 6px 0 0; font-size: 0.88rem; color: #555; line-height: 1.4; }
  .card-profile-link { display: inline-block; margin-top: 2px; font-size: 0.8rem; color: #1a237e; text-decoration: none; }
  .card-profile-link:hover { text-decoration: underline; }
  .card-joined, .card-following { font-size: 0.8rem; color: #888; margin-right: 10px; }
  .card-summary-block { margin: 10px 0; padding: 8px 12px; background: #f0f4ff; border-radius: 8px; }
  .card-summary-block .card-summary { margin: 4px 0 0; font-size: 0.9rem; line-height: 1.5; color: #333; }
  .card-post { background: #f8f9fa; border-left: 4px solid #1a237e; padding: 12px 14px; margin: 12px 0; border-radius: 0 8px 8px 0; }
  .post-content { margin: 0; font-size: 0.95rem; line-height: 1.6; color: #333; }
  .card-feature { margin: 10px 0; font-size: 0.95rem; line-height: 1.55; color: #444; }
  .card-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 16px; padding: 10px 0; border-top: 1px solid #eee; margin-top: 8px; font-size: 0.85rem; color: #555; }
  .action-item { display: inline-flex; align-items: center; gap: 4px; }
  .action-icon { opacity: 0.85; }
  .action-link a { color: #1a237e; text-decoration: none; font-weight: 500; }
  .action-link a:hover { text-decoration: underline; }
  .btn-experience { display: inline-block; padding: 6px 14px; background: #1a237e; color: #fff; border-radius: 8px; text-decoration: none; font-weight: 500; }
  .btn-experience:hover { background: #283593; }
  .card-footer { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; font-size: 0.85rem; color: #666; margin-top: 4px; }
  .tag-mention { color: #6f42c1; }
  .link-ok { color: #198754; font-size: 0.8rem; }
  .link-fail { color: #dc3545; font-size: 0.8rem; }
  .link-unknown { color: #6c757d; font-size: 0.8rem; }
  .link-status { margin-left: auto; }
  .card-team, .card-heat { color: #666; }
  .footer-note { font-size: 0.8rem; color: #999; margin-top: 28px; line-height: 1.5; }
</style>
"""


def _script():
    return """
<script>
(function(){
  var list = document.getElementById('card-list');
  var cards = Array.from(list.querySelectorAll('.card'));
  var sortBtns = document.querySelectorAll('.btn-sort');
  var filterBtns = document.querySelectorAll('.btn-filter');
  var currentSort = 'default';
  var currentFilter = 'all';

  function apply() {
    var filtered = currentFilter === 'all' ? cards : cards.filter(function(c){ return c.dataset.category === currentFilter; });
    if (currentSort === 'time') filtered.sort(function(a,b){ return (b.dataset.time || '').localeCompare(a.dataset.time || ''); });
    else if (currentSort === 'followers') filtered.sort(function(a,b){ return Number(b.dataset.followers || 0) - Number(a.dataset.followers || 0); });
    else if (currentSort === 'heat') filtered.sort(function(a,b){ return Number(b.dataset.heat || 0) - Number(a.dataset.heat || 0); });
    else filtered.sort(function(a,b){ return Number(a.dataset.rank || 0) - Number(b.dataset.rank || 0); });
    filtered.forEach(function(c){ list.appendChild(c); });
  }

  sortBtns.forEach(function(btn){
    btn.addEventListener('click', function(){
      sortBtns.forEach(function(b){ b.classList.remove('active'); });
      this.classList.add('active');
      currentSort = this.dataset.sort;
      apply();
    });
  });
  filterBtns.forEach(function(btn){
    btn.addEventListener('click', function(){
      filterBtns.forEach(function(b){ b.classList.remove('active'); });
      this.classList.add('active');
      currentFilter = this.dataset.filter;
      apply();
    });
  });
})();
</script>
"""
