import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *

# Inputs
text_notes = IN[0]  # Nested list containing TextNotes data

# Function to determine column and row boundaries based on the positions of TextNotes
def infer_grid_dimensions(text_notes):
    x_values = []
    y_values = []
    
    # Extract X and Y coordinates from the nested list
    for note in text_notes:
        position_data = note[1][2]
        _, x, y, _ = position_data
        x_values.append(x)
        y_values.append(y)
    
    # Sort and calculate the average difference between sorted unique values as the inferred width/height
    unique_x_values = sorted(set(x_values))
    unique_y_values = sorted(set(y_values))
    
    column_width = (max(unique_x_values) - min(unique_x_values)) / (len(unique_x_values) - 1) if len(unique_x_values) > 1 else 1
    row_height = (max(unique_y_values) - min(unique_y_values)) / (len(unique_y_values) - 1) if len(unique_y_values) > 1 else 1
    
    return column_width, row_height

# Infer column width and row height
column_width, row_height = infer_grid_dimensions(text_notes)

# Function to determine column and row indices based on X, Y values
def calculate_grid_indices(x, y, column_width, row_height):
    column = int(x // column_width) + 1  # Convert to 1-based index
    row = int(y // row_height) + 1       # Convert to 1-based index
    return column, row

# Loop through each TextNote and add Column and Row information to the nested list
for note in text_notes:
    position_data = note[1][2]
    _, x, y, _ = position_data
    
    # Calculate column and row indices
    column, row = calculate_grid_indices(x, y, column_width, row_height)
    
    # Move Column and Row data to the same level as the note title
    note.insert(1, ("Column", column))
    note.insert(2, ("Row", row))

# Output (for verification in Dynamo)
OUT = text_notes
