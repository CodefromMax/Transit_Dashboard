import geopandas as gpd 
import pandas as pd 

# Path to shape file
SHAPE_PATH = "/Users/ninajiang/Desktop/Capstone_Trasnforming_Transit_Access/Transit_Dashboard/data/temp_census/lct_000b21a_e/lct_000b21a_e.shp"
gdf = gpd.read_file(SHAPE_PATH)

toronto_gdf = gdf[gdf['CTUID'].str.startswith('535')]
toronto_gdf['centroid'] = toronto_gdf.geometry.centroid

df = pd.DataFrame(toronto_gdf)

OUTPUT_PATH = "/Users/ninajiang/Desktop/Capstone_Trasnforming_Transit_Access/Transit_Dashboard/data/temp_census/toronto_ct_boundaries_centroids.csv"
df.to_csv(OUTPUT_PATH, index=False)

print("Saved to Destination")


