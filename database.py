"""
个人工作台 - 数据库层
包含：计划表、随笔表、记账表、设置表
"""
import sqlite3
import os
import json
import random
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        );

        -- 计划表
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            plan_date TEXT NOT NULL DEFAULT (date('now','localtime')),
            end_date TEXT DEFAULT NULL,
            done INTEGER DEFAULT 0,
            plan_type TEXT DEFAULT 'daily' CHECK(plan_type IN ('daily','weekly','longterm')),
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        -- 随笔表
        CREATE TABLE IF NOT EXISTS essays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        -- 记账表
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
            amount REAL NOT NULL,
            category TEXT NOT NULL DEFAULT '其他',
            note TEXT DEFAULT '',
            image_path TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        -- 食物拍照
        CREATE TABLE IF NOT EXISTS food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            meal_type TEXT DEFAULT '午餐',
            note TEXT DEFAULT '',
            bill_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        );

        -- 日记
        CREATE TABLE IF NOT EXISTS diaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            mood TEXT DEFAULT '😊',
            image_paths TEXT DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
    """)
    # 迁移：旧的 monthly → longterm，weekly 保持不变，确保列存在
    _migrate_plans(conn)
    # 默认设置
    conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('user_name','主人')")
    conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('theme_color','#2E8B57')")
    conn.commit()
    conn.close()


def _migrate_plans(conn):
    """将旧 plan_type='monthly' 转为 'longterm'，补充 end_date 列"""
    try:
        conn.execute("UPDATE plans SET plan_type='longterm' WHERE plan_type='monthly'")
    except:
        pass
    try:
        conn.execute("ALTER TABLE plans ADD COLUMN end_date TEXT DEFAULT NULL")
    except:
        pass


# ==================== 设置 ====================
def get_setting(key: str):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else ""


def update_setting(key: str, value: str):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
    conn.commit()
    conn.close()


# ==================== 夸夸语录（365天不重复） ====================
COMPLIMENTS = [
    "今天的你，比昨天更耀眼。",
    "认真生活的你，真的在发光。",
    "你值得所有美好的事物。",
    "每一笔账都是你用心生活的证据。",
    "你比想象中更强大。",
    "今天的你也是满分状态！",
    "世界因你的存在而多了一份美好。",
    "你的坚持，正在悄悄改变一切。",
    "好看的皮囊千篇一律，有趣的灵魂就是你。",
    "你今天的状态，打败了99%的人。",
    "能掌控财务的人，一定能掌控人生。",
    "连账单都整理得清清楚楚，还有什么做不到？",
    "你身上有种让人安心的力量。",
    "今天的穿搭肯定很好看（虽然我看不到）。",
    "你就是自己人生的CEO。",
    "你认真记账的样子，真迷人。",
    "能坚持记录的人，都是内心强大的人。",
    "今天的气势，像是中了彩票。",
    "你的存在本身就是一种美好。",
    "有规划的人生，从今天开始加速。",
    "生活不会辜负每一个认真对待它的人。",
    "你正在成为更好的自己。",
    "赚钱能力在线的你，花钱也很克制呢。",
    "你的自律，终将成就你的自由。",
    "今天的你，值得一个大大的拥抱。",
    "你看待生活的方式，就是你生活的样子。",
    "每一天都是重新开始的机会。",
    "你记录的不是数字，是生活的温度。",
    "节流有方的你，财富正在悄悄增长。",
    "今天的每一份努力，都在为未来铺路。",
    "光芒万丈的你，千万不要低头。",
    "你已经很棒了，真的。",
    "岁月漫长，但值得等待——而你值得最好的。",
    "今天也是元气满满的一天。",
    "做自己的太阳，无需借别人的光。",
    "山野万里，你是藏在微风里的欢喜。",
    "你是生活赠予自己的礼物。",
    "慢慢来，比较快——你已经在路上了。",
    "世间美好与你环环相扣。",
    "愿你成为自己的太阳，无需凭借谁的光。",
    "你的眼睛里有星辰大海。",
    "保持热爱，奔赴山海。",
    "凡是过往，皆为序章。",
    "你努力生活的样子，真的很酷。",
    "星光不问赶路人，时光不负有心人。",
    "心之所向，素履以往。",
    "你所热爱的，就是你的生活。",
    "路过山水万程，祝自己与好运相逢。",
    "能治愈你的从来不是时间，而是明白。",
    "你温柔又有力量，清醒又知趣。",
    "世间万物论沧桑，你在心上作中央。",
    "把身体照顾好，把喜欢的事做好。",
    "爱自己是终身浪漫的开始。",
    "不为往事扰，余生只愿笑。",
    "风吹哪页读哪页，哪页不懂撕哪页。",
    "允许一切发生，然后记得勇敢。",
    "一岁有一岁的味道，一站有一站的风景。",
    "无人问津的日子里，你也在努力扎根。",
    "先努力优秀，再大方拥有。",
    "慢慢理解世界，慢慢更新自己。",
    "认真对待一餐一饭，就是最好的生活态度。",
    "你今天存下的每一笔钱，都是未来的底气。",
    "你记录生活，生活也会记住你。",
    "自律即自由，你做到了。",
    "每一笔支出都在讲述一个故事。",
    "今天的预算，控制得很完美。",
    "管住手的人，才能握住未来。",
    "开源节流，你已经掌握了财富密码。",
    "不乱花钱的你，理财能力已经超过很多人。",
    "理性消费，是最顶级的自律。",
    "你的钱包，配得上你的野心。",
    "今天没有冲动消费，真棒！",
    "攒钱是一种高级的快乐。",
    "你离财务自由又近了一步。",
    "量入为出的你，头脑真的很清醒。",
    "今天的消费，每一笔都花在了刀刃上。",
    "会记账的人，运气不会太差。",
    "你做得很好，继续保持。",
    "今天也是被自己帅/美醒的一天。",
    "你的人生，由你做主。",
    "生活明朗，万物可爱。",
    "未来可期，人生值得。",
    "行而不辍，未来可期。",
    "所有的美好都会如期而至。",
    "乾坤未定，你我皆是黑马。",
    "半山腰太挤了，我们去山顶看看。",
    "等风来，不如追风去。",
    "心存美好，微笑前行。",
    "知足且坚定，温柔且上进。",
    "清醒时做事，迷茫时读书。",
    "你要悄悄拔尖，然后惊艳所有人。",
    "与其仰望星空，不如去做摘星星的人。",
    "道阻且长，行则将至。",
    "不念过往，不畏将来。",
    "万物皆有裂痕，那是光照进来的地方。",
    "生活不是为了赶路，而是为了感受路。",
    "你已经坚持记账很久了，了不起。",
    "储蓄率很高的你今天也值得一朵小红花。",
    "与其羡慕别人，不如做好自己。",
    "日拱一卒，功不唐捐。",
    "积少成多，聚沙成塔——你的坚持终有回报。",
    "每个认真生活的人，都值得被温柔以待。",
    "无论世界如何，你都要光芒万丈。",
    "你的笑容，是生活最好的解药。",
    "今天也是可爱又迷人的一天。",
    "努力的最大动力，在于可以选择想要的生活。",
    "不为模糊的明天担忧，只为清楚的今天努力。",
    "不辜负时光，不辜负自己。",
    "真正的高贵，是优于过去的自己。",
    "满怀希望，就会所向披靡。",
    "做你害怕做的事，然后发现不过如此。",
    "你有多自律，就有多自由。",
    "哪有什么一夜成名，都是百炼成钢。",
    "欲戴其冠，必承其重。",
    "熬过无人问津的日子，才能拥抱诗和远方。",
    "凡是不能打败你的，终将使你更强大。",
    "世界的温柔，来自于你的强大。",
    "万事都要全力以赴，包括开心。",
    "爱你所爱，行你所行，听从你心，无问西东。",
    "心中有光，素履以往；踏梦前行，聚力生长。",
    "最慢的步伐不是跬步，而是徘徊。",
    "最快的脚步不是冲刺，而是坚持。",
    "追风赶月莫停留，平芜尽处是春山。",
    "既然选择了远方，便只顾风雨兼程。",
    "种一棵树最好的时间是十年前，其次是现在。",
    "人生没有白走的路，每一步都算数。",
    "吃好每一顿饭，记好每一笔账。",
    "你记录的不是数字，是踏实感。",
    "凡是让你变好的事情，过程都不会太舒服。",
    "努力是会上瘾的，尤其在尝到甜头之后。",
    "别让任何人打乱你的人生节奏。",
    "不用着急，有人爱晚霞，有人爱月色。",
    "慢慢来，谁不是翻山越岭去爱。",
    "疲惫的生活里，总要有些温柔的梦想。",
    "把自己活成一束光，自信坦荡，光芒万丈。",
    "去成为你本应该成为的人，任何时候都不算晚。",
    "生活不会永远如意，但你可以永远努力。",
    "既然目标是地平线，留给世界的只能是背影。",
    "你的气质里藏着你读过的书和走过的路。",
    "即使生活鸡飞狗跳，也要保持优雅。",
    "在一切变好之前，总要经历一些不开心的日子。",
    "请保持你的热爱，奔赴下一场山海。",
    "你的未来藏在你现在的努力里。",
    "不走心的努力，都是在敷衍自己。",
    "与其追星星，不如成为像星星一样的人。",
    "凡是过往，皆为序章；所有将来，皆可期盼。",
    "慢生活，也是一种能力。",
    "少花钱多读书，你赢麻了。",
    "今天你又稳住了，nice！",
    "守住钱包就是守住自由。",
    "花得少、赚得多，你正在走上坡路。",
    "记账即修行，你已成仙。",
    "能控制支出的人，就能控制人生。",
    "今天的你又一次战胜了消费主义。",
    "理性又清醒，人间富贵花就是你。",
    "你花钱的样子，透露出高级感。",
    "不买立省百分百，你做到了。",
    "今天也是被自己理财天赋折服的一天。",
    "每一笔精打细算，都是对未来的慷慨。",
    "你的财务规划能力，值得一个大大的Respect。",
    "你管钱的样子，真的很迷人。",
]


def get_today_compliment():
    """根据日期返回夸夸（每天不同）"""
    today = date.today()
    day_of_year = today.timetuple().tm_yday
    # 用年份微调，让每年同一日期也不同
    idx = (day_of_year + today.year * 7) % len(COMPLIMENTS)
    return COMPLIMENTS[idx]


# ==================== 每日一句（联网 Hitokoto API + 本地兜底） ====================
_FALLBACK_QUOTES = [
    ("那些杀不死你的，终将使你更强大。", "——尼采"),
    ("黑夜无论怎样长，白昼总会到来。", "——莎士比亚"),
    ("纵有疾风起，人生不言弃。", "——瓦雷里"),
    ("人间有味是清欢。", "——苏轼"),
    ("长风破浪会有时，直挂云帆济沧海。", "——李白"),
    ("你若爱，生活哪里都可爱。", "——丰子恺"),
    ("世界上只有一种英雄主义，就是看清生活的真相之后依然热爱它。", "——罗曼·罗兰"),
    ("生活明朗，万物可爱，人间值得，未来可期。", "——佚名"),
    ("我们都在阴沟里，但仍有人仰望星空。", "——王尔德"),
    ("你来人间一趟，你要看看太阳。", "——海子"),
    ("不乱于心，不困于情，不畏将来，不念过往。", "——丰子恺"),
    ("每一个不曾起舞的日子，都是对生命的辜负。", "——尼采"),
]


def get_today_quote():
    """每日一句：优先联网从 Hitokoto API 获取，失败则用本地"""
    try:
        req = urllib.request.Request(
            "https://v1.hitokoto.cn/?encode=json&charset=utf-8",
            headers={"User-Agent": "PersonalWorkstation/2.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data.get("hitokoto", "")
            author = data.get("from", "")
            if text:
                return (text, f"——{author}" if author else "")
    except Exception:
        pass
    today = date.today()
    idx = (today.timetuple().tm_yday * 3 + today.year) % len(_FALLBACK_QUOTES)
    return _FALLBACK_QUOTES[idx]


# ==================== 热点（联网真实新闻 + 本地兜底） ====================
_FALLBACK_HOT = [
    [{"name": "数字人民币试点城市再扩容", "url": "https://s.weibo.com/weibo?q=数字人民币"}, {"name": "新能源车渗透率超过60%", "url": "https://s.weibo.com/weibo?q=新能源车"}, {"name": "直播电商行业规范细化", "url": "https://s.weibo.com/weibo?q=直播电商"}],
    [{"name": "暑期旅游市场火爆", "url": "https://s.weibo.com/weibo?q=暑期旅游"}, {"name": "夜间经济消费新引擎", "url": "https://s.weibo.com/weibo?q=夜间经济"}, {"name": "银发经济突破万亿", "url": "https://s.weibo.com/weibo?q=银发经济"}],
    [{"name": "AI大模型多款国产开源", "url": "https://s.weibo.com/weibo?q=AI大模型"}, {"name": "5G-A商用网络加速", "url": "https://s.weibo.com/weibo?q=5G-A"}, {"name": "无人驾驶多城上路测试", "url": "https://s.weibo.com/weibo?q=无人驾驶"}],
]


def get_hot_topics():
    """实时热点：优先微博实时热搜，失败用备选"""
    result = _fetch_weibo_realtime()
    if result and len(result) > 0:
        return result[:6]

    # 兜底 — 按当前小时随机变化
    today = date.today()
    week_num = today.isocalendar()[1]
    hour = datetime.now().hour
    idx = (week_num + today.year * 3 + hour) % len(_FALLBACK_HOT)
    return [_FALLBACK_HOT[idx]]


def _fetch_weibo_realtime():
    """从微博实时热搜接口获取当日热点"""
    try:
        req = urllib.request.Request(
            "https://weibo.com/ajax/side/hotSearch",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://weibo.com/",
                "Accept": "application/json, text/plain, */*",
            }
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            realtime = data.get("data", {}).get("realtime", [])
            if realtime:
                return [
                    {
                        "name": item.get("word", "").strip(),
                        "url": "https://s.weibo.com/weibo?q=" + urllib.parse.quote(item.get("word", ""))
                    }
                    for item in realtime[:10]
                    if item.get("word")
                ]
    except Exception:
        pass
    return []


# ==================== 计划操作 ====================
def add_plan(content: str, plan_date: str = "", plan_type: str = "daily", end_date: str = None):
    conn = get_db()
    if not plan_date:
        plan_date = date.today().isoformat()
    conn.execute(
        "INSERT INTO plans (content, plan_date, plan_type, end_date) VALUES (?,?,?,?)",
        (content, plan_date, plan_type, end_date)
    )
    conn.commit()
    conn.close()


def get_plans(plan_date: str = "", plan_type: str = ""):
    conn = get_db()
    query = "SELECT * FROM plans WHERE 1=1"
    params = []
    if plan_date:
        query += " AND plan_date=?"
        params.append(plan_date)
    if plan_type:
        query += " AND plan_type=?"
        params.append(plan_type)
    query += " ORDER BY done ASC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_plan(plan_id: int):
    conn = get_db()
    row = conn.execute("SELECT done FROM plans WHERE id=?", (plan_id,)).fetchone()
    if row:
        new_done = 1 if row["done"] == 0 else 0
        conn.execute("UPDATE plans SET done=? WHERE id=?", (new_done, plan_id))
        conn.commit()
    conn.close()


def update_plan(plan_id: int, content: str):
    conn = get_db()
    conn.execute("UPDATE plans SET content=? WHERE id=?", (content, plan_id))
    conn.commit()
    conn.close()


def delete_plan(plan_id: int):
    conn = get_db()
    conn.execute("DELETE FROM plans WHERE id=?", (plan_id,))
    conn.commit()
    conn.close()


# ==================== 随笔操作 ====================
def add_essay(content: str):
    conn = get_db()
    conn.execute("INSERT INTO essays (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()


def get_today_essay():
    conn = get_db()
    today_str = date.today().isoformat()
    row = conn.execute(
        "SELECT * FROM essays WHERE date(created_at)=? ORDER BY created_at DESC LIMIT 1",
        (today_str,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_essay(essay_id: int, content: str):
    conn = get_db()
    conn.execute("UPDATE essays SET content=?, created_at=datetime('now','localtime') WHERE id=?", (content, essay_id))
    conn.commit()
    conn.close()


def get_all_essays(limit: int = 50):
    """获取所有随笔，按时间倒序"""
    conn = get_db()
    rows = conn.execute("SELECT * FROM essays ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==================== 记账操作（保留） ====================
def add_bill(bill_type: str, amount: float, category: str, note: str = "", image_path: str = "", bill_date: str = ""):
    conn = get_db()
    if bill_date:
        conn.execute(
            "INSERT INTO bills (type, amount, category, note, image_path, created_at) VALUES (?,?,?,?,?,?)",
            (bill_type, amount, category, note, image_path, bill_date + " 12:00:00")
        )
    else:
        conn.execute(
            "INSERT INTO bills (type, amount, category, note, image_path) VALUES (?,?,?,?,?)",
            (bill_type, amount, category, note, image_path)
        )
    conn.commit()
    conn.close()


def get_bills(month: str = "", date_filter: str = ""):
    conn = get_db()
    if month:
        rows = conn.execute(
            "SELECT * FROM bills WHERE strftime('%Y-%m', created_at)=? ORDER BY created_at DESC",
            (month,)
        ).fetchall()
    elif date_filter:
        rows = conn.execute(
            "SELECT * FROM bills WHERE date(created_at)=? ORDER BY created_at DESC",
            (date_filter,)
        ).fetchall()
    else:
        today_str = date.today().isoformat()
        rows = conn.execute(
            "SELECT * FROM bills WHERE date(created_at)=? ORDER BY created_at DESC",
            (today_str,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_bill(bill_id: int):
    conn = get_db()
    conn.execute("DELETE FROM bills WHERE id=?", (bill_id,))
    conn.commit()
    conn.close()


def update_bill(bill_id: int, bill_type: str, category: str, amount: float, note: str):
    conn = get_db()
    conn.execute("UPDATE bills SET type=?, category=?, amount=?, note=? WHERE id=?", (bill_type, category, amount, note, bill_id))
    conn.commit()
    conn.close()


def get_bills_summary(year: str = "", month: str = ""):
    """总账/年度总账：前端统一数据格式"""
    conn = get_db()
    total_income = 0
    total_expense = 0
    days = []
    monthly = []

    if year and month:
        # 选具体月：按天汇总 + 每天账单明细
        ym = f"{year}-{month}"
        total_income = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='income' AND strftime('%Y-%m', created_at)=?", (ym,)
        ).fetchone()[0]
        total_expense = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='expense' AND strftime('%Y-%m', created_at)=?", (ym,)
        ).fetchone()[0]

        day_rows = conn.execute("""
            SELECT date(created_at) as d, type, SUM(amount) as total FROM bills
            WHERE strftime('%Y-%m', created_at)=? GROUP BY d, type ORDER BY d
        """, (ym,)).fetchall()

        # 按天整理
        day_map = {}
        for r in day_rows:
            k = r["d"]
            if k not in day_map:
                day_map[k] = {"date": k, "expense": 0, "income": 0}
            day_map[k][r["type"]] = round(r["total"], 2)

        # 补全当月所有天
        import calendar
        days_in_month = calendar.monthrange(int(year), int(month))[1]
        for d in range(1, days_in_month + 1):
            ds = f"{year}-{month}-{d:02d}"
            if ds in day_map:
                day = day_map[ds]
            else:
                day = {"date": ds, "expense": 0, "income": 0}
            # 加载当天账单列表
            bill_rows = conn.execute(
                "SELECT * FROM bills WHERE date(created_at)=? ORDER BY created_at DESC", (ds,)
            ).fetchall()
            day["bills"] = [dict(r) for r in bill_rows]
            days.append(day)

    elif year:
        # 选全年：按月汇总
        total_income = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='income' AND strftime('%Y', created_at)=?", (year,)
        ).fetchone()[0]
        total_expense = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='expense' AND strftime('%Y', created_at)=?", (year,)
        ).fetchone()[0]

        mon_rows = conn.execute("""
            SELECT strftime('%m', created_at) as m, type, SUM(amount) as total FROM bills
            WHERE strftime('%Y', created_at)=? GROUP BY m, type ORDER BY m
        """, (year,)).fetchall()

        mon_map = {}
        for r in mon_rows:
            k = r["m"]
            if k not in mon_map:
                mon_map[k] = {"month": k, "expense": 0, "income": 0}
            mon_map[k][r["type"]] = round(r["total"], 2)

        for i in range(1, 13):
            m = f"{i:02d}"
            monthly.append(mon_map.get(m, {"month": m, "expense": 0, "income": 0}))

    conn.close()
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "days": days,
        "monthly": monthly,
    }


def get_year_stats(year: str):
    """年度统计：按月的收支汇总"""
    conn = get_db()
    income = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='income' AND strftime('%Y', created_at)=?",
        (year,)
    ).fetchone()[0]
    expense = conn.execute(
        "SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='expense' AND strftime('%Y', created_at)=?",
        (year,)
    ).fetchone()[0]
    # 按月分解
    rows = conn.execute("""
        SELECT strftime('%m', created_at) as m, type, SUM(amount) as total FROM bills
        WHERE strftime('%Y', created_at)=?
        GROUP BY m, type ORDER BY m
    """, (year,)).fetchall()
    conn.close()

    monthly = {}
    for r in rows:
        m = r["m"]
        if m not in monthly:
            monthly[m] = {"month": m, "expense": 0, "income": 0}
        monthly[m][r["type"]] = round(r["total"], 2)
    # 补全12个月
    result = []
    for i in range(1, 13):
        m = f"{i:02d}"
        if m in monthly:
            result.append(monthly[m])
        else:
            result.append({"month": m, "expense": 0, "income": 0})

    return {
        "income": income, "expense": expense, "balance": income - expense,
        "monthly": result,
        "categories": get_bill_stats(f"{year}-01")["categories"]  # 用一月的分类，实际应该跨年汇总
    }


def get_day_bills(date_str: str):
    """获取某一天的所有账单详情"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM bills WHERE date(created_at)=? ORDER BY created_at DESC",
        (date_str,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==================== 首页汇总 ====================
def get_dashboard_data():
    today_str = date.today().isoformat()
    conn = get_db()

    today_income = conn.execute("SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='income' AND date(created_at)=?", (today_str,)).fetchone()[0]
    today_expense = conn.execute("SELECT COALESCE(SUM(amount),0) FROM bills WHERE type='expense' AND date(created_at)=?", (today_str,)).fetchone()[0]

    today_plans = conn.execute("""
        SELECT * FROM plans WHERE plan_type='daily' 
        AND (plan_date=? OR (end_date IS NOT NULL AND plan_date <= ? AND end_date >= ?))
        ORDER BY done ASC, created_at DESC
    """, (today_str, today_str, today_str)).fetchall()

    longterm_plans = conn.execute("SELECT * FROM plans WHERE plan_type='longterm' ORDER BY done ASC, created_at DESC").fetchall()

    # 本周周计划
    weekly_plans = conn.execute("""
        SELECT * FROM plans WHERE plan_type='weekly' 
        AND plan_date >= date('now','localtime','weekday 0','-6 days')
        AND plan_date <= date('now','localtime','weekday 0','+6 days')
        ORDER BY plan_date ASC, done ASC
    """).fetchall()

    today_essay = conn.execute("SELECT * FROM essays WHERE date(created_at)=? ORDER BY created_at DESC LIMIT 1", (today_str,)).fetchone()

    conn.close()

    # 根据支出情况定制夸奖
    compliment = get_today_compliment()
    if today_expense > 500:
        compliment = "今天开销不小，但能记下来就是好样的！" if today_expense > 500 else compliment

    return {
        "today_str": today_str,
        "today_income": today_income,
        "today_expense": today_expense,
        "today_plans": [dict(r) for r in today_plans],
        "longterm_plans": [dict(r) for r in longterm_plans],
        "weekly_plans": [dict(r) for r in weekly_plans],
        "today_essay": dict(today_essay) if today_essay else None,
        "compliment": compliment,
        "daily_quote": get_today_quote(),
        "hot_topics": get_hot_topics(),
    }
