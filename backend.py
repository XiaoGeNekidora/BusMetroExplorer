from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn
from typing import List, Dict, Any
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="BusRoute API")

# Add CORS middleware to allow requests from any origin (e.g. index.html)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the 'data' directory to serve static files (like .fgb)
app.mount("/data", StaticFiles(directory="data"), name="data")

DB_PATH = "data/bus_routes.db"


def get_db_connection():
    """Create a database connection with dict-like row factory."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/route", response_model=List[Dict[str, Any]])
def get_route_info(
        name: str = Query(..., alias="route_cn", description="Route name in Chinese (e.g. '8路(柯柯牙--电影小镇站)')")):
    """
    根据 route_cn 返回 route 的全部信息。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Exact match query
    cursor.execute("SELECT * FROM bus_routes WHERE route_cn = ?", (name,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        # Optional: Try partial match if exact match fails?
        # For now, return strict 404 as requested or empty list
        # Returning empty list is often better for APIs than 404 for search
        return []

    return [dict(row) for row in rows]


@app.get("/stop", response_model=List[Dict[str, Any]])
def get_routes_by_stop(id: str = Query(..., alias="stop_id", description="Stop ID (e.g. 'BV09219967')")):
    """
    根据 stop_id 返回 route_cn, route_en 信息。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Select distinct routes for this stop
    cursor.execute("SELECT DISTINCT route_cn, route_en FROM bus_stops WHERE stop_id = ?", (id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    return [dict(row) for row in rows]


@app.get("/stop_details", response_model=List[Dict[str, Any]])
def get_stop_routes_details(id: str = Query(..., alias="stop_id", description="Stop ID (e.g. 'BV09219967')")):
    """
    根据 stop_id 返回所有经过该站点的线路的完整信息（包含 geometry）。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 联表查询：找出该站点对应的所有 route_cn，然后在 bus_routes 中查找这些线路的完整信息
    query = """
            SELECT DISTINCT r.*
            FROM bus_routes r
                     JOIN bus_stops s ON r.route_cn = s.route_cn
            WHERE s.stop_id = ? \
            """
    cursor.execute(query, (id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    return [dict(row) for row in rows]


@app.get("/route_stops", response_model=List[Dict[str, Any]])
def get_route_stops(route_cn: str = Query(..., description="Route name in Chinese")):
    """
    根据 route_cn 返回该线路的所有停靠站点信息 (name_cn, name_en, stop_id)，按顺序排列。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 使用 rowid 进行排序以保持自然序（即 SHP 文件中的顺序）
    # 如果有 sequence 字段，应该优先使用 sequence
    query = """
            SELECT name_cn, name_en, stop_id
            FROM bus_stops
            WHERE route_cn = ?
            ORDER BY rowid \
            """
    cursor.execute(query, (route_cn,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    return [dict(row) for row in rows]


@app.get("/")
async def read_index():
    return FileResponse('index.html')


if __name__ == "__main__":
    # Run user with: python backend.py
    # Access API docs at: http://127.0.0.1:8000/docs
    uvicorn.run(app, host="0.0.0.0", port=8000)
