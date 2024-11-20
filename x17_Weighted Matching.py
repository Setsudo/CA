# Load necessary libraries
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Inputs: Each input is a tuple of four lists: (items, indices, reordered_items, weights)
perfect_match = IN[0]
partial_match_1 = IN[1]
partial_match_2 = IN[2]
partial_match_3 = IN[3]
partial_match_4 = IN[4]
takeoff_list = IN[5]  # Original Takeoff list to check the indexing consistency

# Initialize output lists
final_matched_items = []       # Best matched items from Master Family List
final_matched_indices = []     # Indices corresponding to the best matched items
final_weights = []             # Weights for each match, with lower weight indicating higher priority
match_criteria = []            # Original match criteria from input matches (used to verify alignment with Takeoff)

# List of all match types for easier iteration
all_matches = [perfect_match, partial_match_1, partial_match_2, partial_match_3, partial_match_4]

# Process each index in the `TakeoffList` order
for i in range(len(takeoff_list)):  # Use the length of the Takeoff list for iteration
    # Track the best match details for this index
    best_match = None
    best_index = None
    best_weight = float('inf')  # Initialize with infinity to find the lowest weight
    match_criteria_item = None

    # Iterate through each match type to determine the best match for this index
    for match_type in all_matches:
        # Ensure the match_type tuple has exactly four components to prevent unpacking errors
        if len(match_type) != 4:
            continue

        items, indices, reordered_items, weights = match_type  # Extract components from the match tuple
        # Iterate through the indices to find a match for the current takeoff index
        for j in range(len(indices)):
            index = indices[j]

            # If the current index matches the takeoff index, evaluate the match
            if index == i:
                item = items[j]
                weight = weights[j]

                # Select the item with the lowest weight (highest priority)
                if item is not None and weight < best_weight:
                    best_match = item
                    best_index = i  # Set the best index to the current takeoff index
                    best_weight = weight
                    match_criteria_item = item

    # Verify if the current best match index matches the original indexing in the Takeoff list
    if best_index is not None and best_index != i:
        raise ValueError(f"Index mismatch: best index {best_index} does not match Takeoff index {i}.")

    # Append results for the best match found
    final_matched_items.append(best_match if best_match is not None else None)  # Append the best matched item from Master Family List
    final_matched_indices.append(best_index if best_index is not None else None)  # Append the index of the best match
    match_criteria.append(match_criteria_item if match_criteria_item is not None else None)
    final_weights.append(best_weight if best_match is not None else 0)  # Set weight to 0 if no match

# Output the final selected items, indices, match criteria, and weights in the required format
OUT = (
    final_matched_items,      # Index 0: Best matched items from Master Family List
    final_matched_indices,    # Index 1: Indices of the best matched items
    match_criteria,           # Index 2: Original match criteria from matching logic inputs
    final_weights             # Index 3: Weights for each selected match
)
