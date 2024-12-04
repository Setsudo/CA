import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Inputs
input_list = IN[0]  # The input list containing all rows
desired_sub_headers = IN[1]  # The list of desired sub-headers to keep

# Function to filter rows based on Sub-Header and remove left elements using X value

def filter_rows(input_list, filter_values):
    filtered_rows = []
    
    for row in input_list:
        row_name, row_data = row
        new_row_data = []
        
        # Normalize sub-header text by removing line breaks
        normalized_filter_values = [header.replace("\n", " ").replace("\r", " ") for header in filter_values]
        
        # Find the minimum X value of the sub-header items, regardless of line breaks in the text
        x_values = [item[1][2][1] for item in row_data if item[0].replace("\n", " ").replace("\r", " ") in normalized_filter_values]
        
        if x_values:
            min_x_value = min(x_values)
            
            # Add only items that are at or to the right of the sub-header X value
            for item in row_data:
                x_value = item[1][2][1]
                if x_value >= min_x_value:
                    new_row_data.append(item)
        
        # Add the row to filtered_rows if it has any data left after filtering
        if new_row_data:
            filtered_rows.append([row_name, new_row_data])
    
    return filtered_rows

# Apply filter
filtered_output = filter_rows(input_list, desired_sub_headers)

# Output
OUT = filtered_output
