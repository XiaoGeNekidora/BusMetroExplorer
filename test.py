import pandas as pd
import geopandas as gpd

pd.set_option('display.max_columns', None)  # 显示所有列，不限制列数
pd.set_option('display.expand_frame_repr', False)  # 禁止换行显示（在一行内拉长）
pd.set_option('display.max_colwidth', 50)  # 如果单元格内字符串太长，可以调大这个值

# 只需要读取 .shp 文件，它会自动关联同文件夹下的 .dbf, .prj 等
file_path = "data/bus_stops.shp"
df = gpd.read_file(file_path)

print(df.columns.tolist())
# 查看前 5 行数据（包含线路名、长度等属性和几何图形）
print(df.head())

line_1 = df[df['name_cn'] == '悦澜湾']

print(line_1)
