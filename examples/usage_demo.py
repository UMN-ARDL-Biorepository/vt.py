import json
from dotenv import load_dotenv
from vt.api import VersaTrak


def main():
    # 1. Load credentials from .env file
    # Ensure VT_API_URL, VT_USERNAME, VT_PASSWORD are set
    load_dotenv(override=True)

    # 2. Initialize the VersaTrak client
    # The client will automatically attempt login using environment variables
    # or provided arguments.
    print("Connecting to VersaTrak API...")
    vt = VersaTrak()

    # Check if login was successful
    if not vt.is_logged_on:
        print("Failed to log in. Please check your credentials in .env")
        return

    print(f"Logged in as: {vt.username}")
    print(f"Connected to instance: {vt.instance}")

    try:
        # 3. Get all Monitored Objects
        print("\nFetching Monitored Objects...")
        objects_data = vt.getallmonitoredobjects()
        objects = json.loads(objects_data)

        # Pick a temperature sensor if possible, otherwise fall back to the first object
        moid = None
        for obj_id, obj_data in objects.items():
            if "Temp" in obj_data.get("name", ""):
                moid = obj_id
                break

        if not moid and objects:
            moid = list(objects.keys())[0]

        if not moid:
            print("No monitored objects found.")
            return

        obj = objects[moid]
        print(f"Selected Object: {obj['name']} (ID: {moid})")

        # 4. Get the UOM Converter
        # This helper class handles the scaling and offset formulas
        print("\nInitializing UOM Converter...")
        converter = vt.get_uom_converter()

        # 5. Demonstrate reading conversion
        # Let's get the current status of this object to see its latest reading
        print("\nFetching current status...")
        status_data = vt.currentstatus()
        status_dict = json.loads(status_data)

        # Current status is a dictionary keyed by MOID
        obj_status = status_dict.get(moid)

        if obj_status and "mps" in obj_status and obj_status["mps"]:
            # A monitored object can have multiple measuring points (mps)
            # In currentstatus, mps is a list of dictionaries
            for mp_info in obj_status["mps"]:
                # The raw value is often in 'lastReading' for current status
                raw_val = mp_info.get("lastReading")
                uom_id = mp_info.get("effUomId") or mp_info.get("uomId")
                mp_name = mp_info.get("mpt", {}).get("name", "Unknown")

                if raw_val is not None:
                    # 1. Convert by UOM ID (standard)
                    human_val_id = converter.format(raw_val, uom_id)

                    # 2. Convert by UOM Name (new!)
                    # Get the name from metadata for demonstration
                    uom_meta = converter.uom_map.get(uom_id, {})
                    uom_name = uom_meta.get("name", "Unknown")
                    human_val_name = converter.format(raw_val, uom_name)

                    # 3. Convert by Display Unit (e.g. °C, %)
                    disp_unit = uom_meta.get("dispUom", "")
                    human_val_unit = converter.format(raw_val, disp_unit)

                    print(f"Measuring Point: {mp_name}")
                    print(f"  Raw Value: {raw_val}")
                    print(f"  By UOM ID: {human_val_id}")
                    print(f"  By Name:   {human_val_name}")
                    print(f"  By Unit:   {human_val_unit}")
        else:
            print(f"No current status data found for {obj['name']}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 6. Always log off to close the session cleanly
        print("\nLogging off...")
        vt.logoff()
        print("Done.")


if __name__ == "__main__":
    main()
