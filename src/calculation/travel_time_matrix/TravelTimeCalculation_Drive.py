import os
import time
import datetime
import geopandas as gpd
import pandas as pd
import r5py


class TravelTimeCalculation:
    def __init__(self, osm_path = None, gtfs_path = None):
        """
        Initializes the TravelTimeCalculation class with OSM and GTFS data.
        # Travel time matrix is not a attribute becuase 1 instance can be used to calculate multiple travel time matrices.
        There is only 1 transport network that is built and used to calculate travel time matrices.

        Parameters:
        osm_path (str): Path to the OSM data file.
        gtfs_path (str): Path to the GTFS data file.
        """
        self.osm_path = osm_path
        self.gtfs_path = gtfs_path
        self.transport_network = None

    def build_transport_network(self):
        """
        Builds the transport network using the provided OSM and GTFS data.
        """
        start_time = time.time()
        self.transport_network = r5py.TransportNetwork(self.osm_path, [self.gtfs_path])
        elapsed_time = time.time() - start_time
        print(f"Transport network built in {elapsed_time:.2f} seconds.")

    @staticmethod
    def load_geodata(file_path, is_point=True, id_col="id"):
        """
        Loads and processes geospatial data (origins or destinations).

        Parameters:
        file_path (str): Path to the GeoJSON file.
        is_point (bool): Whether to use the centroids (if False).
        id_col (str): Column name to use as the unique identifier.

        Returns:
        GeoDataFrame: Processed geospatial data.
        """
        data = gpd.read_file(file_path)
        if not is_point:
            data = data.copy()
            data["geometry"] = data.geometry.centroid
        if id_col not in data.columns:
            raise ValueError(f"ID column '{id_col}' not found in the file.")
        data["id"] = data[id_col]
        return data

    def compute_travel_time_matrix(self, origins_path, destinations_path, output_path, 
                                   origin_id_col="id", destination_id_col="id", 
                                   origin_is_point=True, destination_is_point=True, 
                                   departure_time=None):
        """
        Computes the travel time matrix using the transport network.

        Parameters:
        origins_path (str): Path to the origins GeoJSON file.
        destinations_path (str): Path to the destinations GeoJSON file.
        output_path (str): Path to save the resulting travel time matrix.
        origin_id_col (str): Column name for origin IDs.
        destination_id_col (str): Column name for destination IDs.
        origin_is_point (bool): Whether origins are points. If False, centroids are generated for polygons.
        destination_is_point (bool): Whether destinations are points.
        departure_time (datetime, optional): Departure time for the calculation.

        Returns:
        DataFrame: Travel time matrix.
        """
        if not self.transport_network:
            raise ValueError("Transport network not built. Call build_transport_network first.")

        origins = self.load_geodata(origins_path, origin_is_point, origin_id_col)
        destinations = self.load_geodata(destinations_path, destination_is_point, destination_id_col)

        if departure_time is None:
            departure_time = datetime.datetime(2024, 10, 21, 7, 0, 0)

        start_time = time.time()
        travel_time_matrix = r5py.TravelTimeMatrixComputer(
            self.transport_network,
            origins=origins,
            destinations=destinations,
            transport_modes=[r5py.TransportMode.CAR],
            # /TransportMode.CAR
            departure=departure_time,
            departure_time_window=datetime.timedelta(hours=2),
        ).compute_travel_times()
        elapsed_time = time.time() - start_time
        print(f"Travel time matrix computed in {elapsed_time:.2f} seconds.")

        travel_time_matrix.to_csv(output_path, index=False)
        print(f"Travel time matrix saved to {output_path}.")
        return travel_time_matrix
    
    # This method should be added to Metric Calculation class later
    @staticmethod
    def filter_destinations(travel_time_matrix_path, output_path, top_n=None, threshold=None):
        """
        Filters the travel time matrix to find destinations based on top N or threshold.

        Parameters:
        travel_time_matrix_path (str): Path to the travel time matrix CSV file.
        output_path (str): Path to save the filtered results.
        top_n (int, optional): Number of top destinations to include.
        threshold (float, optional): Travel time threshold to include destinations.
        """
        travel_time_matrix = pd.read_csv(travel_time_matrix_path)

        # Filter out rows where from_id == to_id (self-loops)
        data = travel_time_matrix[travel_time_matrix['from_id'] != travel_time_matrix['to_id']]
        
        if isinstance(threshold, list):
            for t in threshold:
                # Filter destinations within the specified travel time threshold
                filtered_destinations = data[data['travel_time'] <= t]
                # Sort the result by 'from_id' and 'travel_time' for clarity
                filtered_destinations = filtered_destinations[['from_id', 'to_id', 'travel_time']].sort_values(['from_id', 'travel_time'])
                # Generate a specific output path for each threshold
                specific_output_path = output_path.replace('.csv', f'_threshold_{t}.csv')
                # Save the result to a CSV file without including the index
                filtered_destinations.to_csv(specific_output_path, index=False)
                print(f"Generated {specific_output_path}")
                
        elif threshold is not None:
            # Filter destinations within the specified travel time threshold
            filtered_destinations = data[data['travel_time'] <= threshold]
            # Sort the result by 'from_id' and 'travel_time' for clarity
            filtered_destinations = filtered_destinations[['from_id', 'to_id', 'travel_time']].sort_values(['from_id', 'travel_time'])
            # Save the result to a CSV file without including the index
            filtered_destinations.to_csv(output_path, index=False)
            print(f"Generated {output_path}")
            
        elif top_n is not None:
            # Sort by travel time, group by 'from_id', and take the top N by travel time
            filtered_destinations = (
                data.sort_values('travel_time')
                .groupby('from_id')
                .head(top_n)
            )
            # Sort the result by 'from_id' and 'travel_time' for clarity
            filtered_destinations = filtered_destinations[['from_id', 'to_id', 'travel_time']].sort_values(['from_id', 'travel_time'])
            # Save the result to a CSV file without including the index
            # Generate a specific output path for each threshold
            specific_output_path = output_path.replace('.csv', f'_Top_{top_n}.csv')
            filtered_destinations.to_csv(specific_output_path, index=False)
            print(f"Generated {specific_output_path}")
    
        else:
            raise ValueError("Either top_n or threshold must be specified.")
        
        return filtered_destinations

if __name__ == "__main__":
    OSM_path = "/OSM_data/Toronto.osm.pbf"
    GTFS_path = "GTFS_data/raw/latest_feed_version_2024-10-22.zip"
    origins_path = "/path/to/origins.geojson"
    destinations_path = "/path/to/destinations.geojson"
    output_matrix_path = "/path/to/travel_time_matrix.csv"
    filtered_output_path = "/path/to/filtered_travel_time.csv"

    travel_calculator = TravelTimeCalculation(OSM_path, GTFS_path)
    travel_calculator.build_transport_network()

    travel_calculator.compute_travel_time_matrix(
        origins_path, destinations_path, output_matrix_path
    )

    travel_calculator.filter_destinations(
        travel_time_matrix_path=output_matrix_path,
        output_path=filtered_output_path,
        top_n=5
    )
