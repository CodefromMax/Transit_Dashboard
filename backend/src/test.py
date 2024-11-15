from gettext import find
from flask import Flask, request, jsonify
import csv
import os
import shutil
import math
from helper.find_project_root import find_project_root
import traceback

app = Flask(__name__)

PROJECT_ROOT = find_project_root("Transit_Dashboard")

# Paths to source and destination folders
SOURCE_DIR = os.path.join(PROJECT_ROOT, "data/GTFS_data/extracted/2024-10-22")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "backend/src/gtfs_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FILES = ["shapes", "stops"]
# FILES = ["agency", "calendar_dates", "calendar", "routes", "shapes", "stop_times", "stops", "trips"]

# agency can stay the same, does not need to be edited


# File paths
PATHS_DICT = {"source": {}, "output": {}}

for file_name in FILES:
    PATHS_DICT["source"][file_name] = os.path.join(SOURCE_DIR, f"{file_name}.txt")
    PATHS_DICT["output"][file_name] = os.path.join(OUTPUT_DIR, f"{file_name}.txt")


# Function to calculate Euclidean distance
def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)


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


# Function to append new GTFS data
def append_gtfs(data):
    """
    Append new data to the GTFS files in the output folder.

    Args:
        data (list): List of dictionaries with 'id', 'type', 'lat', 'lng'.
    Returns:
        dict: Status and updated file paths.
    """
    # Read and determine the next stop_id
    with open(PATHS_DICT["output"]["stops"], mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_stop_ids = [
            int(row["stop_id"]) for row in reader if row["stop_id"].isdigit()
        ]
    next_stop_id = max(existing_stop_ids, default=0) + 1

    # Read and determine the next shape sequence
    with open(PATHS_DICT["output"]["shapes"], mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_shape_id = [
            int(row["shape_id"]) for row in reader if row["shape_id"].isdigit()
        ]
    next_shape_id = max(existing_shape_id, default=0) + 1

    # Calculate distances for the shape
    distances = [0.0]
    for i in range(1, len(data)):
        lat1, lon1 = data[i - 1]["lat"], data[i - 1]["lng"]
        lat2, lon2 = data[i]["lat"], data[i]["lng"]
        distances.append(distances[-1] + calculate_distance(lat1, lon1, lat2, lon2))

    # Append to shapes.txt
    with open(
        PATHS_DICT["output"]["shapes"], mode="a", newline="", encoding="utf-8"
    ) as file:
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

    # Append to stops.txt
    with open(
        PATHS_DICT["output"]["stops"], mode="a", newline="", encoding="utf-8"
    ) as file:
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
        for idx, point in enumerate(data):
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

    return {
        "status": "success",
        "shapes_file": PATHS_DICT["output"]["shapes"],
        "stops_file": PATHS_DICT["output"]["stops"],
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
        result = append_gtfs(points)
        return jsonify(result), 200
    except Exception as e:
        error_message = traceback.format_exc()
        return jsonify({"error": error_message}), 500


if __name__ == "__main__":
    app.run(debug=True)
