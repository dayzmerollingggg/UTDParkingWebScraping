import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import glob
import os

# --- Assumed File Naming Convention and Column Headers ---
# The script now looks for all files ending in '.csv'.
# It assumes filenames are in the format "WeekDay_Garage_#".
COL_DATE = 'Date'
COL_HOUR = 'Hour'
COL_MINUTE = 'Minute'
COL_PERMIT_TYPE = 'Permit Type'
COL_SPACES_LEFT = 'Spaces Left'


def create_parking_trend_graph(df, weekday, garage_num):
    """
    Processes a DataFrame of parking data to create a trend graph.

    Args:
        df (pd.DataFrame): The input DataFrame with parking data.
        weekday (str): The day of the week to be used in the graph title.
        garage_num (str): The garage number to be used in the graph title.
    """
    # Check if the necessary columns exist in the DataFrame
    required_cols = [COL_DATE, COL_HOUR, COL_MINUTE, COL_PERMIT_TYPE, COL_SPACES_LEFT]
    if not all(col in df.columns for col in required_cols):
        print(f"Error in data for {weekday} Garage {garage_num}: Missing one of the required columns:")
        print(f"Expected: {required_cols}")
        print(f"Found: {list(df.columns)}")
        return

    # --- Data Cleaning and Aggregation ---
    print(f"Processing data for {weekday} Garage {garage_num}...")

    # Group by 'Permit Type' and 'Hour' and calculate the mean of 'Spaces Left'
    hourly_avg_spaces = df.groupby([COL_PERMIT_TYPE, COL_HOUR])[COL_SPACES_LEFT].mean().reset_index()

    # --- Plotting the Data ---
    print(f"Generating graph for {weekday} Garage {garage_num}...")

    sns.set_style("whitegrid")
    
    plt.figure(figsize=(12, 8))
    
    # Define a custom color palette for each permit type.
    color_palette = {
        'Gold Permit': "#ffe93e",  # A shade of blue
        'Orange Permit': '#ff7f0e',  # A shade of orange
        'Pay-By-Space': "#39cde4",  # A shade of green
        'Purple Permit': "#6c06b1",
        # Add more permit types here if needed
    }

    # Use seaborn to create a line plot.
    sns.lineplot(
        data=hourly_avg_spaces,
        x=COL_HOUR,
        y=COL_SPACES_LEFT,
        hue=COL_PERMIT_TYPE,
        marker='o',
        palette=color_palette
    )

    # --- Customizing the Plot for better readability ---
    # The title is now dynamic based on the filename
    plt.title(f'Average Parking Spaces Left on {weekday} for Garage {garage_num}', fontsize=16, fontweight='bold')
    plt.xlabel('Hour of the Day (24-hour format)', fontsize=12)
    plt.ylabel('Average Spaces Left', fontsize=12)
    plt.xticks(range(24))
    plt.grid(True)
    plt.legend(title='Permit Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # The output filename is now dynamic based on the filename
    output_file_name = f'{weekday}_Garage_{garage_num}_parking_spaces_graph.png'
    plt.savefig(output_file_name)
    print(f"Graph saved as '{output_file_name}'")
    plt.close() # Close the plot to free up memory for the next one


# --- Main execution block ---
if __name__ == '__main__':
    # Find all CSV files in the current directory that match the naming pattern
    csv_files = glob.glob("*.csv")
    if not csv_files:
        print("No CSV files found in the current directory.")
    
    for file_path in csv_files:
        try:
            # Extract weekday and garage number from the filename
            filename_with_ext = os.path.basename(file_path)
            base_filename, file_extension = os.path.splitext(filename_with_ext)
            
            # Split the base filename to get the parts
            parts = base_filename.split('_')
            if len(parts) >= 3 and parts[0].isalpha() and parts[1] == 'Garage' and parts[2].isdigit():
                weekday = parts[0]
                garage_num = parts[2].split('.')[0] # Remove file extension
                
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(file_path, index_col=False)

                # Call the function to create the graph
                create_parking_trend_graph(df, weekday, garage_num)
            else:
                print(f"Skipping file '{filename_with_ext}' due to incorrect naming format.")

        except pd.errors.EmptyDataError:
            print(f"Error: The file '{file_path}' is empty. Skipping.")
        except FileNotFoundError:
            # This should not happen with glob, but is a good practice
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An unexpected error occurred while processing '{file_path}': {e}")
