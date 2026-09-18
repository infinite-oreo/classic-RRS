# classic RRS

一个跑在本机的个人比赛情报聚合工具:订阅AI/编程比赛相关的RSS/Atom源(Hackathon公告、AI比赛资讯、CTF/编程竞赛讨论等),后台定时抓取,每天在"今日摘要"页面按订阅源分组、按分类筛选查看更新,方便随时发现值得报名的比赛。

## 首次运行

```bash
cd "classic RRS"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

打开浏览器访问 http://127.0.0.1:5000/today

首次运行会自动在 `data/app.db` 建库建表,不需要手动初始化。

## 一键导入比赛类订阅源

`seed_feeds.py` 里预置了一批验证可用的 AI/编程比赛相关 RSS 源(MLH、Dev.to 的 hackathon/ai/machinelearning/llm/competition 标签、Hacker News 关键词搜索等),分好 `Hackathon`/`AI比赛`/`编程比赛` 三个分类:

```bash
source venv/bin/activate
python seed_feeds.py
```

重复运行是安全的,已存在的订阅源会自动跳过。这些RSS源多是"比赛相关讨论/资讯"而非官方比赛日历(Devpost、Kaggle、HackerEarth等平台官方都不提供比赛列表RSS),想追更权威的比赛信息还是需要手动去 `/feeds` 页面添加你自己找到的赛事源。

## 日常使用

- `/feeds` 添加订阅源(填RSS地址即可,标题可留空自动获取,分类建议按 `Hackathon`/`AI比赛`/`编程比赛` 之类的关键词填,方便在今日摘要里筛选)
- `/opml/import` 从其他RSS阅读器批量导入订阅列表
- `/today` 查看当天新抓到的内容,默认按订阅源分组、只显示未读,顶部有分类筛选条可以只看某一类比赛信息
- `/archive` 按日期回看历史内容,同样支持分类筛选
- 默认每15分钟自动抓取一次,也可以在 `/feeds` 页面点"立即刷新"手动触发

## 长期后台常驻(launchd)

不想每次开机手动 `python run.py`,可以用 macOS 的 launchd 让它开机自启、崩溃自动重启:

```bash
cp launchd/com.classicrss.app.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.classicrss.app.plist
```

- 查看是否在跑:`launchctl list | grep classicrss`
- 看日志:`tail -f "data/logs/stdout.log"` 或 `stderr.log`
- 重新拉起(改代码后):
  ```bash
  launchctl unload ~/Library/LaunchAgents/com.classicrss.app.plist
  launchctl load ~/Library/LaunchAgents/com.classicrss.app.plist
  ```
- 停止常驻:`launchctl unload ~/Library/LaunchAgents/com.classicrss.app.plist`

plist里的路径写的是绝对路径,如果项目目录挪动了需要同步改 `launchd/com.classicrss.app.plist` 里的三处路径。

## Supabase保活

后台调度器每 `SUPABASE_KEEPALIVE_INTERVAL_HOURS`(默认24小时)会对 `app/config.py` 里配置的 Supabase 项目的 `_keepalive` 表做一次轻量 SELECT,防止免费版项目因连续7天无API活动被自动暂停。这个查询只读不写,用的是已经配置好对应RLS策略的 anon key。想换成自己另一个Supabase项目,改 `app/config.py` 里的 `SUPABASE_URL`/`SUPABASE_ANON_KEY`,并确保目标项目里有一张允许 anon 角色 SELECT 的表(表名同步改 `app/keepalive.py` 里的 URL)。

## 改端口/改抓取频率

在 `app/config.py` 里改 `PORT`(默认5000)和 `FETCH_INTERVAL_MINUTES`(默认15分钟),改完重启进程生效。

## 数据备份

所有数据都在单个文件 `data/app.db` 里,想备份/迁移直接拷贝这一个文件即可。
