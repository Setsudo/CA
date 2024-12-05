import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import re

# Function to flatten nested list into a single-level list
def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

# Function to remove all non-alphanumeric characters, spaces, and line breaks from a string
def normalize_string(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

# Function to search for labels and return the desired columns in the original format
def find_labels_and_columns(data, labels, num_following_columns):
    results = []
    found_labels = set()
    normalized_labels = [normalize_string(label) for label in labels]
    
    # Iterate through each element in the data
    for i, element in enumerate(data):
        if isinstance(element, list) and len(element) > 0 and isinstance(element[0], str):
            label = element[0]
            normalized_label = normalize_string(label)
            if normalized_label in normalized_labels:
                # Mark the label as found
                found_labels.add(normalized_label)
                
                # Extract the row and column of the matched label
                label_row = None
                label_column = None
                for sub_element in element:
                    if isinstance(sub_element, list) and len(sub_element) > 1:
                        if sub_element[0] == 'Row':
                            label_row = sub_element[1]
                        elif sub_element[0] == 'Column':
                            label_column = sub_element[1]
                
                if label_row is None or label_column is None:
                    continue
                
                # Collect the elements in the same row, based on column values to the right of the matched label
                collected_section = [element]  # Start with the matched element itself
                columns_collected = 1  # Count the current label as collected
                
                # Sort the data based on the column value to ensure proper ordering
                sorted_data = sorted([elem for elem in data if isinstance(elem, list) and len(elem) > 0], 
                                    key=lambda x: next((sub[1] for sub in x if isinstance(sub, list) and sub[0] == 'Column'), float('inf')))
                
                # Iterate over sorted data to collect elements that match the same row and are sequential to the right in terms of columns
                for other_element in sorted_data:
                    if other_element == element:
                        continue  # Skip the matched label itself
                    if isinstance(other_element, list) and len(other_element) > 0 and isinstance(other_element[0], str):
                        other_row = None
                        other_column = None
                        for sub in other_element:
                            if isinstance(sub, list) and len(sub) > 1:
                                if sub[0] == 'Row':
                                    other_row = sub[1]
                                elif sub[0] == 'Column':
                                    other_column = sub[1]
                        
                        # If rows match and the other column is strictly to the right of the matched label's column, collect the element
                        if other_row == label_row and other_column is not None and other_column > label_column and columns_collected < num_following_columns + 1:
                            collected_section.append(other_element)
                            columns_collected += 1
                
                # Title each list with the relevant Sub-Header
                results.append([label, collected_section])

    # Check if all labels were found, if not append the error to OUT
    if len(found_labels) != len(normalized_labels):
        missing_labels = [label for label in labels if normalize_string(label) not in found_labels]
        if missing_labels:
            return f"Error: The following labels were not found in the data: {missing_labels}"

    return results

# Input data: The structured dataset and list of labels of interest from Dynamo UI input
data = IN[0]  # Expecting input from Dynamo to be a structured list

# Dynamically input labels of interest from user (Dynamo UI input)
labels_of_interest = IN[1]  # Expecting input from Dynamo to be a list of labels

# Input for number of following columns to collect (Dynamo UI input)
num_following_columns = IN[2]  # Expecting input from Dynamo to be an integer specifying the number of following columns

# Find labels and their respective columns
matched_results = find_labels_and_columns(data, labels_of_interest, num_following_columns)

# Output the results in the same format as the input
OUT = matched_results
