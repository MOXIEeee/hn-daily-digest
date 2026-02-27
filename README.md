# HN Top Blogs Daily Digest

每天自动抓取 Hacker News 2025 最热门博客，生成中文摘要并发送到邮箱。

## 用途

这个项目会自动：
1. 抓取 94 个技术博客的最新文章
2. 使用 AI 生成中文摘要
3. 每天定时发送到你的邮箱

## 配置

1. Fork 这个仓库
2. 在仓库 Settings 中添加 Secrets：
   - `EMAIL_USER` - 你的 Gmail 地址
   - `EMAIL_PASSWORD` - Gmail 应用密码
   - `TO_EMAIL` - 接收摘要的邮箱地址

## 获取 Gmail 应用密码

1. 开启 Gmail 两步验证
2. 访问 https://myaccount.google.com/apppasswords
3. 生成应用密码

## 手动触发

可以在 GitHub Actions 页面手动运行 workflow。
