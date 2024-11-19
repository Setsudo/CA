import re

# Input from Excel Import Node
excel_data = IN[0]  # Input Excel data (deeply nested structure)
target_sub_header_text = IN[1]  # The sub-header text we are looking for

# Clean the target text to remove extra spaces, normalize line breaks, and convert to upper case
target_sub_header_text_clean = re.sub(r'\s+', ' ', target_sub_header_text.strip()).upper()

output_data = []

# Function to flatten nested lists
def flatten_list(data):
    flat_list = []
    if isinstance(data, list):
        for item in data:
            flat_list.extend(flatten_list(item))
    else:
        flat_list.append(data)
    return flat_list

# Flatten the deeply nested list structure to access the actual rows
flattened_data = flatten_list(excel_data)

# Iterate through the flattened data to find rows (each row is a list)
for row in flattened_data:
    if isinstance(row, list) and len(row) >= 2:
        subcategory = row[1]

        # Check if the subcategory is a string and is not None
        if subcategory is not None and isinstance(subcategory, str):
            # Normalize the text for consistent comparison
            subcategory_clean = re.sub(r'\s+', ' ', subcategory.strip()).upper()

            # Debugging: Print the cleaned sub-header to see exactly what we are matching
            print(f"Sub-Header in Row: '{subcategory_clean}'")
            print(f"Target Sub-Header: '{target_sub_header_text_clean}'")

            # Final matching check
            if target_sub_header_text_clean == subcategory_clean:
                output_data = row
                break

# Output the transformed data focusing on the specific sub-header
OUT = output_data if output_data else f"No matching sub-header found for: '{target_sub_header_text_clean}'"
