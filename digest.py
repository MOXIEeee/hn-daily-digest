"""
HN Top Blogs Daily Digest - Main Script
抓取 94 个技术博客的最新文章，生成中文摘要，发送到邮箱
"""

import feedparser
import requests
import smtplib
import json
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time

# RSS 订阅源列表（HN 2025 最热门博客）
RSS_FEEDS = [
    ("simonwillison.net", "https://simonwillison.net/atom/everything/"),
    ("jeffgeerling.com", "https://www.jeffgeerling.com/blog.xml"),
    ("seangoedecke.com", "https://www.seangoedecke.com/rss.xml"),
    ("krebsonsecurity.com", "https://krebsonsecurity.com/feed/"),
    ("daringfireball.net", "https://daringfireball.net/feeds/main"),
    ("ericmigi.com", "https://ericmigi.com/rss.xml"),
    ("antirez.com", "http://antirez.com/rss"),
    ("idiallo.com", "https://idiallo.com/feed.rss"),
    ("maurycyz.com", "https://maurycyz.com/index.xml"),
    ("pluralistic.net", "https://pluralistic.net/feed/"),
    ("shkspr.mobi", "https://shkspr.mobi/blog/feed/"),
    ("lcamtuf.substack.com", "https://lcamtuf.substack.com/feed"),
    ("mitchellh.com", "https://mitchellh.com/feed.xml"),
    ("dynomight.net", "https://dynomight.net/feed.xml"),
    ("utcc.utoronto.ca", "https://utcc.utoronto.ca/~cks/space/blog/?atom"),
    ("xeiaso.net", "https://xeiaso.net/blog.rss"),
    ("oldnewthing", "https://devblogs.microsoft.com/oldnewthing/feed"),
    ("righto.com", "https://www.righto.com/feeds/posts/default"),
    ("lucumr.pocoo.org", "https://lucumr.pocoo.org/feed.atom"),
    ("skyfall.dev", "https://skyfall.dev/rss.xml"),
    ("garymarcus.substack.com", "https://garymarcus.substack.com/feed"),
    ("rachelbythebay.com", "https://rachelbythebay.com/w/atom.xml"),
    ("overreacted.io", "https://overreacted.io/rss.xml"),
    ("timsh.org", "https://timsh.org/rss/"),
    ("johndcook.com", "https://www.johndcook.com/blog/feed/"),
    ("gilesthomas.com", "https://gilesthomas.com/feed/rss.xml"),
    ("matklad.github.io", "https://matklad.github.io/feed.xml"),
    ("derekthompson.org", "https://www.theatlantic.com/feed/author/derek-thompson/"),
    ("evanhahn.com", "https://evanhahn.com/feed.xml"),
    ("terriblesoftware.org", "https://terriblesoftware.org/feed/"),
    ("rakhim.exotext.com", "https://rakhim.exotext.com/rss.xml"),
    ("joanwestenberg.com", "https://joanwestenberg.com/rss"),
    ("xania.org", "https://xania.org/feed"),
    ("micahflee.com", "https://micahflee.com/feed/"),
    ("nesbitt.io", "https://nesbitt.io/feed.xml"),
    ("construction-physics.com", "https://www.construction-physics.com/feed"),
    ("tedium.co", "https://feed.tedium.co/"),
    ("susam.net", "https://susam.net/feed.xml"),
    ("entropicthoughts.com", "https://entropicthoughts.com/feed.xml"),
    ("hillelwayne", "https://buttondown.com/hillelwayne/rss"),
    ("dwarkesh.com", "https://www.dwarkeshpatel.com/feed"),
    ("borretti.me", "https://borretti.me/feed.xml"),
    ("wheresyoured.at", "https://www.wheresyoured.at/rss/"),
    ("jayd.ml", "https://jayd.ml/feed.xml"),
    ("minimaxir.com", "https://minimaxir.com/index.xml"),
    ("geohot.github.io", "https://geohot.github.io/blog/feed.xml"),
    ("paulgraham.com", "http://www.aaronsw.com/2002/feeds/pgessays.rss"),
    ("filfre.net", "https://www.filfre.net/feed/"),
    ("jim-nielsen.com", "https://blog.jim-nielsen.com/feed.xml"),
    ("dfarq.homeip.net", "https://dfarq.homeip.net/feed/"),
    ("jyn.dev", "https://jyn.dev/atom.xml"),
    ("geoffreylitt.com", "https://www.geoffreylitt.com/feed.xml"),
    ("downtowndougbrown.com", "https://www.downtowndougbrown.com/feed/"),
    ("brutecat.com", "https://brutecat.com/rss.xml"),
    ("eli.thegreenplace.net", "https://eli.thegreenplace.net/feeds/all.atom.xml"),
    ("abortretry.fail", "https://www.abortretry.fail/feed"),
    ("fabiensanglard.net", "https://fabiensanglard.net/rss.xml"),
    ("oldvcr.blogspot.com", "https://oldvcr.blogspot.com/feeds/posts/default"),
    ("bogdanthegeek.github.io", "https://bogdanthegeek.github.io/blog/index.xml"),
    ("hugotunius.se", "https://hugotunius.se/feed.xml"),
    ("gwern.net", "https://gwern.substack.com/feed"),
    ("berthub.eu", "https://berthub.eu/articles/index.xml"),
    ("chadnauseam.com", "https://chadnauseam.com/rss.xml"),
    ("simone.org", "https://simone.org/feed/"),
    ("it-notes.dragas.net", "https://it-notes.dragas.net/feed/"),
    ("beej.us", "https://beej.us/blog/rss.xml"),
    ("hey.paris", "https://hey.paris/index.xml"),
    ("danielwirtz.com", "https://danielwirtz.com/rss.xml"),
    ("matduggan.com", "https://matduggan.com/rss/"),
    ("refactoringenglish.com", "https://refactoringenglish.com/index.xml"),
    ("worksonmymachine.substack.com", "https://worksonmymachine.substack.com/feed"),
    ("philiplaine.com", "https://philiplaine.com/index.xml"),
    ("steveblank.com", "https://steveblank.com/feed/"),
    ("bernsteinbear.com", "https://bernsteinbear.com/feed.xml"),
    ("danieldelaney.net", "https://danieldelaney.net/feed"),
    ("troyhunt.com", "https://www.troyhunt.com/rss/"),
    ("hermen.bearblog.dev", "https://herman.bearblog.dev/feed/"),
    ("tomrenner.com", "https://tomrenner.com/index.xml"),
    ("blog.pixelmelt.dev", "https://blog.pixelmelt.dev/rss/"),
    ("martinalderson.com", "https://martinalderson.com/feed.xml"),
    ("danielchasehooper.com", "https://danielchasehooper.com/feed.xml"),
    ("sgtatham", "https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/feed.xml"),
    ("grantslatton.com", "https://grantslatton.com/rss.xml"),
    ("experimental-history.com", "https://www.experimental-history.com/feed"),
    ("anildash.com", "https://anildash.com/feed.xml"),
    ("aresluna.org", "https://aresluna.org/main.rss"),
    ("michael.stapelberg.ch", "https://michael.stapelberg.ch/feed.xml"),
    ("miguelgrinberg.com", "https://blog.miguelgrinberg.com/feed"),
    ("keygen.sh", "https://keygen.sh/blog/feed.xml"),
    ("mjg59.dreamwidth.org", "https://mjg59.dreamwidth.org/data/rss"),
    ("computer.rip", "https://computer.rip/rss.xml"),
    ("tedunangst.com", "https://www.tedunangst.com/flak/rss"),
]

# 只获取过去24小时内的文章
def is_recent(entry, hours=24):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        pub_date = datetime(*entry.published_parsed[:6])
        return datetime.now() - pub_date < timedelta(hours=hours)
    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        upd_date = datetime(*entry.updated_parsed[:6])
        return datetime.now() - upd_date < timedelta(hours=hours)
    return False

# 抓取 RSS 源
def fetch_recent_articles(hours=24, max_per_feed=3):
    """获取最近 hours 小时内发布的文章"""
    articles = []

    for name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                continue

            count = 0
            for entry in feed.entries[:10]:  # 先取前10个
                if count >= max_per_feed:
                    break
                if is_recent(entry, hours):
                    title = entry.get('title', 'No title')
                    link = entry.get('link', '')
                    summary = entry.get('summary', entry.get('description', ''))

                    # 清理 HTML 标签
                    import re
                    summary_text = re.sub(r'<[^>]+>', '', summary)[:500]

                    articles.append({
                        'source': name,
                        'title': title,
                        'link': link,
                        'summary': summary_text
                    })
                    count += 1

        except Exception as e:
            print(f"Error fetching {name}: {e}")
            continue

    return articles

# 使用免费的 AI API 生成摘要
def generate_summary_with_ai(articles):
    """使用 AI 生成中文摘要"""

    if not articles:
        return []

    # 准备文章列表（限制数量避免API超限）
    article_texts = []
    for i, art in enumerate(articles[:20]):  # 最多处理20篇
        article_texts.append(f"""
{i+1}. 【{art['source']}】{art['title']}
摘要: {art['summary'][:300]}
""")

    prompt = f"""你是一个科技博客编辑。请为以下技术/创业/AI博客文章生成中文摘要。

要求：
1. 用中文输出
2. 对每篇文章进行分类：编程技术、AI机器学习、硬件物理、商业创业、其他
3. 每篇用 2-3 句话详细概括核心观点、作者论点和价值
4. 优先推荐AI和商业创业类文章

文章列表：
{''.join(article_texts)}

请按以下格式输出：
---

### 🚀 AI机器学习

**1. [博客名] 文章标题**
   分类：AI机器学习
   核心观点：xxx（2-3句话详细说明）

### 💻 编程技术

**1. [博客名] 文章标题**
   分类：编程技术
   核心观点：xxx

### 🔧 硬件物理

**1. [博客名] 文章标题**
   分类：硬件物理
   核心观点：xxx

### 💰 商业创业

**1. [博客名] 文章标题**
   分类：商业创业
   核心观点：xxx

### 📌 其他

**1. [博客名] 文章标题**
   分类：其他
   核心观点：xxx
"""

    try:
        # 使用 Google Gemini API（免费额度较大）
        api_key = os.environ.get('GEMINI_API_KEY', '')

        if api_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 4000
                }
            }

            response = requests.post(url, headers=headers, json=data, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']

        # 如果没有 API key，使用简单处理
        return generate_simple_summary(articles)

    except Exception as e:
        print(f"AI summary error: {e}")
        return generate_simple_summary(articles)

def generate_simple_summary(articles):
    """简单的摘要生成（当 AI 不可用时）"""
    if not articles:
        return "今日暂无更新。"

    output = ["### 今日博客更新\n"]

    for i, art in enumerate(articles[:15], 1):
        output.append(f"**{i}. [{art['source']}] {art['title']}**")
        if art['summary']:
            summary_line = art['summary'][:150].replace('\n', ' ')
            output.append(f"   {summary_line}...")
        output.append(f"   [阅读原文]({art['link']})")
        output.append("")

    return '\n'.join(output)

# 发送邮件
def send_email(content, to_email):
    """发送邮件"""
    email_user = os.environ.get('EMAIL_USER', '')
    email_password = os.environ.get('EMAIL_PASSWORD', '')

    if not email_user or not email_password:
        print("Email credentials not set")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📰 技术博客每日摘要 - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = email_user
        msg['To'] = to_email

        # HTML 格式
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; }}
                .article {{ margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
                .source {{ color: #666; font-size: 12px; }}
                .title {{ font-size: 16px; font-weight: bold; margin: 5px 0; }}
                .summary {{ color: #333; }}
                .link {{ color: #0066cc; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h2>📰 技术博客每日摘要</h2>
            <p>来源：Hacker News 2025 最热门博客 ({datetime.now().strftime('%Y-%m-%d')})</p>
            <hr>
            {content}
            <hr>
            <p style="color: #999; font-size: 12px;">
                本摘要由 AI 自动生成，来源为 HN 2025 最热门的技术/创业/AI 博客。
            </p>
        </body>
        </html>
        """

        # 纯文本格式
        text_content = content.replace('<br>', '\n').replace('<b>', '').replace('</b>', '')

        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # 发送邮件
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, to_email, msg.as_string())
        server.quit()

        print(f"Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False

def main():
    print(f"Starting HN Daily Digest at {datetime.now()}")

    # 1. 抓取最近24小时的最新文章
    print("Fetching recent articles...")
    articles = fetch_recent_articles(hours=24)

    if not articles:
        print("No recent articles found")
        return

    print(f"Found {len(articles)} recent articles")

    # 2. 生成摘要
    print("Generating summary with AI...")
    summary = generate_summary_with_ai(articles)

    # 3. 转换为可发送格式
    email_content = format_email_content(articles, summary)

    # 4. 发送邮件
    to_email = os.environ.get('TO_EMAIL', 'zhaomuxi77@gmail.com')
    print(f"Sending to {to_email}...")
    send_email(email_content, to_email)

    print("Done!")

def format_email_content(articles, ai_summary):
    """格式化邮件内容"""

    html = ""

    # AI 摘要部分
    if ai_summary:
        html += f"""
        <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin-top: 0;">🤖 AI 摘要</h3>
            <pre style="white-space: pre-wrap; font-family: inherit;">{ai_summary}</pre>
        </div>
        """

    # 文章列表
    html += "<h3>📄 全部更新</h3>"

    for i, art in enumerate(articles[:20], 1):
        html += f"""
        <div class="article">
            <div class="source">{art['source']}</div>
            <div class="title">{i}. {art['title']}</div>
            <div class="summary">{art['summary'][:200]}...</div>
            <a class="link" href="{art['link']}">阅读原文 →</a>
        </div>
        """

    return html

if __name__ == "__main__":
    main()
