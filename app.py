"""
个人工作台 - FastAPI 后端
运行: python app.py
"""
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import database


def get_device_id(x_device_id: Optional[str] = Header(None)) -> str:
    """从请求头提取设备ID，用于数据隔离"""
    return x_device_id or "legacy"


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


@app.get("/sw.js")
def service_worker():
    from fastapi.responses import Response
    with open("static/sw.js", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="application/javascript")


@app.get("/favicon.ico")
def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("static/favicon.png")


# ==================== 设置（设备隔离） ====================

@app.get("/api/settings")
def get_settings(device_id: str = Header(None, alias="X-Device-Id")):
    did = device_id or "legacy"
    return {
        "user_name": database.get_setting("user_name", did),
        "theme_color": database.get_setting("theme_color", did),
        "app_icon": database.get_setting("app_icon", did),
        "custom_categories": database.get_setting("custom_categories", did),
        "device_name": database.get_setting("device_name", did),
    }


@app.put("/api/settings")
async def update_settings_full(request: Request):
    device_id = request.headers.get("X-Device-Id", "legacy")
    data = await request.json()
    for key, value in data.items():
        database.update_setting(key, str(value) if value else "", device_id)
    return {"ok": True}


@app.get("/api/settings/cat-icons")
def get_cat_icons(device_id: str = Header(None, alias="X-Device-Id")):
    """分类图标也按设备隔离"""
    did = device_id or "legacy"
    result = {}
    conn = database.get_db()
    rows = conn.execute(
        "SELECT key, value FROM device_settings WHERE key LIKE 'cat_icon_%' AND device_id=?",
        (did,)
    ).fetchall()
    # fallback to legacy
    if not rows:
        rows = conn.execute(
            "SELECT key, value FROM device_settings WHERE key LIKE 'cat_icon_%' AND device_id='legacy'"
        ).fetchall()
    conn.close()
    for row in rows:
        result[row["key"].replace("cat_icon_", "")] = row["value"]
    return result


@app.post("/api/settings/cat-icon/upload")
async def upload_cat_icon(request: Request, image: UploadFile = File(...), category: str = Form(...)):
    device_id = request.headers.get("X-Device-Id", "legacy")
    ext = os.path.splitext(image.filename)[1] or ".png"
    filename = f"cat_{category}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await image.read())
    icon_url = f"/static/uploads/{filename}"
    database.update_setting(f"cat_icon_{category}", icon_url, device_id)
    return {"ok": True, "url": icon_url}


@app.post("/api/settings/upload-icon")
@app.post("/api/upload-icon")
async def upload_icon(request: Request, image: UploadFile = File(...)):
    """上传自定义应用图标（设备隔离）"""
    device_id = request.headers.get("X-Device-Id", "legacy")
    ext = os.path.splitext(image.filename)[1] or ".png"
    filename = f"app_icon_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await image.read())
    icon_url = f"/static/uploads/{filename}"
    database.update_setting("app_icon", icon_url, device_id)
    return {"ok": True, "url": icon_url}


# ==================== 仪表盘数据 ====================

@app.get("/api/dashboard")
def dashboard_data(device_id: str = Header(None, alias="X-Device-Id")):
    return database.get_dashboard_data(device_id or "legacy")


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
    device_id = request.headers.get("X-Device-Id", "legacy")
    data = await request.json()
    database.add_plan(
        content=data["content"],
        device_id=device_id,
        plan_date=data.get("plan_date", ""),
        plan_type=data.get("plan_type", "daily"),
        end_date=data.get("end_date"),
    )
    return {"ok": True}


@app.get("/api/plans")
def plans_list(plan_date: str = "", plan_type: str = "", device_id: str = Header(None, alias="X-Device-Id")):
    return database.get_plans(device_id or "legacy", plan_date, plan_type)


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
    device_id = request.headers.get("X-Device-Id", "legacy")
    data = await request.json()
    database.add_essay(data["content"], device_id)
    return {"ok": True}


@app.get("/api/essays/today")
def essays_today(device_id: str = Header(None, alias="X-Device-Id")):
    essay = database.get_today_essay(device_id or "legacy")
    return essay or {"id": None, "content": ""}


@app.get("/api/essays")
def essays_list(device_id: str = Header(None, alias="X-Device-Id")):
    return database.get_all_essays(device_id or "legacy")


@app.put("/api/essays/{essay_id}")
async def essays_update(essay_id: int, request: Request):
    data = await request.json()
    database.update_essay(essay_id, data["content"])
    return {"ok": True}


# ==================== 记账 API ====================

@app.post("/api/bills/add")
async def bills_add(request: Request):
    device_id = request.headers.get("X-Device-Id", "legacy")
    data = await request.json()
    database.add_bill(
        bill_type=data["type"],
        amount=float(data["amount"]),
        category=data.get("category", "其他"),
        device_id=device_id,
        note=data.get("note", ""),
        bill_date=data.get("bill_date", ""),
    )
    return {"ok": True}


@app.get("/api/bills")
def bills_list(month: str = "", date: str = "", device_id: str = Header(None, alias="X-Device-Id")):
    return database.get_bills(device_id or "legacy", month=month, date_filter=date)


@app.delete("/api/bills/{bill_id}")
def bills_delete(bill_id: int):
    database.delete_bill(bill_id)
    return {"ok": True}


@app.put("/api/bills/{bill_id}")
async def bills_update(bill_id: int, request: Request):
    data = await request.json()
    database.update_bill(bill_id, data.get("type"), data.get("category"), float(data.get("amount", 0)), data.get("note"))
    return {"ok": True}


@app.get("/api/bills/summary")
def bills_summary(year: str = "", month: str = "", device_id: str = Header(None, alias="X-Device-Id")):
    return database.get_bills_summary(device_id or "legacy", year, month)


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
