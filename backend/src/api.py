from calculation.Calculation_Pipeline import CalculationPipeline
from calculation.Update_total_metric_table import process_job_accessibility
from flask import Flask, jsonify, request
import traceback
from helper.find_project_root import find_project_root
import os
from gtfs_manager import GTFSManager, OUTPUT_DIR, zip_output_folder

app = Flask(__name__)

PROJECT_ROOT = find_project_root("Transit_Dashboard")
NEW_GTFS_PATH =  os.path.join(PROJECT_ROOT, "backend/src/gtfs_output.zip")
# Flask routes
@app.route("/append-gtfs", methods=["POST"])
def append_gtfs_endpoint():
    """API endpoint to append GTFS data."""
    try:
        if not request.json:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        gtfs_manager = GTFSManager()
        result = gtfs_manager.process_new_data(request.json)
        zip_output_folder(OUTPUT_DIR, "gtfs_output")
        #generate_metric_table()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": traceback.format_exc()}), 500

@app.route("/generate-metric-table", methods=["GET"])
def generate_metric_table():
    # Your metric table generation logic
    try:
        # calculate after scenario
        # print("Current working directory:", os.getcwd())
        # print("Project Root:", PROJECT_ROOT)  # Add your actual variable name
        # print("GTFS file path:", NEW_GTFS_PATH)
        print("Creating Calculation Pipeline")
        after_calculator = CalculationPipeline(GTFS_PATH=NEW_GTFS_PATH, is_after=True, name = "After")
        print("Calculating Travel Time")
        after_calculator.travel_time_calculation()
        print("Running Metric Calculation")
        after_calculator.run_metric_calculation(threshold=30,n_closest = 1)

        # update total metric table
        process_job_accessibility()


        return "Updated Metric Table"
    except Exception as e:
        error_message = traceback.format_exc()
        return jsonify({"error": error_message}), 500
    
if __name__ == "__main__":
    app.run(port=4000, debug=True)
