import pandas as pd

# Path to the CSV file
file_path = '/Users/max/Desktop/Transit_Dashboard/data/results/metrics/total_Metric_Table_Ontario_Line_Updated1.csv'

# Load the CSV file
df = pd.read_csv(file_path)

# # Filter rows where Metric_Name equals "Job Commute Time"
# job_commute_time_rows = df['Metric_Name'] == 'Job Commute Time'
# # Ensure Travel_Time_Threshold is treated as string for manipulation
# df['Travel_Time_Threshold'] = df['Travel_Time_Threshold'].astype(str)
# # Update the Travel_Time_Threshold column for these rows
# df.loc[job_commute_time_rows, 'Travel_Time_Threshold'] = (
#     df.loc[job_commute_time_rows, 'Travel_Time_Threshold']
#     .str.split()
#     .str[-1]
# )
df['CTUID'] = df['CTUID'].apply(lambda x: f"{float(x):.2f}")
# # Save the updated DataFrame back to the file (if needed)
df.to_csv(file_path, index=False)