import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
import re
import unicodedata
from difflib import SequenceMatcher

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

# Improved function to normalize sub-header strings for better matching
def improved_normalize_header(header):
    if not isinstance(header, str):
        return ""
    # Handle line breaks in text
    header = header.replace('\n', ' ')
    header = unicodedata.normalize('NFKD', header)  # Normalize unicode characters
    # Keep forward slashes for "BEER / WINE" style headers
    header = re.sub(r'\s*\([^)]*\)', '', header)  # Remove all parentheses and their contents
    header = re.sub(r'[^\w\s/]', '', header)  # Replace special characters except slashes
    header = re.sub(r'\s+', ' ', header)  # Replace line breaks and multiple spaces with a single space
    header = header.strip()  # Remove leading/trailing whitespace
    header = header.upper()  # Convert to uppercase for uniform comparison
    return header

# Function to take tolerance as input
def group_text_notes(text_notes_data, tolerance, sub_headers_filter):
    # Normalize sub_headers_filter for comparison
    normalized_sub_headers_filter = [improved_normalize_header(header) for header in sub_headers_filter]

    # Ensure that text_notes_data is a list and tolerance is a float
    text_notes_data = navigate_and_flatten(text_notes_data)
    
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

    # Sort positions by Y (descending), then by X (ascending)
    positions.sort(key=lambda pos: (-pos[1], pos[0]))

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

    # Process the grouped rows to extract sub-headers, their values, and Legend Index
    processed_rows = []
    matched_sub_headers = []
    for row in grouped_rows:
        texts_in_row = [item[2] for item in row]  # Extract the text elements
        legend_indices_in_row = [item[3] for item in row]  # Extract the Legend Index
        if len(texts_in_row) > 4 and not texts_in_row[0].isdigit():
            # Assume the first item is a sub-header, followed by the four values we're interested in
            sub_header = texts_in_row[0]
            normalized_sub_header = improved_normalize_header(sub_header)

            type_labels = texts_in_row[1:5]  # Extract type labels (e.g., LF, SLF, DR)
            values = texts_in_row[1:5]  # Collect all four values
            legend_indices = legend_indices_in_row[1:5]  # Collect corresponding Legend Index for each value

            # Create a structured entry to maintain the original nested format
            if normalized_sub_header in normalized_sub_headers_filter or any(similar(normalized_sub_header, filter_header) for filter_header in normalized_sub_headers_filter):
                processed_entry = [
                    sub_header,
                    type_labels,  # Type labels
                    values,  # Values corresponding to the type labels
                    legend_indices   # Corresponding Legend Index for each value
                ]
                processed_rows.append(processed_entry)

                # Track matched sub-header with number of occurrences
                matched_sub_headers.append(normalized_sub_header)

    # Ensure the number of outputs matches the number of inputs exactly
    output_rows = []
    for sub_header in sub_headers_filter:
        normalized_sub_header = improved_normalize_header(sub_header)
        matching_entries = [entry for entry in processed_rows if improved_normalize_header(entry[0]) == normalized_sub_header]
        if matching_entries:
            # Make sure to append all matching entries that are required by the number of inputs
            output_rows.extend(matching_entries)  # Do not limit to one entry to ensure exact match count
        else:
            # If no match found, add a default entry
            output_rows.append([sub_header, ["N/A"] * 4, [0] * 4, ["N/A"] * 4])

    # Error if any sub-header is not matched
    unmatched_sub_headers = set(normalized_sub_headers_filter) - set(matched_sub_headers)
    if unmatched_sub_headers:
        # Raise an error and also output the error in the result for visibility in Dynamo Watch node
        error_message = f"The following sub-headers were not matched: {unmatched_sub_headers}"
        OUT = error_message
        return OUT

    return output_rows

# Adjustable tolerance value for grouping rows (Dynamo input)
tolerance = IN[1]

# Convert tolerance to float
try:
    tolerance = float(tolerance)  # Convert to float if possible
except (ValueError, TypeError):
    raise ValueError("tolerance must be a number")

# Use the navigate_and_flatten function to process text_notes_data
text_notes_data = navigate_and_flatten(text_notes_data)

# Group the text notes with the given tolerance and sub-header filter
try:
    processed_rows = group_text_notes(text_notes_data, tolerance, sub_headers_filter)
    OUT = processed_rows  # Output the grouped rows
except ValueError as e:
    OUT = str(e)  # Output the error message to the Watch node in Dynamo
