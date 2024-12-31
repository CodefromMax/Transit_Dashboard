import os
import sys
PROJECT_ROOT = "/Users/max/Desktop/Transit_Dashboard"
sys.path.append(PROJECT_ROOT)
from src.calculation.Calculation_Pipeline import CalculationPipeline
from src.calculation.Update_total_metric_table import process_job_accessibility

BASELINE_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip") 
# TODO: make sure to change to new gtfs path
NEW_GTFS_PATH = "/Users/max/Desktop/Transit_Dashboard/data/GTFS_data/gtfs_output_v10.zip" 

# calculate before scenario
before_calculator = CalculationPipeline(GTFS_PATH=BASELINE_GTFS_PATH, is_after=False,name = "Before")
before_calculator.travel_time_calculation()
before_calculator.run_metric_calculation(30,1)

# calculate after scenario
after_calculator = CalculationPipeline(GTFS_PATH=NEW_GTFS_PATH, is_after=True, name = "After")
after_calculator.travel_time_calculation()
after_calculator.run_metric_calculation(threshold=30,n_closest = 1)

# update total metric table
process_job_accessibility()