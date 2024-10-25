import geopandas as gpd 
import pandas as pd
from helper.find_project_root import find_project_root

def main():
    # Path to shape file
    
    root_path = find_project_root("Transit_Dashboard")
    SHAPE_PATH = f"{root_path}/data/census/lct_000b21a_e/lct_000b21a_e.shp"
    gdf = gpd.read_file(SHAPE_PATH)

    toronto_gdf = gdf[gdf['CTUID'].str.startswith('535')]
    toronto_gdf['centroid'] = toronto_gdf.geometry.centroid

    df = pd.DataFrame(toronto_gdf)

    OUTPUT_PATH = f"{root_path}/data/census/toronto_ct_boundaries_centroids.csv"
    df.to_csv(OUTPUT_PATH, index=False)

    print("Saved to Destination")


if __name__ == "__main__":
    main()
