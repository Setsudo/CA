import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Inputs
input_list = IN[0]  # The input list containing all rows
desired_sub_headers = IN[1]  # The list of desired sub-headers to keep

# Function to filter rows based on Sub-Header
def filter_rows(input_list, filter_values):
    filtered_rows = []
    
    for row in input_list:
        row_name, row_data = row
        
        # Check if any item in the row matches the desired sub-headers
        if any(item[0] in filter_values for item in row_data):
            filtered_rows.append(row)
    
    return filtered_rows

# Apply filter
filtered_output = filter_rows(input_list, desired_sub_headers)

# Output
OUT = filtered_output
