# Input from Excel Import Node (flattened data)
excel_data = IN[0]

# Initialize an empty list to hold the data in the desired list of lists format
data_rows = []

try:
    # Iterate through each row in the Excel data
    for row in excel_data:
        # Ensure row is a list and has meaningful data in the first six fields (Header, SubHeader, Type, Existing, Proposed, Variation)
        if isinstance(row, list) and len(row) >= 6:
            # Extract and format the required data, providing sensible default values where necessary
            header = row[0] if row[0] is not None else "N/A"
            sub_header = row[1] if row[1] is not None else "N/A"
            item_type = row[2] if row[2] is not None else "N/A"
            existing = row[3] if row[3] is not None else 0
            proposed = row[4] if row[4] is not None else 0
            variation = row[5] if row[5] is not None else 0

            # Only include rows with meaningful sub-header data (ignore entirely empty rows)
            if sub_header != "N/A":
                # Create a list for the row, keeping fields in the correct order
                row_list = [header, sub_header, item_type, existing, proposed, variation]

                # Append the row list to the data rows
                data_rows.append(row_list)

    # Set output to the list of lists
    if not data_rows:
        OUT = "No valid rows found in input data. Check the structure of the input or revise the extraction logic."
    else:
        OUT = data_rows

except Exception as e:
    # Output any errors that occur
    OUT = "Error occurred: {}".format(str(e))
