# Input from Excel Import Node (flattened data)
excel_data = IN[0]

# Input list of Sub-Headers to be matched
sub_headers_to_match = IN[1]

# Initialize an empty list to hold the data in the desired list of lists format
data_rows = []

try:
    # Check if sub_headers_to_match is a list
    if not isinstance(sub_headers_to_match, list):
        raise ValueError("Sub-Headers to match must be provided as a list.")

    # Track unmatched sub-headers
    unmatched_sub_headers = set(sub_headers_to_match)

    # Iterate through each row in the Excel data
    for row in excel_data:
        # Check if the row is a valid list and has at least 6 fields
        if isinstance(row, list) and len(row) >= 6:
            # Extract and format the required data, providing sensible default values where necessary
            header = row[0] if row[0] else "N/A"
            sub_header = row[1] if row[1] else "N/A"
            item_type = row[2] if row[2] else "N/A"
            try:
                existing = float(row[3]) if row[3] else 0  # Convert to float if applicable
                proposed = float(row[4]) if row[4] else 0
                variation = float(row[5]) if row[5] else 0
            except ValueError:
                # Handle case where numerical values are not valid numbers
                existing, proposed, variation = 0, 0, 0

            # Only include rows with meaningful sub-header data that matches the provided list
            if sub_header in sub_headers_to_match:
                # Remove matched sub-header from unmatched list
                unmatched_sub_headers.discard(sub_header)
                # Create a list for the row, keeping fields in the correct order
                row_list = [header, sub_header, item_type, existing, proposed, variation]

                # Append the row list to the data rows
                data_rows.append(row_list)

    # Check for unmatched sub-headers and raise an error if any remain
    if unmatched_sub_headers:
        raise ValueError("The following Sub-Headers were not found in the input data: {}".format(", ".join(unmatched_sub_headers)))

    # Set output to the list of lists
    OUT = data_rows if data_rows else "No valid rows found in input data. Check the structure of the input or revise the extraction logic."

except Exception as e:
    # Output any errors that occur
    OUT = "Error occurred: {}".format(str(e))
