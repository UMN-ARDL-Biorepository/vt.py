import os
import asyncio
from dotenv import load_dotenv
from vt.api import VersaTrak

async def main():
    # Load environment variables from .env
    load_dotenv(override=True)
    
    # Initialize the client.
    # It will use VT_API_URL, VT_USERNAME, VT_PASSWORD from environment if not provided.
    vt = VersaTrak()
    
    # If VT_USERNAME and VT_PASSWORD were provided, it auto-logs in during init.
    # If not, you can call alogin() manually.
    if not vt.is_logged_on:
        print("Logging in...")
        await vt.alogin()
    
    if vt.is_logged_on:
        print("Successfully logged in!")
        
        # Get all monitored objects
        print("\nFetching monitored objects...")
        objects_raw = await vt.agetallmonitoredobjects()
        print(f"Received {len(objects_raw)} bytes of data.")
        
        # Get current status
        print("\nFetching current status...")
        status_raw = await vt.acurrentstatus()
        print(f"Received {len(status_raw)} bytes of data.")
        
        # Log off when done
        print("\nLogging off...")
        await vt.alogoff()
        print("Done.")
    else:
        print("Failed to log in. Check your credentials in .env")

if __name__ == "__main__":
    asyncio.run(main())
