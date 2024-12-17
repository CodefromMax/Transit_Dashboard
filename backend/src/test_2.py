import csv
import math
import os
import shutil
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import pandas as pd
from flask import Flask, jsonify, request

from helper.find_project_root import find_project_root

app = Flask(__name__)

# Constants
PROJECT_ROOT = find_project_root("Transit_Dashboard")
SOURCE_DIR = os.path.join(PROJECT_ROOT, "data/GTFS_data/extracted/2024-10-22")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "backend/src/gtfs_output")
REFERENCE_ROUTE_ID = 72927 #line 1 id
ROUTE_TYPE = 1  # Subway route type
AGENCY_ID = 1  # TTC Agency ID

# File configuration
GTFS_FILES = [
    "agency",
    "calendar_dates",
    "calendar",
    "routes",
    "shapes",
    "stop_times",
    "stops",
    "trips",
]


class GTFSManager:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.paths = self._initialize_paths()
        self.df_cache = {}
        self.AVERAGE_TRANSIT_SPEED = 30  # Average speed in km/h for subway/rail

    def _initialize_paths(self) -> Dict[str, Dict[str, str]]:
        """Initialize file paths for source and output files."""
        paths = {"source": {}, "output": {}}
        for file_name in GTFS_FILES:
            paths["source"][file_name] = os.path.join(SOURCE_DIR, f"{file_name}.txt")
            paths["output"][file_name] = os.path.join(OUTPUT_DIR, f"{file_name}.txt")
        return paths

    def reset_and_copy_files(self):
        """Reset output directory and copy source files."""
        for file_name in GTFS_FILES:
            output_path = self.paths["output"][file_name]
            if os.path.exists(output_path):
                os.remove(output_path)
            shutil.copy(self.paths["source"][file_name], output_path)
            print(f"Reset and copied {file_name}")
        self.df_cache.clear()  # Clear cache after reset

    def _get_dataframe(self, file_name: str, source: bool = False) -> pd.DataFrame:
        """Get DataFrame from cache or load it."""
        key = f"{'source' if source else 'output'}_{file_name}"
        if key not in self.df_cache:
            path = self.paths["source" if source else "output"][file_name]
            self.df_cache[key] = pd.read_csv(path)
        return self.df_cache[key]

    def _calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two points in kilometers using the haversine formula.
        """
        R = 6371  # Earth's radius in kilometers

        # Convert latitude and longitude to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    def _get_next_id(self, file_name: str, id_column: str) -> int:
        """Get next available ID for a given file and column."""
        df = pd.read_csv(self.paths["output"][file_name])
        
        numeric_ids = []
        for id_val in df[id_column]:
            try:
                numeric_id = int(str(id_val).strip())
                numeric_ids.append(numeric_id)
            except (ValueError, TypeError):
                continue
        
        return max(numeric_ids) + 1 if numeric_ids else 1

    def _calculate_travel_time(self, distance_km: float, speed_kmh: float = None) -> int:
        """
        Calculate travel time in seconds based on distance and speed.
        
        Args:
            distance_km: Distance in kilometers
            speed_kmh: Speed in kilometers per hour (defaults to self.AVERAGE_TRANSIT_SPEED)
        
        Returns:
            int: Travel time in seconds
        """
        speed = speed_kmh or self.AVERAGE_TRANSIT_SPEED
        hours = distance_km / speed
        return int(hours * 3600)  # Convert hours to seconds

    def create_shapes(self, data: List[Dict], shape_id: int):
        """Create shapes from coordinate data with accurate distances in kilometers."""
        shapes_df = self._get_dataframe("shapes")
        
        shapes_data = []
        distances = [0.0]
        
        # Calculate cumulative distances in kilometers
        for i in range(1, len(data)):
            lat1, lon1 = data[i - 1]["lat"], data[i - 1]["lng"]
            lat2, lon2 = data[i]["lat"], data[i]["lng"]
            distance_km = self._calculate_distance_km(lat1, lon1, lat2, lon2)
            distances.append(distances[-1] + distance_km)

        for idx, point in enumerate(data):
            shapes_data.append({
                "shape_id": shape_id,
                "shape_pt_lat": point["lat"],
                "shape_pt_lon": point["lng"],
                "shape_pt_sequence": idx + 1,
                "shape_dist_traveled": round(distances[idx], 4)
            })

        new_shapes = pd.DataFrame(shapes_data)
        updated_shapes = pd.concat([shapes_df, new_shapes], ignore_index=True)
        updated_shapes.to_csv(self.paths["output"]["shapes"], index=False)
        self.df_cache["output_shapes"] = updated_shapes

    def calculate_average_speed(self, reference_trips: List[int], reference_stop_times: pd.DataFrame, stops_df: pd.DataFrame) -> float:
        """Calculate average speed from reference trips in km/h."""
        speeds = []
        
        for trip_id in reference_trips:
            trip_stops = reference_stop_times[reference_stop_times["trip_id"] == trip_id].sort_values("stop_sequence")
            if len(trip_stops) < 2:
                continue
                
            for i in range(len(trip_stops) - 1):
                current_stop = stops_df[stops_df["stop_id"] == trip_stops.iloc[i]["stop_id"]].iloc[0]
                next_stop = stops_df[stops_df["stop_id"] == trip_stops.iloc[i + 1]["stop_id"]].iloc[0]
                
                distance_km = self._calculate_distance_km(
                    current_stop["stop_lat"], current_stop["stop_lon"],
                    next_stop["stop_lat"], next_stop["stop_lon"]
                )
                
                current_time = datetime.strptime(trip_stops.iloc[i]["departure_time"], "%H:%M:%S")
                next_time = datetime.strptime(trip_stops.iloc[i + 1]["arrival_time"], "%H:%M:%S")
                time_diff_hours = (next_time - current_time).total_seconds() / 3600
                
                if time_diff_hours > 0:
                    speed_kmh = distance_km / time_diff_hours
                    speeds.append(speed_kmh)
        
        return sum(speeds) / len(speeds) if speeds else self.AVERAGE_TRANSIT_SPEED
    
    def create_stops(self, data: List[Dict], next_stop_id: int, shape_id: int) -> int:
        """Create stops from coordinate data."""
        stops_df = self._get_dataframe("stops")
        
        stops_data = []
        station_count = 0
        current_stop_id = next_stop_id
        
        for point in data:
            if point["type"] == "station":
                station_count += 1
                stops_data.append({
                    "stop_id": current_stop_id,
                    "stop_code": "",
                    "stop_name": f"Station {shape_id}. Stop #{station_count}",
                    "stop_desc": "",
                    "stop_lat": point["lat"],
                    "stop_lon": point["lng"],
                    "zone_id": "",
                    "stop_url": "",
                    "location_type": "",
                    "parent_station": "",
                    "stop_timezone": "",
                    "wheelchair_boarding": "1"
                })
                current_stop_id += 1

        new_stops = pd.DataFrame(stops_data)
        updated_stops = pd.concat([stops_df, new_stops], ignore_index=True)
        updated_stops.to_csv(self.paths["output"]["stops"], index=False)
        self.df_cache["output_stops"] = updated_stops
        
        return current_stop_id - 1  # Return last stop_id
    
    def create_trips(self, next_trip_id: int, route_id: int, shape_id: int):
        """Create trips for new route."""
        trips_df = self._get_dataframe("trips")
        
        # Get reference trips and modify for new route
        reference_trips = trips_df[trips_df["route_id"] == REFERENCE_ROUTE_ID].copy()
        reference_trips["trip_headsign"] = "New Line"
        reference_trips["route_id"] = route_id
        reference_trips["shape_id"] = shape_id
        reference_trips["trip_id"] = range(next_trip_id, next_trip_id + len(reference_trips))
        
        updated_trips = pd.concat([trips_df, reference_trips], ignore_index=True)
        updated_trips.to_csv(self.paths["output"]["trips"], index=False)
        self.df_cache["output_trips"] = updated_trips
        
    def create_route(self, route_id: int):
        """Create new route."""
        routes_df = self._get_dataframe("routes")
        
        new_route = pd.DataFrame([{
            "route_id": route_id,
            "agency_id": AGENCY_ID,
            "route_short_name": "NEW LINE",
            "route_long_name": "",
            "route_desc": "",
            "route_type": ROUTE_TYPE,
            "route_url": "",
            "route_color": "FF0000",
            "route_text_color": "FFFFFF"
        }])
        
        updated_routes = pd.concat([routes_df, new_route], ignore_index=True)
        updated_routes.to_csv(self.paths["output"]["routes"], index=False)
        self.df_cache["output_routes"] = updated_routes

    def create_stop_times(self, first_stop_id: int, last_stop_id: int, n_trips: int = 10):
        """Create stop times with accurate travel times based on distances."""
        trips_df = self._get_dataframe("trips")
        stops_df = self._get_dataframe("stops")
        stop_times_df = self._get_dataframe("stop_times")
        
        # Get reference data and calculate average speed
        reference_trips = trips_df[trips_df["route_id"] == REFERENCE_ROUTE_ID]["trip_id"].unique()[:n_trips]
        reference_stop_times = stop_times_df[stop_times_df["trip_id"].isin(reference_trips)]
        
        avg_speed_kmh = self.calculate_average_speed(reference_trips, reference_stop_times, stops_df)
        print(f"Average speed from reference trips: {avg_speed_kmh:.2f} km/h")
        
        # Create new stop times
        new_trips = trips_df[trips_df["route_id"] > REFERENCE_ROUTE_ID]["trip_id"].unique()
        new_stops = stops_df[
            (stops_df["stop_id"] >= first_stop_id) & 
            (stops_df["stop_id"] <= last_stop_id)
        ].sort_values("stop_id")
        
        new_stop_times = []
        for trip_id in new_trips:
            ref_trip = reference_stop_times[reference_stop_times["trip_id"] == reference_trips[0]]
            current_time = datetime.strptime(ref_trip.iloc[0]["arrival_time"], "%H:%M:%S")
            
            stops_sequence = new_stops if trip_id % 2 == 0 else new_stops[::-1]
            
            for idx, (_, stop) in enumerate(stops_sequence.iterrows()):
                if idx > 0:
                    prev_stop = stops_sequence.iloc[idx - 1]
                    distance_km = self._calculate_distance_km(
                        prev_stop["stop_lat"], prev_stop["stop_lon"],
                        stop["stop_lat"], stop["stop_lon"]
                    )
                    travel_seconds = self._calculate_travel_time(distance_km, avg_speed_kmh)
                    current_time += timedelta(seconds=travel_seconds)
                
                new_stop_times.append({
                    "trip_id": trip_id,
                    "arrival_time": current_time.strftime("%H:%M:%S"),
                    "departure_time": current_time.strftime("%H:%M:%S"),
                    "stop_id": stop["stop_id"],
                    "stop_sequence": idx + 1,
                    "stop_headsign": "",
                    "pickup_type": 0,
                    "drop_off_type": 0,
                    "shape_dist_traveled": ""
                })
        
        new_stop_times_df = pd.DataFrame(new_stop_times)
        updated_stop_times = pd.concat([stop_times_df, new_stop_times_df], ignore_index=True)
        updated_stop_times.to_csv(self.paths["output"]["stop_times"], index=False)
        self.df_cache["output_stop_times"] = updated_stop_times
    
    def process_new_data(self, data: List[Dict]) -> Dict[str, str]:
        """Process new GTFS data and create all necessary files."""
        self.reset_and_copy_files()
        
        next_stop_id = self._get_next_id("stops", "stop_id")
        next_shape_id = self._get_next_id("shapes", "shape_id")
        next_trip_id = self._get_next_id("trips", "trip_id")
        next_route_id = self._get_next_id("routes", "route_id")
        
        self.create_shapes(data, next_shape_id)
        last_stop_id = self.create_stops(data, next_stop_id, next_shape_id)
        self.create_route(next_route_id)
        self.create_trips(next_trip_id, next_route_id, next_shape_id)
        self.create_stop_times(next_stop_id, last_stop_id)
        
        return {
            "status": "success",
            **{f"{file}_file": self.paths["output"][file] for file in GTFS_FILES}
        }
# Flask routes
@app.route("/append-gtfs", methods=["POST"])
def append_gtfs_endpoint():
    """API endpoint to append GTFS data."""
    try:
        if not request.json:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        gtfs_manager = GTFSManager()
        result = gtfs_manager.process_new_data(request.json)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": traceback.format_exc()}), 500


if __name__ == "__main__":
    app.run(debug=True)
