"""
Running Travel Time Calculation + Metric Calculation for New GTFS Data
"""
import pandas as pd
import os
import sys

PROJECT_ROOT = "/Users/max/Desktop/Transit_Dashboard"
# = os.path.abspath(os.path.join('../..')) # project root [NINA][!!!!!] make sure ends with /Transit_Dashboard
sys.path.append(PROJECT_ROOT)
print(PROJECT_ROOT)

from src.calculation.travel_time_matrix.TravelTimeCalculation import TravelTimeCalculation
from src.calculation.Metric_Calculation.MetricCalculation import MetricCalculation
OSM_PATH = os.path.join(PROJECT_ROOT, "data/OSM_data/Toronto.osm.pbf")
OLD_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip")
NEW_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/gtfs_output_v10.zip") # TODO: [!!!!!] PLEASE INSERT THE PATH TO WHERE THE NEW GTFS DATA IS SAVED
CT_CENTROID_PATH = os.path.join(PROJECT_ROOT, "data/census_tract_data/toronto_ct_centroids1.geojson")

print("[DEBUG]: ", OSM_PATH)

RUN_TRAVEL_TIME_TYPES = ["Hospitals", "Schools", "Libraries", "Cooling_Center", "Jobs"] # update to separate metric categories

# separate calculation based on metric types
KEY_DEST = ["Hospitals", "Schools", "Libraries", "Cooling_Center"]
JOB = ["Jobs"]
ECO = []

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

    # calculate travel time reduction only in After condition
    if is_after:
        for item in types:
            if item == "Jobs": 
                print("For type Jobs IPR")
            else:
                # run metric comparison

                # paths for number of key destinations
                dest_threshold_before_csv_path = os.path.join(metric_out_folder, "dest_within_threshold_"+str(threshold)+"_"+item+"_baseline.csv")
                dest_threshold_after_csv_path = os.path.join(metric_out_folder, "dest_within_threshold_"+str(threshold)+"_"+item+"_after.csv")
                
                # paths for travel time n_closest key destination
                n_closest_before_csv_path = os.path.join(metric_out_folder, str(n_closest)+"th_closest_travel_time_"+item+"_baseline.csv")
                n_closest_after_csv_path = os.path.join(metric_out_folder, str(n_closest)+"th_closest_travel_time_"+item+"_after.csv")

                ctuid_reference_path = os.path.join(PROJECT_ROOT, "data", "results/CTUIDs.csv")
                ct_to_neighbourhood = os.path.join(PROJECT_ROOT, "data/visual_data/CTUID-w-Neighborhood.csv")
                
                calculate_num_key_dest_diff(dest_threshold_before_csv_path, dest_threshold_after_csv_path, ctuid_reference_path, ct_to_neighbourhood, item, threshold=threshold)
                calculate_key_dest_trave_time_red(n_closest_before_csv_path, n_closest_after_csv_path, ctuid_reference_path, ct_to_neighbourhood, item, n_closest=n_closest)


def calculate_num_key_dest_diff(before_csv_path, after_csv_path, CTUID_source, neighbourhood_source, item, threshold=30):
    total_destinations_df = pd.read_csv(CTUID_source)
    area_names_df = pd.read_csv(neighbourhood_source)

    # Add Neighbourhood Data
    total_destinations_df = MetricCalculation.add_column_with_join(
        total_destinations_df,
        area_names_df,
        base_ctuid_col='CTUID',
        join_ctuid_col='CTUID',
        join_column_name='AREA_NAME',
        new_column_name='Neighbourhood'
    )

    before_column_names = {'from_id': 'from_id','to_id': 'to_id', 'CTUID':'CTUID',
        'total_column': f'total_destinations_within_{threshold}_mins_before'}
    
    total_destinations_df = MetricCalculation.add_column_with_join(
    total_destinations_df,
    MetricCalculation.calculate_total_destinations(before_csv_path, CTUID_source, before_column_names),
    base_ctuid_col='CTUID',
    join_ctuid_col='CTUID',
    join_column_name=f'total_destinations_within_{threshold}_mins_before',
    new_column_name=f'total_destinations_within_{threshold}_mins_before'
    )
    # display(total_destinations_df.head(20))
    after_column_names = {'from_id': 'from_id','to_id': 'to_id', 'CTUID':'CTUID',
            'total_column': f'total_destinations_within_{threshold}_mins_after'}

    # Add 'after' totals
    total_destinations_df = MetricCalculation.add_column_with_join(
        total_destinations_df,
        MetricCalculation.calculate_total_destinations(after_csv_path, CTUID_source, after_column_names),
        base_ctuid_col='CTUID',
        join_ctuid_col='CTUID',
        join_column_name=f'total_destinations_within_{threshold}_mins_after',
        new_column_name=f'total_destinations_within_{threshold}_mins_after'
    )

    # Calculate Difference
    total_destinations_df[f'total_destinations_within_{threshold}_mins_diff'] = (
        total_destinations_df[f'total_destinations_within_{threshold}_mins_after'] - 
        total_destinations_df[f'total_destinations_within_{threshold}_mins_before']
    )

    # Save the final DataFrame to CSV
    # csv_output_path = f'../results/hospitals_{threshold}_before_after_diff.csv'
    # [NINA][!!!!!][JAN/FEB IMPROVEMENT] DATA SAVE DESTINATION RESTRUCTURE
    csv_output_path = os.path.join(PROJECT_ROOT, "data/results/metrics", "COMBINE_num_dest_within_threshold_"+str(threshold)+"_"+item+".csv")
    total_destinations_df.to_csv(csv_output_path, index=False)

    # pivoted results for POWERBI
    pivoted_output_path = os.path.join(PROJECT_ROOT, "data/results/metrics", "PIVOTED_num_dest_within_threshold_"+str(threshold)+"_"+item+".csv")
    MetricCalculation.pivot_totals_to_rows(csv_output_path, pivoted_output_path)
    temp_reformat_cols(pivoted_output_path, item)

# calculate travel time reduction
# [NINA][JAN/FEB IMPROVEMENT]: combine with the previous function if possible
def calculate_key_dest_trave_time_red(before_csv_path, after_csv_path, CTUID_source, neighbourhood_source, item, n_closest=1):
    total_destinations_df = pd.read_csv(CTUID_source)
    area_names_df = pd.read_csv(neighbourhood_source)

    before_csv = pd.read_csv(before_csv_path)
    after_csv = pd.read_csv(after_csv_path)

    # Add Neighbourhood data
    total_destinations_df = MetricCalculation.add_column_with_join(
        total_destinations_df,
        area_names_df,
        base_ctuid_col='CTUID',
        join_ctuid_col='CTUID',
        join_column_name='AREA_NAME',
        new_column_name='Neighbourhood'
    )
    # # display(total_destinations_df.head(20))
    # before_column_names = {'from_id': 'from_id','to_id': 'to_id', 'CTUID':'CTUID',
    #         'total_column': f'travel_time_to_first_dest_before'}

    total_destinations_df = MetricCalculation.add_column_with_join(
        total_destinations_df,
        before_csv,
        base_ctuid_col='CTUID',
        join_ctuid_col='from_id',
        join_column_name=f'travel_time',
        new_column_name=f'travel_time_to_first_dest_before'
    )
    # display(total_destinations_df.head(20))
    # after_column_names = {'from_id': 'from_id','to_id': 'to_id', 'CTUID':'CTUID',
    #         'total_column': f'travel_time_to_first_dest_after'}

    # Add 'after' totals
    total_destinations_df = MetricCalculation.add_column_with_join(
        total_destinations_df,
        after_csv,
        base_ctuid_col='CTUID',
        join_ctuid_col='from_id',
        join_column_name=f'travel_time',
        new_column_name=f'travel_time_to_first_dest_after'
    )

    # Calculate Difference
    total_destinations_df[f'travel_time_to_first_dest_reduction'] = (
        abs(total_destinations_df[f'travel_time_to_first_dest_after'] - 
        total_destinations_df[f'travel_time_to_first_dest_before'])
    )

    # Save the final DataFrame to CSV
    # csv_output_path = f'../results/first_hospitals_before_after_reduction.csv'
    # [NINA][!!!!!][JAN/FEB IMPROVEMENT] DATA SAVE DESTINATION RESTRUCTURE
    csv_output_path = os.path.join(PROJECT_ROOT, "data/results/metrics", "COMBINE_travel_time_reduction_"+str(n_closest)+"th_"+item+".csv")
    total_destinations_df.to_csv(csv_output_path, index=False)

    # pivoted results for POWERBI
    pivoted_output_path = os.path.join(PROJECT_ROOT, "data/results/metrics", "PIVOTED_travel_time_reduction_"+str(n_closest)+"th_"+item+".csv")
    MetricCalculation.pivot_totals_to_rows(csv_output_path, pivoted_output_path)
    temp_reformat_cols(pivoted_output_path, item)

# [NINA][!!!!!][JAN/FEB IMPROVEMENT]: add column for metric, metric type, category, before_after_diff, need to be inserted into pivot function
# metric type: the metric types: [Social, Economic, Environmental]
# metric name: {Social: [num_dest_within_threshold_mins, n_th_dest_travel_time_reduction], Economic: [num_dest_within_threshold_mins]}
# category: {Social: [Hospitals, Schools, Libraries, Cooling_Center], Economic: [Job Categories]}
# before_after_diff: [before, after, difference]

def temp_reformat_cols(path, item):
    pivoted_df = pd.read_csv(path)

    pivoted_df["Metric_Type"] = "Social"
    pivoted_df["Category"]  = item
    pivoted_df["Metric_Name"] = pivoted_df["Before_After_Difference"].transform(lambda x: x.rsplit('_', 1)[0])
    pivoted_df["Before_After_Benefit"] = pivoted_df["Before_After_Difference"].transform(lambda x: x.rsplit('_', 1)[-1])
    
    reorder_col = ['CTUID','Neighbourhood','Metric_Type','Metric_Name','Category','Before_After_Benefit', 'Value']
    pivoted_df = pivoted_df[reorder_col]
    pivoted_df.to_csv(path, index=False)
    # cols ['CTUID','Neighbourhood','Metric_Type','Metric_Name','Category','Before_After_Benefit', 'Value']
      


run_travel_time(OSM = OSM_PATH, GTFS = OLD_GTFS_PATH, types = RUN_TRAVEL_TIME_TYPES, is_after = False)
run_metrics_calculation(travel_time_out_folder = os.path.join(PROJECT_ROOT, "data/results/travel_time_matrix"), threshold = 30, n_closest =1, is_after = False, types = RUN_TRAVEL_TIME_TYPES)
run_travel_time(OSM = OSM_PATH, GTFS = NEW_GTFS_PATH, types = RUN_TRAVEL_TIME_TYPES, is_after = True)
run_metrics_calculation(travel_time_out_folder = os.path.join(PROJECT_ROOT, "data/results/travel_time_matrix"), threshold = 30, n_closest =1, is_after = True, types = RUN_TRAVEL_TIME_TYPES)


