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
                # Extract the element and the following columns based on count
                end_index = min(i + num_following_columns + 1, len(data))
                results.append(data[i:end_index])

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
