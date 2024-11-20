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
rows_to_drop = IN[5]  # Number of starting rows to drop

# Initialize output lists
final_matched_items = []       # Best matched items from Master Family List
final_matched_indices = []     # Indices corresponding to the best matched items in Master Family List
final_weights = []             # Weights for each match, with lower weight indicating higher priority
match_criteria = []            # Original match criteria from input matches (used to verify alignment with Takeoff)

# List of all match types for easier iteration
all_matches = [perfect_match, partial_match_1, partial_match_2, partial_match_3, partial_match_4]

# Determine the length of the shortest list in the matches (to avoid out-of-range errors)
min_length = min(len(match[0]) for match in all_matches if len(match) == 4)

# Adjust min_length to account for rows to drop
min_length = max(0, min_length - rows_to_drop)

# Process each index in the input lists, starting after the dropped rows
for i in range(rows_to_drop, rows_to_drop + min_length):
    best_match = None
    best_index = None
    best_weight = None  # Start with None to signify no match found yet

    # Iterate through each match type to determine the best match for this index
    for match_type in all_matches:
        # Ensure the match_type tuple has exactly four components to prevent unpacking errors
        if len(match_type) != 4:
            continue

        items, indices, reordered_items, weights = match_type  # Extract components from the match tuple
        
        # Ensure that we do not exceed the bounds of any of the lists
        if i >= len(items) or i >= len(indices) or i >= len(weights):
            continue
        
        item = items[i]
        index = indices[i]
        weight = weights[i]

        # Select the item with the lowest weight (highest priority)
        if item is not None and (best_weight is None or weight < best_weight):
            best_match = item
            best_index = index
            best_weight = weight

    # Append the best match found for this index
    final_matched_items.append(best_match if best_match is not None else None)
    final_matched_indices.append(best_index if best_index is not None else None)
    match_criteria.append(best_match if best_match is not None else None)  # Ensure criteria matches final match
    final_weights.append(best_weight if best_weight is not None else None)

# Output the final selected items, indices, match criteria, and weights in the required format
OUT = (
    final_matched_items,      # Index 0: Best matched items from Master Family List
    final_matched_indices,    # Index 1: Indices of the best matched items in Master Family List
    match_criteria,           # Index 2: Original match criteria from matching logic inputs
    final_weights             # Index 3: Weights for each selected match
)
