"""
Consolidate multiple appliance CSV files into a unified database
Combines all individual appliance usage data into a single SQLite database
"""

import os
import pandas as pd
import sqlite3
from pathlib import Path
import warnings
from config import DB_PATH, CSV_PATH, ARCHIVE_DIR

warnings.filterwarnings('ignore')

class ApplianceDataConsolidator:
    def __init__(self, archive_dir=ARCHIVE_DIR, db_path=DB_PATH, csv_path=CSV_PATH):
        self.archive_dir = Path(archive_dir)
        self.db_path = Path(db_path)
        self.csv_path = Path(csv_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
    def get_appliance_files(self):
        """Get all appliance CSV files from archive (excluding the metadata file)"""
        csv_files = []
        for file in sorted(self.archive_dir.glob("*.csv")):
            if file.name != "0_smart_plugs_devices.csv":
                csv_files.append(file)
        
        return csv_files
    
    def load_appliance_metadata(self):
        """Load the metadata file containing appliance info"""
        metadata_path = self.archive_dir / "0_smart_plugs_devices.csv"
        try:
            metadata = pd.read_csv(metadata_path)
            print(f"✓ Loaded metadata: {len(metadata)} appliances")
            return metadata
        except Exception as e:
            print(f"⚠ Could not load metadata: {e}")
            return None
    
    def get_appliance_info_from_metadata(self, filename, metadata):
        """Extract appliance info from metadata"""
        if metadata is None:
            return {}
        
        # Find the row matching this filename
        matching_rows = metadata[metadata['files_names'] == filename]
        if len(matching_rows) > 0:
            row = matching_rows.iloc[0]
            return {
                'appliance_id': row.get('id', ''),
                'appliance_name': row.get('plug_name', ''),
                'appliance_category': row.get('appliance_category', ''),
                'power_max': row.get('power_max', '')
            }
        
        return {}
    
    def consolidate_to_sqlite(self):
        """Consolidate all CSV files into SQLite database"""
        print("\n" + "="*70)
        print("CONSOLIDATING APPLIANCE DATA TO SQLITE DATABASE")
        print("="*70)
        
        # Load metadata
        metadata = self.load_appliance_metadata()
        
        # Get all appliance CSV files
        csv_files = self.get_appliance_files()
        print(f"Found {len(csv_files)} appliance files to consolidate\n")
        
        # Connect to SQLite database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create main table for consolidated data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appliance_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance_id TEXT,
                appliance_name TEXT,
                appliance_category TEXT,
                power_max REAL,
                timestamp DATETIME,
                power_reading REAL
            )
        ''')
        
        # Create table for appliance metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appliance_metadata (
                appliance_id TEXT PRIMARY KEY,
                appliance_name TEXT,
                appliance_category TEXT,
                power_max REAL,
                file_name TEXT,
                row_count INTEGER
            )
        ''')
        
        total_rows = 0
        successful_files = 0
        failed_files = 0
        
        # Process each appliance file
        for idx, csv_file in enumerate(csv_files, 1):
            try:
                print(f"[{idx}/{len(csv_files)}] Processing {csv_file.name}...", end=" ")
                
                # Load CSV
                df = pd.read_csv(csv_file)
                
                # Get appliance info from metadata
                app_info = self.get_appliance_info_from_metadata(csv_file.name, metadata)
                
                # Add appliance info columns
                df['appliance_id'] = app_info.get('appliance_id', csv_file.stem)
                df['appliance_name'] = app_info.get('appliance_name', csv_file.stem.replace('_', ' ').title())
                df['appliance_category'] = app_info.get('appliance_category', 'unknown')
                df['power_max'] = app_info.get('power_max', '')
                
                # Standardize column names (assuming power consumption column)
                # Common column names: 'power', 'Power', 'consumption', 'Consumption', etc.
                power_col = None
                timestamp_col = None
                
                for col in df.columns:
                    col_lower = col.lower()
                    if col_lower in ['power', 'consumption', 'watts', 'w']:
                        power_col = col
                    if col_lower in ['timestamp', 'time', 'datetime', 'ts', 'date_time']:
                        timestamp_col = col
                
                # If columns not found, use first two columns (assume first is timestamp, second is power)
                if not power_col or not timestamp_col:
                    if len(df.columns) >= 3:  # At least timestamp and power
                        timestamp_col = df.columns[0]
                        power_col = df.columns[1]
                
                if power_col and timestamp_col:
                    # Rename to standard names
                    df.rename(columns={
                        timestamp_col: 'timestamp',
                        power_col: 'power_reading'
                    }, inplace=True)
                    
                    # Select relevant columns
                    select_cols = ['appliance_id', 'appliance_name', 'appliance_category', 
                                  'power_max', 'timestamp', 'power_reading']
                    
                    available_cols = [col for col in select_cols if col in df.columns]
                    df = df[available_cols]
                    
                    # Insert into database
                    df.to_sql('appliance_readings', conn, if_exists='append', index=False)
                    
                    # Update metadata table
                    cursor.execute('''
                        INSERT OR REPLACE INTO appliance_metadata 
                        (appliance_id, appliance_name, appliance_category, power_max, file_name, row_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        app_info.get('appliance_id', csv_file.stem),
                        app_info.get('appliance_name', csv_file.name),
                        app_info.get('appliance_category', 'unknown'),
                        app_info.get('power_max', ''),
                        csv_file.name,
                        len(df)
                    ))
                    
                    total_rows += len(df)
                    successful_files += 1
                    print(f"✓ {len(df):,} rows")
                else:
                    print("⚠ Could not identify timestamp/power columns")
                    failed_files += 1
                    
            except Exception as e:
                print(f"✗ Error: {str(e)[:50]}")
                failed_files += 1
        
        # Commit changes
        conn.commit()
        
        # Create indexes asynchronously (optional for performance)
        print("\nCreating database indexes for better query performance...")
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_appliance_id ON appliance_readings(appliance_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON appliance_readings(timestamp)')
            conn.commit()
        except Exception as e:
            print(f"Note: Indexing skipped or delayed: {e}")
        
        conn.close()
        
        print("\n" + "="*70)
        print("CONSOLIDATION COMPLETE")
        print("="*70)
        print(f"Database: {self.db_path}")
        print(f"Total records: {total_rows:,}")
        print(f"Successful files: {successful_files}/{len(csv_files)}")
        print(f"Failed files: {failed_files}/{len(csv_files)}")
        
        return self.db_path
    
    def export_to_csv(self):
        """Export consolidated data from SQLite to CSV"""
        print("\n" + "="*70)
        print("EXPORTING TO CSV")
        print("="*70)
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            df = pd.read_sql_query("SELECT * FROM appliance_readings", conn)
            conn.close()
            
            df.to_csv(str(self.csv_path), index=False)
            print(f"✓ CSV exported: {self.csv_path}")
            print(f"  Shape: {df.shape}")
            return self.csv_path
        except Exception as e:
            print(f"✗ Error exporting CSV: {e}")
            return None
    
    def generate_summary(self):
        """Generate summary statistics"""
        print("\n" + "="*70)
        print("CONSOLIDATED DATABASE SUMMARY")
        print("="*70)
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            # Appliance summary
            print("\nAppliances by Category:")
            query = """
                SELECT appliance_category, COUNT(DISTINCT appliance_id) as count,
                       SUM(row_count) as total_readings
                FROM appliance_metadata
                GROUP BY appliance_category
                ORDER BY count DESC
            """
            summary = pd.read_sql_query(query, conn)
            print(summary.to_string(index=False))
            
            # Top appliances by data volume
            print("\n\nTop 10 Appliances by Record Count:")
            query = """
                SELECT appliance_name, appliance_category, row_count
                FROM appliance_metadata
                ORDER BY row_count DESC
                LIMIT 10
            """
            top = pd.read_sql_query(query, conn)
            print(top.to_string(index=False))
            
            # Overall statistics
            print("\n\nOverall Statistics:")
            query = "SELECT COUNT(*) as total_records, COUNT(DISTINCT appliance_id) as unique_appliances FROM appliance_readings"
            stats = pd.read_sql_query(query, conn)
            print(f"Total Records: {stats.iloc[0]['total_records']:,}")
            print(f"Unique Appliances: {stats.iloc[0]['unique_appliances']}")
            
            conn.close()
        except Exception as e:
            print(f"Error generating summary: {e}")
    
    def run(self):
        """Run full consolidation pipeline"""
        db_path = self.consolidate_to_sqlite()
        self.export_to_csv()
        self.generate_summary()
        
        print("\n" + "="*70)
        print("✓ CONSOLIDATION PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\nOutput Files:")
        print(f"  Database: {self.db_path}")
        print(f"  CSV: {self.csv_path}")
        
        return db_path, self.csv_path


def main():
    consolidator = ApplianceDataConsolidator()
    db_path, csv_path = consolidator.run()


if __name__ == "__main__":
    main()
