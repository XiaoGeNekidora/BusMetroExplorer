import sqlite3
import time

DB_PATH = "data/bus_routes.db"

def optimize_database():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Define indexes to create
    indexes = [
        ("idx_stops_stop_id", "bus_stops", "stop_id"),
        ("idx_stops_route_cn", "bus_stops", "route_cn"),
        ("idx_routes_route_cn", "bus_routes", "route_cn")
    ]

    print("Creating indexes to speed up queries...")
    start_time = time.time()
    
    for idx_name, table, column in indexes:
        try:
            print(f"Creating index {idx_name} on {table}({column})...")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column})")
        except Exception as e:
            print(f"Failed to create index {idx_name}: {e}")

    # Commit changes
    conn.commit()
    
    # Analyze to update statistics for query planner
    print("Analyzing database for query optimization...")
    cursor.execute("ANALYZE")
    
    end_time = time.time()
    conn.close()
    
    print(f"Optimization complete in {end_time - start_time:.2f} seconds!")
    print("The query performance should now trigger index scan instead of full table scan.")

if __name__ == "__main__":
    optimize_database()

