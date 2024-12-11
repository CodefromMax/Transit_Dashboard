import pandas as pd

class MetricCalculation:
    def __init__(self, travel_time_matrix_path):
        """
        Initializes the MetricCalculation class.

        Parameters:
        travel_time_matrix_path (str): Path to the travel time matrix CSV file.
        """
        self.travel_time_matrix_path = travel_time_matrix_path
        self.travel_time_matrix = pd.read_csv(travel_time_matrix_path)

    def filter_destinations(self, output_path=None, top_n=None, threshold=None):
        """
        Filters the travel time matrix to find destinations based on top N or threshold.

        Parameters:
        output_path (str): Path to save the filtered results.
        top_n (int, optional): Number of top destinations to include.
        threshold (float, optional): Travel time threshold to include destinations.
        
        Returns:
        DataFrame: Filtered travel time matrix.
        """
        # Filter out rows where from_id == to_id (self-loops)
        data = self.travel_time_matrix[self.travel_time_matrix['from_id'] != self.travel_time_matrix['to_id']]
        
        if isinstance(threshold, list):
            for t in threshold:
                # Filter destinations within the specified travel time threshold
                filtered_destinations = data[data['travel_time'] <= t]
                # Sort the result by 'from_id' and 'travel_time' for clarity
                filtered_destinations = filtered_destinations[['from_id', 'to_id', 'travel_time']].sort_values(['from_id', 'travel_time'])
                # Generate a specific output path for each threshold
                if output_path:
                    specific_output_path = output_path.replace('.csv', f'_threshold_{t}.csv')
                    # Save the result to a CSV file without including the index
                    filtered_destinations.to_csv(specific_output_path, index=False)
                    print(f"Filtered Destinations generated {specific_output_path}")
                
        elif threshold is not None:
            # Filter destinations within the specified travel time threshold
            filtered_destinations = data[data['travel_time'] <= threshold]
            # Sort the result by 'from_id' and 'travel_time' for clarity
            filtered_destinations = filtered_destinations[['from_id', 'to_id', 'travel_time']].sort_values(['from_id', 'travel_time'])
            # Save the result to a CSV file without including the index
            if output_path:
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
            if output_path:
                specific_output_path = output_path.replace('.csv', f'_Top_{top_n}.csv')
                filtered_destinations.to_csv(specific_output_path, index=False)
                print(f"Generated {specific_output_path}")
    
        else:
            raise ValueError("Either top_n or threshold must be specified.")
        
        return filtered_destinations

    def get_nth_travel_time(self, n, output_path=None):
        """
        Calculates the N-th travel time for each origin in the travel time matrix.

        Parameters:
        n (int): The rank of the travel time to retrieve (e.g., 1st, 2nd, etc.).
        output_path (str, optional): Path to save the result. If None, does not save.

        Returns:
        DataFrame: DataFrame containing the N-th travel time for each origin.
        """
        data = self.travel_time_matrix

        # Replace NaN values in the travel_time column with 100
        data['travel_time'] = data['travel_time'].fillna(100)

        # Sort by travel time and group by 'from_id'
        sorted_data = data.sort_values(['from_id', 'travel_time'])
        

        # Get the N-th travel time for each 'from_id'
        nth_travel_time = (
            sorted_data.groupby('from_id')
            .nth(n - 1)  # Adjust for zero-indexing
            .reset_index()
        )

        # Keep only relevant columns
        nth_travel_time = nth_travel_time[['from_id', 'to_id', 'travel_time']]
        
        # Save to CSV if output_path is provided
        if output_path:
            nth_travel_time.to_csv(output_path, index=False)
            print(f"N-th travel time (N={n}) saved to {output_path}")

        return nth_travel_time

    @staticmethod
    def add_column_with_join(base_df, join_df, base_ctuid_col, join_ctuid_col, join_column_name, new_column_name):
        """
        Function to join a column from a secondary DataFrame and report missing CTUIDs on both sides.
        :param base_df: The main DataFrame to add the new column to.
        :param join_df: The DataFrame to join data from.
        :param base_ctuid_col: The CTUID column name in the base DataFrame.
        :param join_ctuid_col: The CTUID column name in the join DataFrame.
        :param join_column_name: The column name in the join DataFrame to add.
        :param new_column_name: The name of the new column to add to the base DataFrame.
        :return: Updated base DataFrame.
        """
        # Convert CTUID columns to the same data type (string format)
        base_df[base_ctuid_col] = base_df[base_ctuid_col].astype(str)
        join_df[join_ctuid_col] = join_df[join_ctuid_col].astype(str)
        base_df[base_ctuid_col] = base_df[base_ctuid_col].apply(lambda x: f"{float(x):.2f}")
        join_df[join_ctuid_col] = join_df[join_ctuid_col].apply(lambda x: f"{float(x):.2f}")
        # print(base_df[base_ctuid_col])
        # print(join_df[join_ctuid_col])
        # Perform the join
        merged_df = base_df.merge(
            join_df[[join_ctuid_col, join_column_name]],
            left_on=base_ctuid_col,
            right_on=join_ctuid_col,
            how="left"
        )
        
        # Identify missing CTUIDs
        missing_in_base = join_df[~join_df[join_ctuid_col].isin(base_df[base_ctuid_col])][join_ctuid_col]
        missing_in_join = base_df[~base_df[base_ctuid_col].isin(join_df[join_ctuid_col])][base_ctuid_col]

        # Print missing values
        if not missing_in_base.empty:
            print(f"CTUIDs missing in base DataFrame but present in join DataFrame:\n{missing_in_base.tolist()}")
        if not missing_in_join.empty:
            print(f"CTUIDs missing in join DataFrame but present in base DataFrame:\n{missing_in_join.tolist()}")
        
        # Add the new column
        base_df[new_column_name] = merged_df[join_column_name]
        return base_df
    @staticmethod
    def calculate_total_destinations(input_csv_path, ctuid_csv_path, column_names=None, output_csv_path=None):
        """
        Calculate the total number of destinations (to_id) for each origin (from_id) in the travel time matrix,
        join the result with a complete list of CTUIDs, and fill missing values with 0.

        Parameters:
        input_csv_path (str): Path to the input CSV file containing the travel time matrix.
        ctuid_csv_path (str): Path to the CSV file containing the full list of CTUIDs.
        column_names (dict, optional): A dictionary to rename the columns. Keys are:
            - 'from_id': The name of the column representing origins in the input CSV (default is 'from_id').
            - 'to_id': The name of the column representing destinations in the input CSV (default is 'to_id').
            - 'CTUID': The name of the column representing CTUID in the full list (default is 'CTUID').
            - 'total_column': The name of the output column representing the total destinations (default is 'total_destinations').
        output_csv_path (str, optional): Path to save the output CSV file with the total number of destinations for each CTUID. Default is None.

        Returns:
        pd.DataFrame: A DataFrame containing the total number of destinations for each CTUID, with missing values filled with 0.
        """
        # Default column names
        default_column_names = {
            'from_id': 'from_id',
            'to_id': 'to_id',
            'CTUID': 'CTUID',
            'total_column': 'total_destinations'
        }
        column_names = {**default_column_names, **(column_names or {})}

        # Load the travel time matrix CSV file
        travel_time_matrix = pd.read_csv(input_csv_path)
        travel_time_matrix[column_names['from_id']] = travel_time_matrix[column_names['from_id']].apply(lambda x: f"{x:.2f}")
        # Group by 'from_id' and calculate the count of 'to_id' for each 'from_id'
        total_destinations = travel_time_matrix.groupby(column_names['from_id'])[column_names['to_id']].count().reset_index()
        total_destinations.columns = [column_names['CTUID'], column_names['total_column']]

        # Load the CSV file with the full list of CTUIDs
        ct_data = pd.read_csv(ctuid_csv_path)
        ct_data = ct_data[[column_names['CTUID']]]  # Keep only the CTUID column
        ct_data['CTUID'] = ct_data['CTUID'].apply(lambda x: f"{x:.2f}")
        # Merge the total destinations with the full list of CTUIDs
        result = ct_data.merge(total_destinations, on=column_names['CTUID'], how='left')

        # Fill missing values with 0
        result[column_names['total_column']] = result[column_names['total_column']].fillna(0).astype(int)

        # Save the result to a CSV file if output_csv_path is provided
        if output_csv_path:
            result.to_csv(output_csv_path, index=False)
            print(f"Output saved to {output_csv_path}")

        return result
    @staticmethod
    def pivot_totals_to_rows(input_data, output_path=None):
        """
        Pivots all columns except 'CTUID' and 'Neighbourhood' to rows and optionally saves the result to a CSV.

        Args:
            input_data (str or pd.DataFrame): Path to the input CSV file or a pandas DataFrame containing the data.
            output_path (str, optional): Path to save the transformed DataFrame. If None, does not save.

        Returns:
            pd.DataFrame: A transformed DataFrame with all totals pivoted to rows.
        """
        
        # Read the input data if it is a string (file path)
        if isinstance(input_data, str):
            df = pd.read_csv(input_data)
        elif isinstance(input_data, pd.DataFrame):
            df = input_data
        else:
            raise ValueError("input_data must be a file path (str) or a pandas DataFrame.")

        # Identify all columns except 'CTUID' and 'Neighbourhood'
        columns_to_pivot = [col for col in df.columns if col not in ['CTUID', 'Neighbourhood']]

        # Ensure the required columns are present in the DataFrame
        if not columns_to_pivot:
            raise ValueError("No columns available to pivot after 'CTUID' and 'Neighbourhood'.")

        # Pivot the columns to rows
        pivoted_df = pd.melt(
            df, 
            id_vars=['CTUID', 'Neighbourhood'],  # Keep these columns intact
            value_vars=columns_to_pivot,        # Columns to pivot
            var_name='Before_After_Difference',  # Name for the new column indicating the original column names
            value_name='Value'                  # Name for the new column containing the values
        ).sort_values(by=['CTUID', 'Neighbourhood'])

        # Save the result to CSV if output_path is provided
        if output_path:
            pivoted_df.to_csv(output_path, index=False)
            print(f"Transformed data saved to {output_path}")

        return pivoted_df
    @staticmethod
    def group_to_ids_by_ctuid(input_data, output_path=None, from_id_col='from_id', to_id_col='to_id'):
        """
        Groups all `to_id` values for each Census Tract (`from_id` or `CTUID`) into a list.

        Args:
            input_data (str or pd.DataFrame): Path to the input CSV file or a pandas DataFrame containing the data.
            output_path (str, optional): Path to save the grouped result as a CSV. If None, does not save.
            from_id_col (str): Column name representing the Census Tract ID (default is 'from_id').
            to_id_col (str): Column name representing the destination IDs (default is 'to_id').

        Returns:
            pd.DataFrame: A DataFrame with `from_id` and the grouped `to_id` list.
        """
        # Read the input data if it is a string (file path)
        if isinstance(input_data, str):
            df = pd.read_csv(input_data)
        elif isinstance(input_data, pd.DataFrame):
            df = input_data
        else:
            raise ValueError("input_data must be a file path (str) or a pandas DataFrame.")

        # Ensure the required columns are present
        if from_id_col not in df.columns or to_id_col not in df.columns:
            raise ValueError(f"Columns '{from_id_col}' and '{to_id_col}' must exist in the input data.")

        # Group by `from_id` and aggregate `to_id` into lists
        grouped_df = df.groupby(from_id_col)[to_id_col].apply(list).reset_index()

        # Rename the aggregated column for clarity
        grouped_df = grouped_df.rename(columns={to_id_col: f'{to_id_col}_list'})

        # Save the result to a CSV if output_path is provided
        if output_path:
            grouped_df.to_csv(output_path, index=False)
            print(f"Grouped data saved to {output_path}")

        return grouped_df


if __name__ == "__main__":
    travel_time_matrix_path = "/path/to/travel_time_matrix.csv"
    filtered_output_path = "/path/to/filtered_travel_time.csv"
    metrics_output_path = "/path/to/accessibility_metrics.csv"

    metric_calculator = MetricCalculation(travel_time_matrix_path)

    # Filter destinations based on top N or threshold
    metric_calculator.filter_destinations(filtered_output_path, top_n=5)

    # Calculate accessibility metrics
    metric_calculator.calculate_accessibility_metrics(metrics_output_path)