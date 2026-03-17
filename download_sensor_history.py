import asyncio
import json
import argparse
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from vt.api import VersaTrak

async def download_history(sensor_id, period="7d", output_file=None):
    load_dotenv(override=True)
    
    # Initialize client
    vt = VersaTrak()
    if not vt.is_logged_on:
        print(f"Logging in as {vt.username}...")
        await vt.alogin()
    
    if not vt.is_logged_on:
        print("Failed to log in. Check credentials in .env")
        return

    print(f"Fetching history for sensor {sensor_id} (period: {period})...")
    try:
        # Fetch raw history data
        history_raw = await vt.agethistorydata(sensor_id, period=period)
        history_json = json.loads(history_raw)
        
        # Parse history data
        # Structure: {"moid": "...", "name": "...", "mps": [{"mpid": "...", "name": "...", "data": [[ts, val], ...], ...}]}
        
        all_data = []
        sensor_name = history_json.get("name", "Unknown")
        
        for mp_entry in history_json.get("mps", []):
            mp_id = mp_entry.get("mpid")
            mp_name = mp_entry.get("name")
            data_points = mp_entry.get("data", [])
            
            print(f"  Found {len(data_points)} data points for Measuring Point: {mp_name} ({mp_id})")
            
            for point in data_points:
                ts = point.get('d')
                val = point.get('v')
                if ts is not None and val is not None:
                    all_data.append({
                        "sensor_id": sensor_id,
                        "sensor_name": sensor_name,
                        "mp_id": mp_id,
                        "mp_name": mp_name,
                        "timestamp": pd.to_datetime(ts, unit='ms'),
                        "value": val
                    })
        
        if not all_data:
            print("No data points found for this sensor in the specified period.")
            return

        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Sort by timestamp
        df = df.sort_values("timestamp")
        
        # Determine output filename if not provided
        if not output_file:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in sensor_name])
            output_file = f"history_{safe_name}_{timestamp_str}.parquet"
        
        # Save to Parquet
        print(f"Saving {len(df)} records to {output_file}...")
        df.to_parquet(output_file, engine='pyarrow', index=False)
        print("Download complete.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if vt.is_logged_on:
            await vt.alogoff()

def main():
    parser = argparse.ArgumentParser(description="Download VersaTrak sensor historical data to Parquet.")
    parser.add_argument("sensor_id", help="The UUID of the sensor (Monitored Object)")
    parser.add_argument("--period", default="7d", help="Period to fetch (e.g., 24h, 7d, 30d). Default: 7d")
    parser.add_argument("--output", help="Output Parquet file path")
    
    args = parser.parse_args()
    
    asyncio.run(download_history(args.sensor_id, args.period, args.output))

if __name__ == "__main__":
    main()
