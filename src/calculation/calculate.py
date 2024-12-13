"""
Running Travel Time Calculation + Metric Calculation for New GTFS Data
"""
import pandas as pd
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join('../..')) # project root [NINA][!!!!!] make sure ends with /Transit_Dashboard
sys.path.append(PROJECT_ROOT)
print(PROJECT_ROOT)

from src.calculation.travel_time_matrix.TravelTimeCalculation import TravelTimeCalculation
from src.calculation.Metric_Calculation.MetricCalculation import MetricCalculation
OSM_PATH = os.path.join(PROJECT_ROOT, "data/OSM_data/Toronto.osm.pbf")
# OLD_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/extracted/2024-10-22_testing")
NEW_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip") # TODO: [!!!!!] PLEASE INSERT THE PATH TO WHERE THE NEW GTFS DATA IS SAVED
CT_CENTROID_PATH = os.path.join(PROJECT_ROOT, "data/census_tract_data/toronto_ct_centroids1.geojson")

print("[DEBUG]: ", OSM_PATH)

RUN_TRAVEL_TIME_TYPES = ["Hospitals", "Schools", "Libraries", "Cooling_Center", "Jobs"]

# TODO: [JAN/FEB IMPROVEMEMT] for not Overwriting any previously calculated after travel time matrix / metrics
# def get_unique_filename(base_filename):
#     # Extract the base name and extension
#     base, ext = os.path.splitext(base_filename)
    
#     # Start with the original filename
#     filename = base + ext
#     counter = 1
    
#     # Loop until we find an available filename
#     while os.path.exists(filename):
#         filename = f"{base}_{counter}{ext}"
#         counter += 1

#     return filename

def run_travel_time(OSM = OSM_PATH, GTFS = NEW_GTFS_PATH, types = RUN_TRAVEL_TIME_TYPES, is_after = True):
   
    # determine suffix of output file
    if is_after:
        out_suffix = "_after"
    else:
        out_suffix = "_baseline"
    
    # travel time output path
    travel_time_out_folder = os.path.join(PROJECT_ROOT, "data/results/travel_time_matrix")
    # check if the output folder for travel time matrix exists,
    if not os.path.exists(travel_time_out_folder):
        os.makedirs(travel_time_out_folder)
    print("[DEBUG]: ", travel_time_out_folder)
    print("[DEBUG]: ",  os.path.exists(travel_time_out_folder))

    travel_calculator = TravelTimeCalculation(OSM, GTFS)
    travel_calculator.build_transport_network()

    # calculate travel time matrix for key destination and job data
    for item in types:
        if item == "Jobs":
            origins_path = CT_CENTROID_PATH
            destinations_path = CT_CENTROID_PATH
            output_path = os.path.join(travel_time_out_folder, item+out_suffix+".csv")
            print("[DEBUG] output path: ", output_path)
            
            travel_calculator.compute_travel_time_matrix(
                origins_path = origins_path, 
                destinations_path = destinations_path, 
                output_path = output_path, 
                origin_id_col='CTUID', destination_id_col='CTUID',
                origin_is_point=True, destination_is_point=True,  # If it is not a point, the centroid of the polygon will be used
            )
            
        else:
            origins_path = CT_CENTROID_PATH
            destinations_path = os.path.join(PROJECT_ROOT, "data/key_destination_data/", item + "_4326.geojson")
            output_path = os.path.join(travel_time_out_folder, item+out_suffix+".csv")
            print("[DEBUG] output path: ", output_path)
            
            travel_calculator.compute_travel_time_matrix(
                origins_path = origins_path, 
                destinations_path = destinations_path, 
                output_path = output_path, 
                origin_id_col='CTUID', destination_id_col='Address_ID',
                origin_is_point=True, destination_is_point=True,  # If it is not a point, the centroid of the polygon will be used
            )


def run_metrics_calculation(travel_time_out_folder = os.path.join(PROJECT_ROOT, "data/results/travel_time_matrix"), threshold = 30, n_closest =1, is_after = True, types = RUN_TRAVEL_TIME_TYPES):
    
    # metric output paths
    metric_out_folder = os.path.join(PROJECT_ROOT, "data/results/metrics")
    # check if the output folder for travel time matrix exists,
    if not os.path.exists(metric_out_folder):
        os.makedirs(metric_out_folder)
    print("[DEBUG]: ", metric_out_folder)
    print("[DEBUG]: ",  os.path.exists(metric_out_folder))

    # output suffix
    if is_after:
        out_suffix = "_after"
    else:
        # if run baseline, only run metric calculation, not calculate difference
        out_suffix = "_baseline"

    # calculate metrics for key destination and job access
    for item in types:

        if item == "Jobs":
            # travel time matrix for item
            item_travel_time = os.path.join(travel_time_out_folder, item+out_suffix+".csv")
            
            # get employment data by census tract
            # TODO: [NINA][!!!!!] PLEASE VERIFY PATH, REPLACE IF NECESSARY
            employment_data = pd.read_csv(os.path.join(PROJECT_ROOT, "draft/Employment_data.csv"))
            ctuid_reference_path = os.path.join(PROJECT_ROOT, "data", "results/CTUIDs.csv")
            output_path  = os.path.join(metric_out_folder, item+"_access_threshold_"+str(threshold)+out_suffix+".csv")

            # calculate metric for job access
            metric_cal = MetricCalculation(item_travel_time)
            CT_within_30 = metric_cal.filter_destinations(threshold = threshold)
            CT_within_30_grouped = MetricCalculation.group_to_ids_by_ctuid(CT_within_30) #.to_csv("../results/CT_within_30_grouped.csv", index=False)
            MetricCalculation.sum_jobs_by_from_id_and_fill_missing(CT_within_30_grouped, employment_data, ctuid_reference_path= ctuid_reference_path, output_path= output_path)
       
        else: 
            # travel time matrix for item
            item_travel_time = os.path.join(travel_time_out_folder, item+out_suffix+".csv")

            # Destination Paths
            num_of_dest_output_path = os.path.join(metric_out_folder, "dest_within_threshold_"+str(threshold)+"_"+item+out_suffix+".csv") # filtered travel time matrix with time threshold
            nth_travel_time_output_path = os.path.join(metric_out_folder, str(n_closest)+"th_closest_travel_time_"+item+out_suffix+".csv") # n-th closest travel time
        
            # Calculate metrics
            # [NINA][!!!!!] the travel time matrix has to be computed with the run_travel_time function to ensure naming consistency
            metric_cal = MetricCalculation(item_travel_time)
            metric_cal.filter_destinations(output_path = num_of_dest_output_path, threshold = threshold) # filter travel time matrix based on threshold
            metric_cal.get_nth_travel_time(n  = n_closest, output_path = nth_travel_time_output_path) # compute n-th closest destination travel time




    # calculate metric comparison



run_travel_time(OSM = OSM_PATH, GTFS = NEW_GTFS_PATH, types = RUN_TRAVEL_TIME_TYPES, is_after = True)
run_metrics_calculation(travel_time_out_folder = os.path.join(PROJECT_ROOT, "data/results/travel_time_matrix"), threshold = 30, n_closest =1, is_after = True, types = RUN_TRAVEL_TIME_TYPES)


