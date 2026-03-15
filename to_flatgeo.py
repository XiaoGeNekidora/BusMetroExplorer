import geopandas as gpd

# 1. 读取 SHP 文件
gdf = gpd.read_file("data/bus_stops.shp")

# 2. 核心优化：只保留必要的列（例如：站点名和 ID）
# 冗余的属性字段是导致浏览器内存崩溃的元凶
essential_columns = ['name_cn', 'name_en', 'stop_id', 'city_code', 'geometry']
gdf = gdf[essential_columns]

# 3. 坐标系转换：确保是 EPSG:4326 (WGS84)，这是 Web 地图的标准
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

# 4. 导出为 FlatGeobuf
# 注意：你需要安装 pyogrio 或 fiona
# 推荐安装 pyogrio，速度极快：pip install pyogrio
gdf.to_file("data/bus_stops.fgb", driver="FlatGeobuf")

print("转换完成！请检查 data/bus_stops.fgb 文件。")
