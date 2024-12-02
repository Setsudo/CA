import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Sample data from your output (truncated for brevity)
text_notes_data = IN[0]
sub_headers_filter = IN[2]  # List of sub-headers to filter by

# Function to navigate through nested lists to flatten them
# but maintain the heavily nested structure for proper navigation
def navigate_and_flatten(input_list):
    result = []
    for item in input_list:
        if isinstance(item, list):
            result.append(navigate_and_flatten(item))
        else:
            result.append(item)
    return result

# Function to take tolerance as input
def group_text_notes(text_notes_data, tolerance, sub_headers_filter):
    # Ensure that text_notes_data is a list and tolerance is a float
    text_notes_data = navigate_and_flatten(text_notes_data)
    
    # Debug: Check the flattened text notes data
    print("Navigated text_notes_data:", text_notes_data)

    if not isinstance(text_notes_data, list):
        raise ValueError("text_notes_data must be a list")
    if not isinstance(tolerance, (int, float)):
        raise ValueError("tolerance must be a number")
    if not isinstance(sub_headers_filter, list):
        raise ValueError("sub_headers_filter must be a list")

    # Extract positions, text, and Legend Index
    positions = []
    for text_note in text_notes_data:
        if not isinstance(text_note, list) or len(text_note) < 2:
            continue  # Skip invalid entries
        try:
            text = text_note[0]
            legend_index_info = text_note[1]
            if isinstance(legend_index_info, list) and len(legend_index_info) >= 3:
                legend_index = legend_index_info[1]  # Correctly assign Legend Index
                _, x, y, *_ = legend_index_info[2]
                positions.append((x, y, text, legend_index))
        except Exception as e:
            # Debug: Log exceptions in extracting data
            print(f"Error processing text_note: {text_note}, Error: {e}")

    # Debug: Check extracted positions
    print("Extracted positions:", positions)

    # Sort positions by Y (descending), then by X (ascending)
    positions.sort(key=lambda pos: (-pos[1], pos[0]))

    # Debug: Check sorted positions
    print("Sorted positions:", positions)

    # Group by similar Y values (rows) with tolerance
    grouped_rows = []
    if positions:
        current_group = [positions[0]]
    else:
        current_group = []
        
    for current in positions[1:]:
        last = current_group[-1]
        if abs(current[1] - last[1]) <= tolerance:
            current_group.append(current)
        else:
            grouped_rows.append(current_group)
            current_group = [current]
    if current_group:
        grouped_rows.append(current_group)

    # Debug: Check grouped rows
    print("Grouped rows:", grouped_rows)

    # Process the grouped rows to extract sub-headers, their values, and Legend Index
    processed_rows = []
    for row in grouped_rows:
        texts_in_row = [item[2] for item in row]  # Extract the text elements
        legend_indices_in_row = [item[3] for item in row]  # Extract the Legend Index
        if len(texts_in_row) > 4 and not texts_in_row[0].isdigit():
            # Assume the first item is a sub-header, followed by the four values we're interested in
            sub_header = texts_in_row[0]
            values = texts_in_row[1:5]  # Collect all four values
            legend_indices = legend_indices_in_row[1:5]  # Collect corresponding Legend Index for each value
            if sub_header in sub_headers_filter:
                processed_rows.append((sub_header, values, legend_indices))

    # Debug: Check processed rows
    print("Processed rows:", processed_rows)

    return processed_rows

# Adjustable tolerance value for grouping rows (Dynamo input)
tolerance = IN[1]

# Convert tolerance to float
try:
    tolerance = float(tolerance)  # Convert to float if possible
except (ValueError, TypeError):
    raise ValueError("tolerance must be a number")

# Use the navigate_and_flatten function to process text_notes_data
text_notes_data = navigate_and_flatten(text_notes_data)

# Debug: Check initial inputs
print("Initial text_notes_data:", text_notes_data)
print("Tolerance:", tolerance)
print("Sub-header filter list:", sub_headers_filter)

# Group the text notes with the given tolerance and sub-header filter
processed_rows = group_text_notes(text_notes_data, tolerance, sub_headers_filter)

# Output the grouped rows
OUT = processed_rows
