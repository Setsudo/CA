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

# Initialize output lists
final_matched_items = []       # Selected items after applying weights, ordered according to List2 (Takeoff List)
final_matched_indices = []     # Indices corresponding to the best matched items, ordered as in List2
final_weights = []             # Weights for each match, with lower weight indicating higher priority
reordered_matches = []         # Reordered matches to visually align with List2 order

# List of all match types for easier iteration
all_matches = [perfect_match, partial_match_1, partial_match_2, partial_match_3, partial_match_4]

# Process each index in the `TakeoffList` order
for i in range(len(perfect_match[0])):  # Assuming all match lists have the same length
    # Track the best match details for this index
    best_match = None
    best_index = None
    best_weight = None
    
    # Iterate through each match type to determine the best match for this index
    for match_type in all_matches:
        # Ensure the match_type tuple has exactly four components to prevent unpacking errors
        if len(match_type) != 4:
            continue
        
        items, indices, _, weights = match_type  # Extract components from the match tuple
        # Ensure the current index is within bounds for the current list
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

    # Append results for the best match found
    final_matched_items.append(best_match)
    final_matched_indices.append(best_index)
    reordered_matches.append(best_match)  # Matches reordered to align with Takeoff List
    final_weights.append(best_weight if best_weight is not None else 0)  # Set weight to 0 if no match

# Output the final selected items, indices, reordered matches, and weights
OUT = (
    final_matched_items,      # Best matched items
    final_matched_indices,    # Indices of best matches
    reordered_matches,        # Matches reordered to match Takeoff List order
    final_weights             # Weights for each selected match
)
