"""
Pipeline for Running Travel Time Calculation + Metric Calculation (before and after)
Cleaned and reorganized from calculate.py
"""
import pandas as pd
import os
import sys

# [!!!!!] make sure ends with /Transit_Dashboard -> project root
PROJECT_ROOT = "/Users/max/Desktop/Transit_Dashboard"
# os.path.abspath(os.path.join('../..')) 
sys.path.append(PROJECT_ROOT)
print(PROJECT_ROOT)

# import calculation paths
from src.calculation.travel_time_matrix.TravelTimeCalculation import TravelTimeCalculation
from src.calculation.Metric_Calculation.MetricCalculation import MetricCalculation

# path to data
# TODO [!!!!!]: move CTUID_Reference to /data/visual_data or /data/census_tract_data
DATA_PATH = {
    "OSM": "/Users/max/Desktop/Transit_Dashboard/data/OSM_data/Toronto.osm.pbf", 
    # os.path.join(PROJECT_ROOT, "data/OSM_data/Toronto.osm.pbf"),
    "Employment_Data": os.path.join(PROJECT_ROOT, "draft/Employment_data.csv"),
    "Key_Destination_Data": os.path.join(PROJECT_ROOT, "data/key_destination_data"),
    "CT_Centroid": os.path.join(PROJECT_ROOT, "data/census_tract_data/toronto_ct_centroids1.geojson"),
    "CTUID_Reference": os.path.join(PROJECT_ROOT, "src/calculation/results/CTUIDs.csv"),
    "CT_to_Neighbourhood": os.path.join(PROJECT_ROOT, "data/visual_data/CTUID-w-Neighborhood.csv")
}

# Metric Types: 
METRICS = ["Social", "Economic", "Environmental"]
CATEGORY = {
    "Social": ["Hospitals", "Schools", "Libraries", "Cooling_Center"],
    "Economic": ["Jobs"],
    "Environmental": ["CO2"]
}

# GTFS PATH
NEW_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip") 
BASELINE_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip") 


class CalculationPipeline():
    def __init__(self, GTFS_PATH, is_after, name):
        """
        Initialize Object CalculationPipeline
        -------------------------------------
        Parameters: 
        - GTFS_PATH: path to the GTFS data to build network for travel time reduction
        - is_after: determine if the calculation is for before or after
            - is_after = False: run the calculation for the baseline
            - is_after = True: run the calculation for the new line and run 
        - name: name of the line to be created (as the folder name to save intermediate calculations and final results)
        """
        self.GTFS_PATH = GTFS_PATH
        self.is_after = is_after

        if is_after:
            self.out_suffix = "_after"
        else:
            self.out_suffix = "_baseline"

        # create folder under /data/results with name of the new line
        self.line_root = os.path.join(PROJECT_ROOT, "data", "results")
        self.travel_time_path = os.path.join(self.line_root, "travel_time")
        self.metric_path = os.path.join(self.line_root, "metrics")
        if not os.path.exists(self.line_root):
            os.makedirs(self.line_root)
            os.makedirs(self.travel_time_path)
            os.makedirs(self.metric_path)
        else:
            fn = self.line_root.split("/")[-1] # the name
            # Terminate the runtime if the file already exists
            # TODO: need to integrate this with frontend display
            print("[WARNING]: THIS FILE NAME ALREADY EXISTS, CONTINUE RUNNING WILL OVERWRITE THE PREVIOUS VERSION")
            # sys.exit()


    def travel_time_calculation(self):
        """
        Calculate the travel time matrix
            - Travel time Calculation for key_destinations (ct-location) and jobs (ct-ct)
        """
        # initialize travel time calculator object and build transportation network based on gtfs data
        TTCalculator = TravelTimeCalculation(DATA_PATH['OSM'], self.GTFS_PATH)
        TTCalculator.build_transport_network()

        for metric in METRICS:
            # for environmental metric, no travel time calculation. 
            if metric == "Environmental":
                continue

            for category in CATEGORY[metric]:
                origins_path = DATA_PATH["CT_Centroid"]
                output_path = os.path.join(self.travel_time_path, category+self.out_suffix+".csv")

                if category== "Jobs":
                    # for economic metric, travel time calculated for census tract
                    destinations_path = DATA_PATH["CT_Centroid"]
                    destination_id_col = 'CTUID'
                
                else:
                    destinations_path = os.path.join(DATA_PATH["Key_Destination_Data"], category + "_4326.geojson")
                    destination_id_col = 'Address_ID'
                                    
                TTCalculator.compute_travel_time_matrix(
                    origins_path = origins_path, 
                    destinations_path = destinations_path, 
                    output_path = output_path, 
                    origin_id_col = 'CTUID', destination_id_col = destination_id_col,
                    origin_is_point = True, destination_is_point = True,  # If it is not a point, the centroid of the polygon will be used
                )

        print("[DEBUG]: TRAVEL TIME CALCULATION COMPLETED")

    """
    [NINA][!!!!!]
    TODO: Redundancy in data aggregation, reading from multiple files multiple times to complete the final calculation
    - [Improvement] After calculation, aggregate to final usuable format
    - [Improvement] if calculate for the new line, combine baseline and after table, then calculate the difference
    - [Improvement] Changes need to be made in MetricCalculation class (pivote function will probably be the easiest fix)
    - [Improvement] case by case hard coding, need to have method that are scalable to address all (at least majority) cases
        - when calculating "Difference" for before and after scenario
    - [Imporvement] Validate that before files exists before running metric calculation
    -------------------------------------------------------------------------------------------------------------
    - [Metric][!!!!!] Current calculation only supports travel time to "first key destination" ONLY
        - Need to make it able to run for ANY key destination (n-th)
    """            

    def run_metric_calculation(self, threshold, n_closest):
        """
        Caculate the metrics
        """
        for metric in METRICS:
            if metric == "Environmental":
                continue

            for category in CATEGORY[metric]:
                travel_time_matrix_path = os.path.join(self.travel_time_path, category+self.out_suffix+".csv")
                MetricCalculator = MetricCalculation(travel_time_matrix_path=travel_time_matrix_path)
                # job metrics
                if category == "Jobs":
                    # TODO: [NINA]: check if the caculcate accessible works
                    print("[DEBUG]: In Metric Calculation category Jobs")
                    output_job_accessible = os.path.join(self.metric_path, "dest_within_"+str(threshold)+"_minutes_"+category+self.out_suffix+".csv")
                    print("[DEBUG]:MetricCalculator.calculate_accessible_jobs")
                    MetricCalculator.calculate_accessible_jobs(thresholds=threshold, employment_data_path=DATA_PATH["Employment_Data"], 
                                                               ctuid_reference_path=DATA_PATH['CTUID_Reference'], output_path=output_job_accessible)
                    print("[DEBUG]:MetricCalculator.calculate_accessible_jobs COMPLETED")
                    if self.is_after:

                        # num jobs accessible metric
                        job_access_baseline = os.path.join(self.metric_path, "dest_within_"+str(threshold)+"_minutes_"+category+"_baseline.csv")
                        output_combined_job_access = os.path.join(self.metric_path, "CT_job_access_Before_After_Diff_Ontario.csv") # [!] Job Access output path
                        MetricCalculation.combine_job_access_before_after(job_access_baseline, output_job_accessible, output_combined_job_access)
                        print("[DEBUG]: Economic - job access COMPLETED")
                        
                        # calculate for commute time reduction
                        before_path = os.path.join(self.travel_time_path, "Jobs_baseline.csv")
                        after_path = os.path.join(self.travel_time_path, "Jobs_after.csv")
                        
                        commute_time_thresholds = [(0, 15), (15, 30), (30, 45), (45, 60)]
                        MetricCalculation.calculate_commute_time_reduction(
                            before_matrix_path=before_path,
                            after_matrix_path=after_path,
                            thresholds=commute_time_thresholds,
                            category="job",
                            output_path=os.path.join(self.metric_path, "commute_time_results_total.csv")
                        )

                        print("[DEBUG]: Economic - commute time reduction COMPLETED")

    
                # Social (key destination) metrics
                else: 
                    # Social metric has three sub metrics
                    # num_dest, travel time to n-th closest key destination will be calculated here
                    # sub metric number of people accessible will handled in the visualization frontend
                    output_num_dest = os.path.join(self.metric_path, "dest_within_"+str(threshold)+"_minutes_"+category+self.out_suffix+".csv")
                    output_n_th_closest = os.path.join(self.metric_path, "travel_time_to_"+str(n_closest)+"_th_closest_"+category+self.out_suffix+".csv")
                    MetricCalculator.filter_destinations(output_path = output_num_dest, threshold = threshold)
                    MetricCalculator.get_nth_travel_time(n = n_closest, output_path = output_n_th_closest)

                    if self.is_after:
                        # num_dest_baseline = os.path.join(self.metric_path, "dest_within_"+str(threshold)+"_minutes_"+category+"_baseline.csv")
                        # [add_column_with_join] base_df, join_df, base_ctuid_col, join_ctuid_col, join_column_name, new_column name
                        dest_threshold_before_csv_path = os.path.join(self.metric_path,  "dest_within_"+str(threshold)+"_minutes_"+category+"_baseline.csv")
                        dest_threshold_after_csv_path = os.path.join(self.metric_path,  "dest_within_"+str(threshold)+"_minutes_"+category+"_after.csv")
                        
                        # paths for travel time n_closest key destination
                        n_closest_before_csv_path = os.path.join(self.metric_path, "travel_time_to_"+str(n_closest)+"_th_closest_"+category+"_baseline.csv")
                        n_closest_after_csv_path = os.path.join(self.metric_path, "travel_time_to_"+str(n_closest)+"_th_closest_"+category+"_after.csv")
                        
                        print("[DEBUG]: calculate_num_key_dest_diff threshold: ", threshold)
                        self.calculate_num_key_dest_diff(dest_threshold_before_csv_path, dest_threshold_after_csv_path, 
                                                         DATA_PATH["CTUID_Reference"], DATA_PATH["CT_to_Neighbourhood"], 
                                                         category, threshold)
                        print("[DEBUG]: Social - number of key destination accessible COMPLETED")

                        
                        self.calculate_key_dest_trave_time_red(n_closest_before_csv_path, n_closest_after_csv_path, 
                                                               DATA_PATH["CTUID_Reference"], DATA_PATH["CT_to_Neighbourhood"], 
                                                               category, n_closest=n_closest)
                        print("[DEBUG]: Social - travel time reduction to first key destination COMPLETED")
        
        if self.is_after:
            # combine all metric files 
            self.combine_metrics_tables()
            print("[DEBUG]: combine all metric files (except for job ) COMPLETED")
            self.reformat_job_access()
            print("[DEBUG]: ALL METRICS COMPLETED AND SAVED TO DESTINATION")




    def calculate_num_key_dest_diff(self, before_csv_path, after_csv_path, CTUID_source, neighbourhood_source, 
                                    item, threshold):
        print("[DEBUG]: In calculate_num_key_dest_diff")
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
        # temp_reformat_cols(pivoted_output_path, item)

    # calculate travel time reduction
    # [NINA][JAN/FEB IMPROVEMENT]: combine with the previous function if possible
    def calculate_key_dest_trave_time_red(self, before_csv_path, after_csv_path, CTUID_source, neighbourhood_source, item, n_closest=1):
        print("[DEBUG]: In calculate_key_dest_trave_time_red")
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
        # temp_reformat_cols(pivoted_output_path, item)

    # TODO [!!!!!]: hard coded, need to be fixed              
    def combine_metrics_tables(self):
        """
        Combines multiple metric tables into one unified table.

        Args:
            hospital_dest_file (str): Path to the hospital destinations file.
            pivoted_file (str): Path to the pivoted travel time reduction file.
            library_file (str): Path to the library file.
            cooling_file (str): Path to the cooling center file.
            job_access_file (str): Path to the job access file.
            neighbourhood_file (str): Path to the CTUID-Neighbourhood mapping file.
            output_path (str): Path to save the combined table.
        """

        hospital_dest_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_num_dest_within_threshold_30_Hospitals.csv")
        cooling_dest_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_num_dest_within_threshold_30_Cooling_Center.csv")
        school_dest_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_num_dest_within_threshold_30_Schools.csv")
        library_dest_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_num_dest_within_threshold_30_Libraries.csv")
        hospital_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_travel_time_reduction_1th_Hospitals.csv")
        school_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_travel_time_reduction_1th_Schools.csv")
        library_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_travel_time_reduction_1th_Libraries.csv")
        cooling_file = os.path.join(PROJECT_ROOT, "data/results/metrics/PIVOTED_travel_time_reduction_1th_Cooling_Center.csv")

        job_access_file = os.path.join(self.metric_path, "CT_job_access_Before_After_Diff_Ontario.csv")
        neighbourhood_file = "/Users/max/Desktop/Transit_Dashboard/data/visual_data/CTUID-w-Neighborhood.csv"
        output_path = os.path.join(self.metric_path, "total_Metric_Table_Ontario_Line_Update.csv")
        # Load the neighbourhood mapping
        neighbourhood_df = pd.read_csv(neighbourhood_file)
        neighbourhood_df['CTUID'] = neighbourhood_df['CTUID'].apply(lambda x: f"{float(x):.2f}")

        # Function to process individual datasets
        def process_dataset(file_path, metric_name, category):
            df = pd.read_csv(file_path)
            df['CTUID'] = df['CTUID'].apply(lambda x: f"{float(x):.2f}")
            if 'Neighbourhood' not in df.columns:
                df = df.merge(neighbourhood_df, on='CTUID', how='left')
                df.rename(columns={'AREA_NAME': 'Neighbourhood'}, inplace=True)
            return pd.DataFrame([
                {
                    "CTUID": row['CTUID'],
                    "Neighbourhoods": row['Neighbourhood'],
                    "Metric_Type": "Social",
                    "Metric_Name": metric_name,
                    "Travel_Time_Threshold": 30,
                    "Category": category,
                    "Before_After_Benefit": (
                        "before" if row['Before_After_Difference'].split('_')[-1] == "before" else
                        "after" if row['Before_After_Difference'].split('_')[-1] == "after" else
                        "benefit"
                    ),
                    "Value": row['Value']
                }
                for _, row in df.iterrows()
            ])
        # Function to process individual datasets
        def process_dataset2(file_path, metric_name, category):
            df = pd.read_csv(file_path)
            df['CTUID'] = df['CTUID'].apply(lambda x: f"{float(x):.2f}")
            if 'Neighbourhood' not in df.columns:
                df = df.merge(neighbourhood_df, on='CTUID', how='left')
                df.rename(columns={'AREA_NAME': 'Neighbourhood'}, inplace=True)
            return pd.DataFrame([
                {
                    "CTUID": row['CTUID'],
                    "Neighbourhoods": row['Neighbourhood'],
                    "Metric_Type": "Social",
                    "Metric_Name": metric_name,
                    "Travel_Time_Threshold": row['Value'],
                    "Category": category,
                    "Before_After_Benefit": (
                        "before" if row['Before_After_Difference'].split('_')[-1] == "before" else
                        "after" if row['Before_After_Difference'].split('_')[-1] == "after" else
                        "benefit"
                    ),
                    "Value": row['Value']
                }
                for _, row in df.iterrows()
            ])

        # Process each dataset
        hospital_dest_transformed = process_dataset(hospital_dest_file, "Number of Destinations Accessible", "Hospital")
        cooling_dest_transformed = process_dataset(cooling_dest_file, "Number of Destinations Accessible", "Cooling Centre")
        school_dest_transformed = process_dataset(school_dest_file, "Number of Destinations Accessible", "School")
        library_dest_transformed = process_dataset(library_dest_file, "Number of Destinations Accessible", "Library")

        hospital_transformed = process_dataset2(hospital_file, "Travel Time to First Destination", "Hospital")
        cooling_transformed = process_dataset2(cooling_file, "Travel Time to First Destination", "Cooling Centre")
        school_transformed = process_dataset2(school_file, "Travel Time to First Destination", "School")
        library_transformed = process_dataset2(library_file, "Travel Time to First Destination", "Library")
        
        # Process the job access dataset
        job_access_df = pd.read_csv(job_access_file)
        job_access_df['CTUID'] = job_access_df['CTUID'].apply(lambda x: f"{float(x):.2f}")
        if 'Neighbourhood' not in job_access_df.columns:
            job_access_df = job_access_df.merge(neighbourhood_df, on='CTUID', how='left')
            job_access_df.rename(columns={'AREA_NAME': 'Neighbourhood'}, inplace=True)
        job_access_transformed = pd.DataFrame([
            {
                "CTUID": row['CTUID'],
                "Neighbourhoods": row['Neighbourhood'],
                "Metric_Type": "Economic",
                "Metric_Name": "Job Access",
                "Travel_Time_Threshold": 30,
                "Category": row['Job_type'],
                "Before_After_Benefit": (
                    "before" if row['Time'].lower() == "before" else
                    "after" if row['Time'].lower() == "after" else
                    "benefit"
                ),
                
                "Value": row['Num_jobs']
            }
            for _, row in job_access_df.iterrows()
        ])

        # Combine all datasets
        combined_df = pd.concat([
            hospital_dest_transformed,
            cooling_dest_transformed,
            school_dest_transformed,
            library_dest_transformed,
            hospital_transformed,
            library_transformed,
            cooling_transformed,
            school_transformed,
            job_access_transformed
        ], ignore_index=True)

        # Save the combined table
        combined_df.to_csv(output_path, index=False)
        print(f"Combined metrics table saved to {output_path}")
    
    def reformat_job_access(self):
        neighbourhood_path = "/Users/max/Desktop/Transit_Dashboard/data/visual_data/CTUID-w-Neighborhood.csv"
        neighbourhood_df = pd.read_csv(neighbourhood_path)
        neighbourhood_df['CTUID'] = neighbourhood_df['CTUID'].apply(lambda x: f"{float(x):.2f}")

        job_commute_file = os.path.join(self.metric_path, "commute_time_results_total.csv")
        job_commute_df = pd.read_csv(job_commute_file)
        job_commute_df['CTUID'] = job_commute_df['CTUID'].apply(lambda x: f"{float(x):.2f}")
        if 'Neighbourhood' not in job_commute_df.columns:
            job_commute_df = job_commute_df.merge(neighbourhood_df, on='CTUID', how='left')
            job_commute_df.rename(columns={'AREA_NAME': 'Neighbourhood'}, inplace=True)
        job_commute_transformed = pd.DataFrame([
            {
                "CTUID": row['CTUID'],
                "Neighbourhoods": row['Neighbourhood'],
                "Metric_Type": "Economic",
                "Metric_Name": "Job Commute Time",
                "Travel_Time_Threshold": row["Travel_Time_Threshold"],
                "Category": row['Category'],
                "Before_After_Benefit": (
                    "before" if row['Before_After_Benefit'].lower() == "before" else
                    "after" if row['Before_After_Benefit'].lower() == "after" else
                    "benefit"
                ),
                
                "Value": (row['Average Value'] if row['Before_After_Benefit'].lower() == "before" else
                        row['Average Value'] if row['Before_After_Benefit'].lower() == "after" else
                        row['Total Value'])
                
            }
            for _, row in job_commute_df.iterrows()
        ])

        total_metric = os.path.join(self.metric_path, "total_Metric_Table_Ontario_Line_Update.csv")
        total_metric_df = pd.read_csv(total_metric)
        total_metric_df["CTUID"] = total_metric_df["CTUID"].apply(lambda x: f"{float(x):.2f}")

        # Combine all datasets
        combined_df = pd.concat([
            total_metric_df,
            job_commute_transformed
        ], ignore_index=True)
        update = os.path.join(self.metric_path, "total_Metric_Table_Ontario_Line_Update_Commute_total.csv")
        # Save the combined table
        combined_df.to_csv(update, index=False)
        print(f"Combined metrics table saved to {update}")





                    



