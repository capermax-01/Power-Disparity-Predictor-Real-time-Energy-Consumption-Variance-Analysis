"""
Query and analyze the consolidated appliances database
"""

import sqlite3
import pandas as pd
from pathlib import Path
from config import DB_PATH, SAMPLE_CSV_PATH

class ApplianceDataQuery:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
    
    def summary_stats(self):
        """Display summary statistics"""
        print("\n" + "="*80)
        print("CONSOLIDATED APPLIANCES DATABASE - SUMMARY")
        print("="*80)
        
        # Total records and appliances
        query = "SELECT COUNT(*) as total_records, COUNT(DISTINCT appliance_id) as unique_appliances FROM appliance_readings"
        stats = pd.read_sql_query(query, self.conn)
        print(f"\nTotal Records: {stats.iloc[0]['total_records']:,}")
        print(f"Unique Appliances: {stats.iloc[0]['unique_appliances']}")
        
        # Breakdown by category
        print("\n" + "-"*80)
        print("BREAKDOWN BY APPLIANCE CATEGORY:")
        print("-"*80)
        query = """
            SELECT appliance_category, COUNT(DISTINCT appliance_id) as count,
                   SUM(row_count) as total_readings,
                   ROUND(AVG(power_max), 2) as avg_power_max_w
            FROM appliance_metadata
            WHERE appliance_category IS NOT NULL AND appliance_category != ''
            GROUP BY appliance_category
            ORDER BY count DESC
        """
        categories = pd.read_sql_query(query, self.conn)
        print(categories.to_string(index=False))
        
        # Top appliances by data volume
        print("\n" + "-"*80)
        print("TOP 15 APPLIANCES BY DATA VOLUME:")
        print("-"*80)
        query = """
            SELECT appliance_name, appliance_category, row_count,
                   ROUND(power_max, 2) as power_max_w
            FROM appliance_metadata
            ORDER BY row_count DESC
            LIMIT 15
        """
        top_appliances = pd.read_sql_query(query, self.conn)
        print(top_appliances.to_string(index=False))
        
        # Timestamp range
        print("\n" + "-"*80)
        print("DATA TIME RANGE:")
        print("-"*80)
        query = "SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest FROM appliance_readings"
        timerange = pd.read_sql_query(query, self.conn)
        print(f"Earliest: {timerange.iloc[0]['earliest']}")
        print(f"Latest: {timerange.iloc[0]['latest']}")
    
    def get_appliance_data(self, appliance_name, limit=1000):
        """Get data for a specific appliance"""
        query = f"""
            SELECT timestamp, power_reading, appliance_name, appliance_category
            FROM appliance_readings
            WHERE appliance_name LIKE '%{appliance_name}%'
            LIMIT {limit}
        """
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def export_sample(self, output_path, sample_size=100000):
        """Export a sample of consolidated data to CSV"""
        print(f"\nExporting {sample_size:,} sample records to CSV...")
        query = f"""
            SELECT appliance_id, appliance_name, appliance_category, 
                   timestamp, power_reading, power_max
            FROM appliance_readings
            LIMIT {sample_size}
        """
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(output_path, index=False)
        print(f"✓ Sample exported to: {output_path}")
        return output_path
    
    def get_database_info(self):
        """Get database file size and info"""
        size_bytes = Path(self.db_path).stat().st_size
        size_gb = size_bytes / (1024**3)
        print(f"\nDatabase File: {self.db_path}")
        print(f"Size: {size_gb:.2f} GB")
        
        # Table info
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = pd.read_sql_query(query, self.conn)
        print(f"Tables: {', '.join(tables['name'].tolist())}")
    
    def close(self):
        self.conn.close()


def main():
    db_path = DB_PATH
    
    if not db_path.exists():
        print(f"⚠ Database not found at {db_path}")
        return

    query_engine = ApplianceDataQuery(db_path)
    
    # Display summary
    query_engine.summary_stats()
    
    # Get database info
    query_engine.get_database_info()
    
    # Export sample data
    sample_output = SAMPLE_CSV_PATH
    query_engine.export_sample(str(sample_output), sample_size=100000)
    
    print("\n" + "="*80)
    print("✓ DATABASE CONSOLIDATION AND ANALYSIS COMPLETE")
    print("="*80)
    print("\nYou can now:")
    print("  1. Use the SQLite database: appliances_consolidated.db")
    print("  2. Query using SQL directly")
    print("  3. Use the sample CSV: appliances_sample_100k.csv")
    print("  4. Load the entire database into pandas for analysis")
    
    query_engine.close()


if __name__ == "__main__":
    main()
