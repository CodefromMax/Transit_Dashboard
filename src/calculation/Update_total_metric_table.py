import os
import sys
import pandas as pd
PROJECT_ROOT = "/Users/max/Desktop/Transit_Dashboard"
sys.path.append(PROJECT_ROOT)
from src.calculation.Calculation_Pipeline import CalculationPipeline
from src.calculation.Metric_Calculation.MetricCalculation import MetricCalculation

def process_job_accessibility():
    import pandas as pd

    def calculate_job_accessibility(travel_time_matrix_path, thresholds, employment_data_path, ctuid_reference_path, output_path):
        # Initialize Metric Calculation
        Job_Metric = MetricCalculation(travel_time_matrix_path)

        # Calculate job accessibility
        Job_Metric.calculate_accessible_jobs(thresholds, employment_data_path, ctuid_reference_path, output_path)

    def process_job_access_file(job_access_file, neighbourhood_path, threshold):
        # Load the neighbourhood mapping
        neighbourhood_df = pd.read_csv(neighbourhood_path)
        neighbourhood_df['CTUID'] = neighbourhood_df['CTUID'].apply(lambda x: f"{float(x):.2f}")

        # Process the job access dataset
        job_access_df = pd.read_csv(job_access_file)
        job_access_df['CTUID'] = job_access_df['CTUID'].apply(lambda x: f"{float(x):.2f}")
        if 'Neighbourhood' not in job_access_df.columns:
            job_access_df = job_access_df.merge(neighbourhood_df, on='CTUID', how='left')
            job_access_df.rename(columns={'AREA_NAME': 'Neighbourhood'}, inplace=True)

        return pd.DataFrame([
            {
                "CTUID": row['CTUID'],
                "Neighbourhoods": row['Neighbourhood'],
                "Metric_Type": "Economic",
                "Metric_Name": "Job Access",
                "Travel_Time_Threshold": threshold,
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

    # Define file paths and thresholds
    PROJECT_ROOT = "/Users/max/Desktop/Transit_Dashboard"
    neighbourhood_path = os.path.join(PROJECT_ROOT, "data/visual_data/CTUID-w-Neighborhood.csv")
    update_path = os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Update_Commute_total.csv")

    before_after_paths = [
        (os.path.join(PROJECT_ROOT,"data/results/travel_time/Jobs_baseline.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_45.csv"), [45]),
        (os.path.join(PROJECT_ROOT,"data/results/travel_time/Jobs_after.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_After_45.csv"), [45]),
        (os.path.join(PROJECT_ROOT,"data/results/travel_time/Jobs_baseline.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_60.csv"), [60]),
        (os.path.join(PROJECT_ROOT,"data/results/travel_time/Jobs_after.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_After_60.csv"), [60]),
        (os.path.join(PROJECT_ROOT,"data/results/travel_time/Jobs_baseline.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_15.csv"), [15]),
        (os.path.join(PROJECT_ROOT,"data/results/travel_time/Jobs_after.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_After_15.csv"), [15])
    ]

    combined_paths = [
        (os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_45.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_After_45.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_After_Diff_45.csv")),
        (os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_60.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_After_60.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_After_Diff_60.csv")),
        (os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_15.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_After_15.csv"), os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_After_Diff_15.csv"))
    ]

    # Perform before/after calculations
    for travel_time_matrix_path, output_path, thresholds in before_after_paths:
        calculate_job_accessibility(travel_time_matrix_path, thresholds, "/Users/max/Desktop/Transit_Dashboard/draft/Employment_data.csv", os.path.join(PROJECT_ROOT,"src/calculation/results/CTUIDs.csv"), output_path)

    # Combine before/after files
    for job_before_path, job_after_path, combined_job_output_path in combined_paths:
        MetricCalculation.combine_job_access_before_after(job_before_path, job_after_path, combined_job_output_path)

    # Process job access datasets
    job_access_file_45 = os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_After_Diff_45.csv")
    job_access_file_60 = os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_After_Diff_60.csv")
    job_access_file_15 = os.path.join(PROJECT_ROOT,"data/results/CT_job_access_Before_After_Diff_15.csv")

    job_access_transformed_45 = process_job_access_file(job_access_file_45, neighbourhood_path, 45)
    job_access_transformed_60 = process_job_access_file(job_access_file_60, neighbourhood_path, 60)
    job_access_transformed_15 = process_job_access_file(job_access_file_15, neighbourhood_path, 15)

    # Load and combine all datasets
    total_df = pd.read_csv(update_path)
    total_df['CTUID'] = total_df['CTUID'].apply(lambda x: f"{float(x):.2f}")

    combined_df = pd.concat([
        total_df,
        job_access_transformed_45,
        job_access_transformed_60,
        job_access_transformed_15,
    ], ignore_index=True)
    
    updated_path = os.path.join(PROJECT_ROOT,"data/results/metrics/total_Metric_Table_Ontario_Line_Updated.csv")

    # Save the combined table
    combined_df.to_csv(updated_path, index=False)
    print(f"Combined metrics table saved to {update_path}")



