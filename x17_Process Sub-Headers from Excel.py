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

    # Create a list to track unmatched sub-headers
    unmatched_sub_headers = sub_headers_to_match.copy()

    # Iterate through each row in the Excel data
    for row in excel_data:
        # Check if the row is a valid list and has at least 6 fields
        if isinstance(row, list) and len(row) >= 6:
            # Extract and format the required data, providing sensible default values where necessary
            sub_header = row[1] if row[1] else "N/A"
            item_type = row[2] if row[2] else "N/A"
            existing = row[3] if row[3] is not None and row[3] != "" else 0
            proposed = row[4] if row[4] is not None and row[4] != "" else 0
            variation = row[5] if row[5] is not None and row[5] != "" else 0

            # Only include rows with meaningful sub-header data that matches the provided list
            if sub_header in sub_headers_to_match:
                # Create a list for the row, formatted to match the desired output structure with labels
                row_list = [
                    "Sub-Header", sub_header,
                    [
                        "Type", item_type,
                        "Existing", existing,
                        "Proposed", proposed,
                        "Variation", variation
                    ]
                ]

                # Append the row list to the data rows
                data_rows.append(row_list)

                # Remove one occurrence of the matched sub-header from unmatched list if present
                if sub_header in unmatched_sub_headers:
                    unmatched_sub_headers.remove(sub_header)

    # Check for unmatched sub-headers and raise an error if any remain
    if unmatched_sub_headers:
        raise ValueError("The following Sub-Headers were not found in the input data: {}".format(", ".join(unmatched_sub_headers)))

    # Set output to the list of lists
    OUT = data_rows if data_rows else "No valid rows found in input data. Check the structure of the input or revise the extraction logic."

except Exception as e:
    # Output any errors that occur
    OUT = "Error occurred: {}".format(str(e))
