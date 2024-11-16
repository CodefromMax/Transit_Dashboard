"""
Data Class
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import re

class DataMain(object):
    def __init__(self, path, name = None, type = None):
        self.path = path
        self.name = name # not used for now
        self.type = type # not used for now, read data hardcoded

    def read_csv(self):
        df = pd.read_csv(self.path)
        return df
    
    def read_gdf(self):
        gdf = gpd.read_file(self.path)
        return gdf
    
    def save_geojson(self, gdf, output_path):
        gdf.to_file(output_path, driver='GeoJSON')
        print("Save Geojson to ", output_path)

    def save_csv(self):
        pass
    
    def save_json(self):
        pass

    # boundaries (shape file in json will be passed separately)
    # aggregate the data (Key destination, Job Availability, Demographic, Calculated Travel Time)
    def aggregate_for_metric(self, key_dest, job, dem, trvl_time):
        # DO NOT CONCAT TRAVEL TIME FOR NOW
        combined_df = key_dest.merge(job, on='CTUID', how='inner')
        combined_df = combined_df.merge(dem, on='CTUID', how='inner')

        return combined_df
    

class Boundaries(DataMain):
    def __init__(self, path, name, type):
        super().__init__(path, name, type)
        
        self.gdf = self.read_gdf()
        self.gdf_centroid = self.calculate_centroids()
        self.gdf['CTUID'] = self.gdf['CTUID'].astype(float)
        self.gdf_centroid['CTUID'] = self.gdf_centroid['CTUID'].astype(float)


    def calculate_centroids(self):
        gdf_centroid = self.gdf.copy()
        gdf_centroid['centroid'] = gdf_centroid.geometry.centroid
        return gdf_centroid
    
    def save_only_centroid(self, output_path, output_type):
        gdf_centroid_only = gpd.GeoDataFrame(self.gdf_centroid[['CTUID']], geometry=self.gdf_centroid['centroid'])

        if output_type == "Geojson":
            self.save_geojson(gdf = gdf_centroid_only, output_path = output_path)



class KeyDestination (DataMain):
    def __init__(self, path, name, type):
        super().__init__(path, name, type)
        self.key_dest_df = self.read_csv()
        self.key_dest_df['CTUID'] = self.key_dest_df['CTUID'].astype(float)

# ---------------- User editable ------------------ #
class JobData (DataMain):
    def __init__(self, path, name, type):
        super().__init__(path, name, type)

        self.job_df = self.read_csv()
        self.job_df['CTUID'] = self.job_df['CTUID'].astype(float)


# FOR CHASS DATASET
class CensusDemographic(DataMain):
    def __init__(self, path, name, column_path, type):
        super().__init__(path, name, type)
        self.column_path = column_path

        self.census_df = self.read_csv()
        self.column_names = self.read_column()
        self.census_df.columns = self.column_names[1:]
        self.census_df = self.census_df.rename(columns={'GEO UID':'CTUID'})
        self.census_df = self.census_df.fillna(0)
        self.census_df['CTUID'] = self.census_df['CTUID'].astype(float)
        self.census_df = self.census_df.drop(index=0)

    def read_column(self):
        with open(self.column_path, 'r') as f:
            column_names = [line.strip() for line in f.readlines()]
        column_names = [re.sub(r'^COL\d+ - ', '', name) for name in column_names]
        return column_names

    
