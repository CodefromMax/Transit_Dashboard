import csv
import math
import os
import shutil
import traceback

import pandas as pd
from flask import Flask, jsonify, request

from helper.find_project_root import find_project_root

app = Flask(__name__)

PROJECT_ROOT = find_project_root("Transit_Dashboard")
SOURCE_DIR = os.path.join(PROJECT_ROOT, "data/GTFS_data/extracted/2024-10-22")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "backend/src/gtfs_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
# FILES = ["shapes", "stops"]
FILES = [
    "agency",
    "calendar_dates",
    "calendar",
    "routes",
    "shapes",
    "stop_times",
    "stops",
    "trips",
]
# agency can stay the same, does not need to be edited
# File paths
PATHS_DICT = {"source": {}, "output": {}}
for file_name in FILES:
    PATHS_DICT["source"][file_name] = os.path.join(SOURCE_DIR, f"{file_name}.txt")
    PATHS_DICT["output"][file_name] = os.path.join(OUTPUT_DIR, f"{file_name}.txt")


def delete_existing_then_duplicate_gtfs():
    """
    Delete existing shapes.txt and stops.txt in the output folder (if they exist)
    and copy the source files to the output folder.
    """
    # Delete existing files if they exist
    for file in PATHS_DICT["output"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted existing file: {file}")

    # Copy files from source to output folder
    for file_name in FILES:
        shutil.copy(PATHS_DICT["source"][file_name], PATHS_DICT["output"][file_name])
        print(f"Copied over {file_name} copied to output folder.")


def create_shape_file(path: str, data, next_shape_id):

    def calculate_distance(lat1, lon1, lat2, lon2):
        return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)

    distances = [0.0]
    for i in range(1, len(data)):
        lat1, lon1 = data[i - 1]["lat"], data[i - 1]["lng"]
        lat2, lon2 = data[i]["lat"], data[i]["lng"]
        distances.append(distances[-1] + calculate_distance(lat1, lon1, lat2, lon2))

    with open(path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "shape_id",
                "shape_pt_lat",
                "shape_pt_lon",
                "shape_pt_sequence",
                "shape_dist_traveled",
            ],
        )
        for idx, point in enumerate(data):
            writer.writerow(
                {
                    "shape_id": next_shape_id,
                    "shape_pt_lat": point["lat"],
                    "shape_pt_lon": point["lng"],
                    "shape_pt_sequence": idx + 1,
                    "shape_dist_traveled": round(distances[idx], 4),
                }
            )
    return


def create_stops_file(path: str, data, next_stop_id, next_shape_id):
    with open(path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "stop_id",
                "stop_code",
                "stop_name",
                "stop_desc",
                "stop_lat",
                "stop_lon",
                "zone_id",
                "stop_url",
                "location_type",
                "parent_station",
                "stop_timezone",
                "wheelchair_boarding",
            ],
        )
        fake_station_id = 0
        for _, point in enumerate(data):
            if point["type"] == "station":  # Only include stations
                fake_station_id += 1
                writer.writerow(
                    {
                        "stop_id": next_stop_id,
                        "stop_code": "",
                        "stop_name": f"Station {next_shape_id}. Stop #{fake_station_id}",
                        "stop_desc": "",
                        "stop_lat": point["lat"],
                        "stop_lon": point["lng"],
                        "zone_id": "",
                        "stop_url": "",
                        "location_type": "",
                        "parent_station": "",
                        "stop_timezone": "",
                        "wheelchair_boarding": "1",
                    }
                )
                next_stop_id += 1
    return next_stop_id


def create_routes_file(path: str, next_route_id, agency_id, route_type):
    with open(path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "route_id",
                "agency_id",
                "route_short_name",
                "route_long_name",
                "route_desc",
                "route_type",
                "route_url",
                "route_color",
                "route_text_color",
            ],
        )
        writer.writerow(
            {
                "route_id": next_route_id,
                "agency_id": agency_id,
                "route_short_name": "NEW LINE",
                "route_long_name": "",
                "route_desc": "",
                "route_type": route_type,
                "route_url": "",
                "route_color": "FF0000",
                "route_text_color": "FFFFFF",
            }
        )
    return


def create_trips_file(path: str, next_trip_id, next_route_id, next_shape_id):
    trips = pd.read_csv(path)
    trips_new_line = trips[
        trips["route_id"] == 72927
    ]  # this is all the line 1 trips, remove hardcoding later...
    trips_new_line["trip_headsign"] = "New Line"
    trips_new_line["route_id"] = next_route_id
    trips_new_line["shape_id"] = next_shape_id
    trips_new_line["trip_id"] = range(next_trip_id, next_trip_id + len(trips_new_line))
    trips = pd.concat([trips, trips_new_line], ignore_index=True)
    trips.to_csv(path, index=False)


def create_stop_times_file(
    trips_path: str,
    stops_path: str,
    stop_times_path: str,
    next_stop_id: int,
    last_stop_id: int,
    n_trips: int = 10,
):
    """
    Create stop times for the new line by mimicking existing line's schedule
    but with new stops and adjusted times based on historical speed data.

    Args:
        trips_path: Path to trips.txt
        stops_path: Path to stops.txt
        stop_times_path: Path to stop_times.txt
        next_stop_id: First stop ID of the new line
        last_stop_id: Last stop ID of the new line
        n_trips: Number of reference trips to use for speed calculation
    """
    from datetime import datetime, timedelta

    import pandas as pd

    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points"""
        import math

        return math.sqrt(
            (float(lat2) - float(lat1)) ** 2 + (float(lon2) - float(lon1)) ** 2
        )

    # Read necessary files
    trips_df = pd.read_csv(trips_path)
    stops_df = pd.read_csv(stops_path)
    stop_times_df = pd.read_csv(stop_times_path)

    # Get reference route data
    reference_trips = trips_df[trips_df["route_id"] == 72927]["trip_id"].unique()
    reference_stop_times = stop_times_df[stop_times_df["trip_id"].isin(reference_trips)]

    # Calculate average speed from reference trips
    def get_average_speed():
        speeds = []

        # Get sample of trips
        sample_trips = reference_trips[:n_trips]

        for trip_id in sample_trips:
            trip_stops = reference_stop_times[
                reference_stop_times["trip_id"] == trip_id
            ].sort_values("stop_sequence")

            if len(trip_stops) < 2:
                continue

            for i in range(len(trip_stops) - 1):
                current_stop = stops_df[
                    stops_df["stop_id"] == trip_stops.iloc[i]["stop_id"]
                ].iloc[0]
                next_stop = stops_df[
                    stops_df["stop_id"] == trip_stops.iloc[i + 1]["stop_id"]
                ].iloc[0]

                # Calculate distance
                distance = calculate_distance(
                    current_stop["stop_lat"],
                    current_stop["stop_lon"],
                    next_stop["stop_lat"],
                    next_stop["stop_lon"],
                )

                # Calculate time difference
                current_time = datetime.strptime(
                    trip_stops.iloc[i]["departure_time"], "%H:%M:%S"
                )
                next_time = datetime.strptime(
                    trip_stops.iloc[i + 1]["arrival_time"], "%H:%M:%S"
                )
                time_diff = (next_time - current_time).total_seconds()

                if time_diff > 0:  # Avoid division by zero
                    # Calculate speed (distance units per second)
                    speed = distance / time_diff
                    speeds.append(speed)

        # Return average speed, defaulting to a reasonable value if no valid speeds found
        return sum(speeds) / len(speeds) if speeds else 0.001

    # Get average speed from reference trips
    avg_speed = get_average_speed()
    print(f"Calculated average speed: {avg_speed:.6f} distance units per second")

    # Get new line trips
    new_trips = trips_df[trips_df["route_id"] > 72927]["trip_id"].unique()

    # Get new stops for the line
    new_stops = stops_df[
        (stops_df["stop_id"] >= next_stop_id) & (stops_df["stop_id"] <= last_stop_id)
    ].sort_values("stop_id")

    def calculate_travel_time(lat1, lon1, lat2, lon2):
        """Calculate travel time between stops in seconds based on average speed"""
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        return int(distance / avg_speed)

    new_stop_times = []

    # For each new trip
    for trip_id in new_trips:
        # Get reference trip's first arrival time
        ref_trip = reference_stop_times[
            reference_stop_times["trip_id"] == reference_trips[0]
        ]
        start_time = datetime.strptime(ref_trip.iloc[0]["arrival_time"], "%H:%M:%S")

        # Determine direction based on trip_id (even = forward, odd = backward)
        stops_sequence = new_stops if trip_id % 2 == 0 else new_stops[::-1]

        current_time = start_time

        # Create stop times for each stop in sequence
        for idx, (_, stop) in enumerate(stops_sequence.iterrows()):
            if idx > 0:
                # Calculate time to next stop using inferred speed
                prev_stop = stops_sequence.iloc[idx - 1]
                travel_seconds = calculate_travel_time(
                    prev_stop["stop_lat"],
                    prev_stop["stop_lon"],
                    stop["stop_lat"],
                    stop["stop_lon"],
                )
                current_time += timedelta(seconds=travel_seconds)

            new_stop_times.append(
                {
                    "trip_id": trip_id,
                    "arrival_time": current_time.strftime("%H:%M:%S"),
                    "departure_time": current_time.strftime("%H:%M:%S"),
                    "stop_id": stop["stop_id"],
                    "stop_sequence": idx + 1,
                    "stop_headsign": "",
                    "pickup_type": 0,
                    "drop_off_type": 0,
                    "shape_dist_traveled": "",
                }
            )

    # Convert to DataFrame and append to existing stop_times
    new_stop_times_df = pd.DataFrame(new_stop_times)
    final_stop_times = pd.concat([stop_times_df, new_stop_times_df], ignore_index=True)

    # Save to file
    final_stop_times.to_csv(stop_times_path, index=False)
    print(
        f"Created stop times for {len(new_trips)} trips with {len(new_stops)} stops each"
    )


def create_new_gtfs(data):
    """
    Append new data to the GTFS files in the output folder.

    Args:
        data (list): List of dictionaries with 'id', 'type', 'lat', 'lng'.
    Returns:
        dict: Status and updated file paths.
    """

    def get_next_key_id_from_file(path: str, key_id: str):
        with open(path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_ids = [int(row[key_id]) for row in reader if row[key_id].isdigit()]
            return max(existing_ids, default=0) + 1

    next_stop_id = get_next_key_id_from_file(PATHS_DICT["output"]["stops"], "stop_id")
    next_shape_id = get_next_key_id_from_file(
        PATHS_DICT["output"]["shapes"], "shape_id"
    )
    next_trip_id = get_next_key_id_from_file(PATHS_DICT["output"]["trips"], "trip_id")
    next_route_id = get_next_key_id_from_file(
        PATHS_DICT["output"]["routes"], "route_id"
    )
    route_type = 1  # Subway route type
    agency_id = 1  # TTC Agency ID

    """
    What we can do is choose to have the same service as line 1.
      TRIPS.TXT This means from trips just get all of line 1
      Duplicate with unique route_id (only 1), same # of service id, unique trip id's
      Same number of direction there and back
      Give all the same shape id
      block id?
    
    ##INVESTIAGE WHY THERE ARE MANY DIFFERENT SHAPE_ID
    """
    create_shape_file(PATHS_DICT["output"]["shapes"], data, next_shape_id)
    last_stop_id = create_stops_file(
        PATHS_DICT["output"]["stops"], data, next_stop_id, next_shape_id
    )
    create_routes_file(
        PATHS_DICT["output"]["routes"], next_route_id, agency_id, route_type
    )

    create_trips_file(
        PATHS_DICT["output"]["trips"],
        next_trip_id,
        next_route_id,
        next_shape_id,
    )

    create_stop_times_file(
        PATHS_DICT["output"]["trips"],
        PATHS_DICT["output"]["stops"],
        PATHS_DICT["output"]["stop_times"],
        next_stop_id,
        last_stop_id,
    )

    return {
        "status": "success",
        "shapes_file": PATHS_DICT["output"]["shapes"],
        "stops_file": PATHS_DICT["output"]["stops"],
        "routes_file": PATHS_DICT["output"]["routes"],
        "trips_file": PATHS_DICT["output"]["trips"],
        "stop_times": PATHS_DICT["output"]["stop_times"],
    }


@app.route("/append-gtfs", methods=["POST"])
def append_gtfs_endpoint():
    """
    API endpoint to append GTFS data to the duplicated files.
    Expects JSON payload with points and a new shape ID.
    """
    try:
        request_data = request.json
        if not request_data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        points = request_data

        if not points:
            return jsonify({"error": "Missing 'points' or 'shape_id' in payload"}), 400

        # Duplicate the existing files after deleting old ones
        delete_existing_then_duplicate_gtfs()

        # Append new GTFS data
        result = create_new_gtfs(points)
        return jsonify(result), 200
    except Exception as e:
        error_message = traceback.format_exc()
        return jsonify({"error": error_message}), 500


if __name__ == "__main__":
    app.run(debug=True)
