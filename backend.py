from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn
from typing import List, Dict, Any

app = FastAPI(title="BusRoute API")

# Add CORS middleware to allow requests from any origin (e.g. index.html)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_route_info(name: str = Query(..., alias="route_cn", description="Route name in Chinese (e.g. '8路(柯柯牙--电影小镇站)')")):
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

if __name__ == "__main__":
    # Run user with: python backend.py
    # Access API docs at: http://127.0.0.1:8000/docs
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)

