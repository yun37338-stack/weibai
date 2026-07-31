"""
个人工作台 - FastAPI 后端
运行: python app.py
"""
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="个人工作台", version="2.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== 页面 ====================

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


# ==================== 设置 ====================

@app.get("/api/settings")
def get_settings():
    return {
        "user_name": database.get_setting("user_name"),
        "theme_color": database.get_setting("theme_color"),
        "app_icon": database.get_setting("app_icon"),
        "custom_categories": database.get_setting("custom_categories"),
    }


@app.put("/api/settings")
async def update_settings_full(request: Request):
    data = await request.json()
    for key, value in data.items():
        database.update_setting(key, str(value) if value else "")
    return {"ok": True}


@app.get("/api/settings/cat-icons")
def get_cat_icons():
    result = {}
    conn = database.get_db()
    rows = conn.execute("SELECT key, value FROM settings WHERE key LIKE 'cat_icon_%'").fetchall()
    conn.close()
    for row in rows:
        result[row["key"].replace("cat_icon_", "")] = row["value"]
    return result


@app.post("/api/settings/cat-icon/upload")
async def upload_cat_icon(image: UploadFile = File(...), category: str = Form(...)):
    ext = os.path.splitext(image.filename)[1] or ".png"
    filename = f"cat_{category}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await image.read())
    icon_url = f"/static/uploads/{filename}"
    database.update_setting(f"cat_icon_{category}", icon_url)
    return {"ok": True, "url": icon_url}


@app.post("/api/settings/upload-icon")
async def upload_icon(image: UploadFile = File(...)):
    """上传自定义应用图标"""
    ext = os.path.splitext(image.filename)[1] or ".png"
    filename = f"app_icon_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await image.read())
    icon_url = f"/static/uploads/{filename}"
    database.update_setting("app_icon", icon_url)
    return {"ok": True, "url": icon_url}


# ==================== 仪表盘数据 ====================

@app.get("/api/dashboard")
def dashboard_data():
    return database.get_dashboard_data()


# ==================== 每日一句和夸奖 ====================

@app.get("/api/today/quote")
def today_quote():
    quote = database.get_today_quote()
    return {"text": quote[0], "author": quote[1]}


@app.get("/api/today/compliment")
def today_compliment():
    return {"text": database.get_today_compliment()}


@app.get("/api/today/hot")
def today_hot():
    return database.get_hot_topics()


# ==================== 计划 API（完整 CRUD） ====================

@app.post("/api/plans/add")
async def plans_add(request: Request):
    data = await request.json()
    database.add_plan(
        content=data["content"],
        plan_date=data.get("plan_date", ""),
        plan_type=data.get("plan_type", "daily"),
        end_date=data.get("end_date"),
    )
    return {"ok": True}


@app.get("/api/plans")
def plans_list(plan_date: str = "", plan_type: str = ""):
    return database.get_plans(plan_date, plan_type)


@app.put("/api/plans/{plan_id}/toggle")
def plans_toggle(plan_id: int):
    database.toggle_plan(plan_id)
    return {"ok": True}


@app.put("/api/plans/{plan_id}")
async def plans_update(plan_id: int, request: Request):
    data = await request.json()
    database.update_plan(plan_id, data["content"])
    return {"ok": True}


@app.delete("/api/plans/{plan_id}")
def plans_delete(plan_id: int):
    database.delete_plan(plan_id)
    return {"ok": True}


# ==================== 随笔 API ====================

@app.post("/api/essays/add")
async def essays_add(request: Request):
    data = await request.json()
    database.add_essay(data["content"])
    return {"ok": True}


@app.get("/api/essays/today")
def essays_today():
    essay = database.get_today_essay()
    return essay or {"id": None, "content": ""}


@app.get("/api/essays")
def essays_list():
    return database.get_all_essays()


@app.put("/api/essays/{essay_id}")
async def essays_update(essay_id: int, request: Request):
    data = await request.json()
    database.update_essay(essay_id, data["content"])
    return {"ok": True}


# ==================== 分类图标 ====================

@app.post("/api/settings/upload-cat-icon")
async def upload_cat_icon(category: str = Form(...), image: UploadFile = File(...)):
    """为某个分类上传自定义图标"""
    ext = os.path.splitext(image.filename)[1] or ".png"
    filename = f"cat_{category}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await image.read())
    icon_url = f"/static/uploads/{filename}"
    database.update_setting(f"cat_icon_{category}", icon_url)
    return {"ok": True, "url": icon_url, "category": category}


@app.get("/api/settings/cat-icons")
def get_cat_icons():
    cats = ["餐饮", "交通", "购物", "娱乐", "住房", "医疗", "教育", "其他"]
    result = {}
    for c in cats:
        icon = database.get_setting(f"cat_icon_{c}")
        if icon:
            result[c] = icon
    return result


# ==================== 记账 API ====================

@app.post("/api/bills/add")
async def bills_add(request: Request):
    data = await request.json()
    database.add_bill(
        bill_type=data["type"],
        amount=float(data["amount"]),
        category=data.get("category", "其他"),
        note=data.get("note", ""),
    )
    return {"ok": True}


@app.get("/api/bills")
def bills_list(month: str = ""):
    return database.get_bills(month)


@app.delete("/api/bills/{bill_id}")
def bills_delete(bill_id: int):
    database.delete_bill(bill_id)
    return {"ok": True}


@app.put("/api/bills/{bill_id}")
async def bills_update(bill_id: int, request: Request):
    data = await request.json()
    database.update_bill(bill_id, data.get("type"), data.get("category"), float(data.get("amount", 0)), data.get("note"))
    return {"ok": True}


@app.get("/api/bills/stats")
def bills_stats(month: str = ""):
    return database.get_bill_stats(month)


@app.get("/api/bills/year-stats")
def bills_year_stats(year: str = ""):
    return database.get_year_stats(year)


@app.get("/api/bills/day")
def bills_day(date: str = ""):
    return database.get_day_bills(date)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
