from .Calculation_Pipeline import CalculationPipeline
import os

PROJECT_ROOT = os.path.abspath(os.path.join('../..')) 
BASELINE_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip") 
# TODO: make sure to change to new gtfs path
NEW_GTFS_PATH = os.path.join(PROJECT_ROOT, "data/GTFS_data/raw/latest_feed_version_2024-10-22.zip") 

# calculate before scenario
before_calculator = CalculationPipeline(GTFS_PATH=BASELINE_GTFS_PATH, is_after=False)
before_calculator.travel_time_calculation()
before_calculator.run_metric_calculation()

# calculate after scenario
after_calculator = CalculationPipeline(GTFS_PATH=NEW_GTFS_PATH, is_after=True)
after_calculator.travel_time_calculation()
after_calculator.run_metric_calculation()