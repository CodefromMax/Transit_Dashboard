import os
import sys
import pandas as pd

PROJECT_ROOT = "/Users/max/Desktop/Transit_Dashboard"
sys.path.append(PROJECT_ROOT)
from src.calculation.Calculation_Pipeline import CalculationPipeline
from src.calculation.Update_total_metric_table import process_job_accessibility

BASELINE_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip") 
# # TODO: make sure to change to new gtfs path
NEW_GTFS_PATH = "/Users/max/Desktop/Transit_Dashboard/data/GTFS_data/gtfs_output_v10.zip" 

FINAL_OUTPUT_PATH = [os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Update_Commute_total.csv"), 
                     os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Update_Commute_total_15.csv"), 
                     os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Update_Commute_total_45.csv"),
                     os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Update_Commute_total_60.csv")]

travel_time = [30, 15, 45, 60]
# calculate before scenario
before_calculator = CalculationPipeline(GTFS_PATH=BASELINE_GTFS_PATH, is_after=False,name = "Before")
before_calculator.travel_time_calculation()
# calculate after scenario
after_calculator = CalculationPipeline(GTFS_PATH=NEW_GTFS_PATH, is_after=True, name = "After")
after_calculator.travel_time_calculation()

for i in range(4):
    before_calculator.run_metric_calculation(threshold = travel_time[i], n_closest = 1)
    after_calculator.run_metric_calculation(threshold = travel_time[i], n_closest = 1, final_output_path=FINAL_OUTPUT_PATH[i])

# update total metric table
"""
Key Destination:
- dest accessible within 30, [15, 45, 60] - IPR
- travel time reduction to 1st destination
- change in access to specific key destination (PowerBI)

Job Access: 
- job accessible [15, 30, 45, 60]
- commute time reduction

Environmental 
- IPR
"""
process_job_accessibility()

# for adding num dest with different threshold
dest = os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Update_Commute_total_add.csv")
dfTotal = pd.read_csv(dest)

dfs = [dfTotal]

for i in range (1,4):
    df_temp = pd.read_csv(FINAL_OUTPUT_PATH[i])
    df_temp = df_temp[df_temp["Metric_Type"] == "Social"]
    df_temp = df_temp[df_temp["Metric_Name"] == "Number of Destinations Accessible"]
    dfs.append(df_temp)

final_path = os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Update_Commute_total_v1.csv")
result = pd.concat(dfs, ignore_index=True)
result['CTUID'] = result['CTUID'].apply(lambda x: f"{float(x):.2f}")
result.to_csv(final_path, index=False)
