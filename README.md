# BusMetroExplorer

> [!WARNING]
> 本项目为vibe coding，代码质量较差，仅供学习参考。

busrouter.sg but for China

类似[busrouter.sg](https://busrouter.sg)的全国公交线路和站点可视化工具。采用数据集为[CPTOND2025](https://figshare.com/articles/dataset/CPTOND-2025/29377427)。

功能：
- 查看全国超过80万个公交站点的位置和途经线路
- 查看公交线路详情、停靠站、运营公司等
- 自定义显示多条线路的路线图
- 查看停靠一个车站的所有路线图

目前局限：
- 只有公交数据
- 数据质量来自CPTOND2025，可能存在错误和不完整
- 英文翻译来自源数据集，看个乐就行

![img.png](demo.png)

# Usage

## 1. 环境准备 / Prerequisites
确保已安装 Python 3.10 或更高版本。

## 2. 安装依赖 / Installation
克隆仓库并进入目录后，运行：
```bash
pip install -r requirements.txt
```

## 3. 数据准备 / Data Setup
1. 下载 [CPTOND2025](https://figshare.com/articles/dataset/CPTOND-2025/29377427) 数据集。
2. 解压并找到 `dataset/bus/shapefiles/` 目录。
3. 将该目录下的所有文件（`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg` 等）复制到本项目的 `data/` 目录下。
   确保 `data/` 目录下有 `bus_routes.shp` 和 `bus_stops.shp` 等文件。

## 4. 数据处理 / Data Processing
依次运行以下脚本以生成数据库和可视化文件：

```bash
# 生成 SQLite 数据库 (Convert SHP to SQLite)
python shp_to_sqlite.py

# 优化数据库索引 (Create indexes)
python optimize_db.py

# 生成前端所需的 FlatGeobuf 文件 (Generate FlatGeobuf for frontend)
python to_flatgeo.py
```

## 5. 运行项目 / Running

### 启动服务 (Integrated Server)
现在后端已整合静态文件服务，只需启动一个进程：

```bash
uvicorn backend:app --host 0.0.0.0 --port 8000
# 或者如果使用 Python 直接运行
python backend.py
```

启动后，直接访问 `http://localhost:8000` 即可查看地图并使用搜索功能。
后端 API 位于同源地址，例如 `/route`。

