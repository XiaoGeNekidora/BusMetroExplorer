import pandas as pd
import geopandas as gpd
import sqlite3
import os

# 设置 pandas 显示选项以匹配用户输出格式
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_colwidth', 50)

def process_shp_to_sqlite(shp_path, db_path, table_name, columns=None):
    # 1. 读取 SHP 文件
    print(f"\nProcessing {shp_path} -> Table: {table_name}")
    try:
        gdf = gpd.read_file(shp_path)
    except Exception as e:
        print(f"Error reading shapefile: {e}")
        return

    # 如果指定了列，进行筛选
    if columns:
        # 检查列是否存在
        missing_cols = [c for c in columns if c not in gdf.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols} in {shp_path}")
        
        # 只保留存在的列
        valid_cols = [c for c in columns if c in gdf.columns]
        gdf = gdf[valid_cols]

    # 只有当仍然是 GeoDataFrame (包含 geometry) 时才检查坐标系
    if isinstance(gdf, gpd.GeoDataFrame):
        # 确保坐标系为 EPSG:4326 (WGS84)
        if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
            print(f"Converting CRS from {gdf.crs.to_string()} to EPSG:4326...")
            gdf = gdf.to_crs("EPSG:4326")
        elif gdf.crs is None:
            print("Warning: Source CRS is missing. Assuming columns are already correct or handling as is.")

    # 2. 转换 geometry 列为 WKT 字符串
    df = pd.DataFrame(gdf)
    if 'geometry' in df.columns:
        df['geometry'] = df['geometry'].apply(lambda x: x.wkt if hasattr(x, 'wkt') else str(x) if x else None)
    
    # 3. 将 DataFrame 存储到 SQLite
    print(f"Saving to {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        print("Successfully saved to SQLite.")
    except Exception as e:
        print(f"Error saving to SQLite: {e}")
        return

    # 4. 验证
    print(f"Verifying table '{table_name}':")
    try:
        conn = sqlite3.connect(db_path)
        dfr = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        print(f">>> {table_name}")
        print(dfr.head(5)) # 只打印前 5 行避免输出过多
    except Exception as e:
        print(f"Error verification: {e}")

def main():
    db_path = "data/bus_routes.db"
    
    # Process bus_routes (完整保留，包含 geometry)
    # process_shp_to_sqlite("data/bus_routes.shp", db_path, "bus_routes")
    
    # Process bus_stops (只保留特定字段，丢弃 geometry)
    stop_cols = ['stop_id', 'route_cn', 'route_en', 'route_id']
    process_shp_to_sqlite("data/bus_stops.shp", db_path, "bus_stops", columns=stop_cols)

if __name__ == "__main__":
    main()

