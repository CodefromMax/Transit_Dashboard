import csv
import json
import random
from shapely import wkt
from shapely.geometry import mapping
from helper.find_project_root import find_project_root
import sys

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

def csv_to_geojson(csv_file, geojson_file):
    features = []

    # Open the CSV file
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for idx, row in enumerate(reader):
            # Parse the 'geometry' field from WKT to GeoJSON-like format using Shapely
            geometry = wkt.loads(row['geometry'])

            # Prepare the feature properties (you can customize the fields here)
            properties = {
                "CTUID": row['CTUID'],
                "DGUID": row['DGUID'],
                "CTNAME": row['CTNAME'],
                "LANDAREA": float(row['LANDAREA']),
                "PRUID": row['PRUID'],
                "name": f"Feature-{idx + 1}",  # Example: "Feature-1", "Feature-2", etc.
                "density": round(float(row['LANDAREA']) * 100, 2)  # Random density value for each feature
            }

            # Create a feature object with geometry and properties
            feature = {
                "type": "Feature",
                "properties": properties,
                "geometry": mapping(geometry)
            }

            features.append(feature)

    # Create the final GeoJSON structure
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    # Write the GeoJSON to a file
    with open(geojson_file, 'w', encoding='utf-8') as geojsonfile:
        json.dump(geojson_data, geojsonfile, indent=4)

    print(f"GeoJSON file created: {geojson_file}")

if __name__ == '__main__':
    from helper.find_project_root import find_project_root
    root_path = find_project_root("Transit_Dashboard")

    # Usage example
    csv_file = f"{root_path}/data/census/toronto_ct_boundaries_centroids.csv"  # Replace with your CSV file path
    geojson_file = f"{root_path}/data/census/toronto_ct_boundaries_random_metric.geojson"  # Output GeoJSON file path

    csv_to_geojson(csv_file, geojson_file)
