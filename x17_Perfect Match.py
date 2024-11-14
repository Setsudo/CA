# Load the Python Standard and DesignScript Libraries
import sys
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# The inputs to this node will be stored as a list in the IN variables.
dataEnteringNode = IN

# Inputs (maintain original order):
MasterFamilyList = IN[0]  # List1: Master Family List (source for matches)
TakeoffList = IN[1]       # List2: Takeoff List (to find matches in Master Family List)
weight_perfect = IN[2]    # Weight for perfect matches (e.g., 1)
start_row = IN[3]         # Row number to start searching (0-indexed)

# Initialize empty output lists
matched_items = [None] * len(TakeoffList)       # For matched items from MasterFamilyList
matched_indices = [None] * len(TakeoffList)     # For the indices of the matched items in MasterFamilyList
reordered_items = [None] * len(TakeoffList)     # Reordered matches based on TakeoffList
weights = [0] * len(TakeoffList)                # Weights for each match (perfect match weight or 0)

# Function to clean a value by removing non-alphanumeric characters (except numbers) and converting to lowercase
def clean_value(v):
    if v is None:
        return ""  # Return empty string if input is None
    if isinstance(v, (int, float)):  # Convert numbers to strings without unnecessary precision
        v = str(int(v)) if float(v).is_integer() else str(v)
    else:
        v = str(v)  # Ensure the input is a string
    v = ''.join(char for char in v if char.isalnum() or char.isdigit())  # Remove non-alphanumeric characters but keep digits
    return v.lower()  # Convert to lowercase for uniformity

# Iterate through TakeoffList (List2) and check for perfect matches in MasterFamilyList (List1)
for idx, item2 in enumerate(TakeoffList):
    if item2 is None or item2 == "":
        continue  # Skip if item2 is None or empty
    
    clean_item2 = clean_value(item2)
    
    # Iterate through MasterFamilyList (List1) for potential matches, starting at start_row
    for i, item1 in enumerate(MasterFamilyList):
        if i < start_row:
            continue  # Skip rows above the start_row
        if item1 is None or item1 == "":
            continue  # Skip if item1 is None or empty
        
        clean_item1 = clean_value(item1)
        
        # Check for a perfect match
        if clean_item1 == clean_item2:
            # If a match is found, update the output lists at the original index of TakeoffList
            matched_items[idx] = MasterFamilyList[i]    # Matched item from MasterFamilyList
            matched_indices[idx] = i                    # Index of the match in MasterFamilyList
            reordered_items[idx] = MasterFamilyList[i]  # Reorder matches based on TakeoffList
            weights[idx] = weight_perfect               # Assign perfect match weight
            break

# Output tuple with matched items (from MasterFamilyList), matched indices, reordered matches (from MasterFamilyList), and weights
OUT = (matched_items, matched_indices, reordered_items, weights)
