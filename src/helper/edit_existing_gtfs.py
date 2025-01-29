import pandas as pd
import os
import shutil
from pathlib import Path
from helper.find_project_root import find_project_root


def remove_line(gtfs_folder: str, output_folder: str, route_short_name: str):
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Load GTFS files
    routes = pd.read_csv(f"{gtfs_folder}/routes.txt")
    trips = pd.read_csv(f"{gtfs_folder}/trips.txt")
    stop_times = pd.read_csv(f"{gtfs_folder}/stop_times.txt")
    stops = pd.read_csv(f"{gtfs_folder}/stops.txt")
    shapes = pd.read_csv(f"{gtfs_folder}/shapes.txt")

    # Step 1: Normalize types for filtering
    # Ensure route_short_name matches the type in the routes file
    if routes["route_short_name"].dtype in [int, float]:
        try:
            route_short_name = int(route_short_name)
        except ValueError:
            print(
                f"Invalid route_short_name type. Expected integer but got: {route_short_name}"
            )
            return
    else:
        route_short_name = str(route_short_name)

    # Step 2: Find the route_id and route_long_name for the route_short_name
    route_info = routes.loc[routes["route_short_name"] == route_short_name]
    if route_info.empty:
        print(
            f"Route with short name '{route_short_name}' not found in routes.txt. Exiting."
        )
        return

    route_id = route_info["route_id"].values[0]
    route_long_name = route_info["route_long_name"].values[0]
    print(f"Removing route: {route_short_name} - {route_long_name}")

    # Step 3: Remove the route from routes.txt
    routes = routes[routes["route_id"] != route_id]

    # Step 4: Remove trips associated with this route_id from trips.txt
    line_trips = trips[trips["route_id"] == route_id]
    trips = trips[trips["route_id"] != route_id]

    # Step 5: Remove stop_times associated with these trips
    trip_ids = set(line_trips["trip_id"])
    line_stops = stop_times[stop_times["trip_id"].isin(trip_ids)]
    stop_times = stop_times[~stop_times["trip_id"].isin(trip_ids)]

    # Step 6: Track and remove stops in stops.txt
    stop_ids = set(line_stops["stop_id"])
    stops = stops[~stops["stop_id"].isin(stop_ids)]

    # Step 7: Remove shapes in shapes.txt if applicable
    shape_ids = set(line_trips["shape_id"])
    shapes = shapes[~shapes["shape_id"].isin(shape_ids)]

    # Step 8: Save the cleaned files
    routes.to_csv(f"{output_folder}/routes.txt", index=False)
    trips.to_csv(f"{output_folder}/trips.txt", index=False)
    stop_times.to_csv(f"{output_folder}/stop_times.txt", index=False)
    stops.to_csv(f"{output_folder}/stops.txt", index=False)
    shapes.to_csv(f"{output_folder}/shapes.txt", index=False)

    # Step 9: Copy over the remaining files
    gtfs_files_to_keep = [
        "agency.txt",
        "calendar.txt",
        "calendar_dates.txt",
    ]
    for file in gtfs_files_to_keep:
        src_file = os.path.join(gtfs_folder, file)
        dst_file = os.path.join(output_folder, file)
        if os.path.exists(src_file):
            shutil.copy(src_file, dst_file)

    print(
        f"Successfully removed route '{route_short_name}' - '{route_long_name}' from GTFS data."
    )

def zip_output_folder(output_folder: str, zip_name: str):
    """
    Compress the output folder into a ZIP file.
    """
    output_folder = Path(output_folder)
    zip_name = Path(zip_name)

    if not output_folder.is_dir():
        raise ValueError(f"The specified folder path does not exist or is not a directory: {output_folder}")

    # Create the ZIP archive
    shutil.make_archive(zip_name, 'zip', output_folder)
    print(f"Folder '{output_folder}' has been zipped to '{zip_name}.zip'")




if __name__ == "__main__":
    PROJECT_ROOT = find_project_root("Transit_Dashboard")
    SOURCE_DIR = os.path.join(PROJECT_ROOT, "data/GTFS_data/extracted/2024-10-22")
    ROUTE_SHORT_NAME = "4"
    OUTPUT_DIR = os.path.join(
        PROJECT_ROOT, f"data/GTFS_data/extracted/2024-10-22-ex-{ROUTE_SHORT_NAME}"
    )

    remove_line(SOURCE_DIR, OUTPUT_DIR, ROUTE_SHORT_NAME)
