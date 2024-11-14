# Load the Python Standard and DesignScript Libraries
import sys
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# The inputs to this node will be stored as a list in the IN variables.
dataEnteringNode = IN

# Inputs: Two lists to combine
list1 = IN[0]  # First input list (e.g., Instance Parameters)
list2 = IN[1]  # Second input list (e.g., Type Parameters)

# Ensure inputs are lists (handles Dynamo data structure issues)
list1 = list1 if isinstance(list1, list) else []
list2 = list2 if isinstance(list2, list) else []

# Combine logic: Preserving original indices and prioritizing non-null values
combined_list = []
max_length = max(len(list1), len(list2))

for i in range(max_length):
    # Handle out-of-range indices gracefully
    val1 = list1[i] if i < len(list1) else None
    val2 = list2[i] if i < len(list2) else None

    # Prioritize non-null values and handle conflicts
    if val1 is not None and val2 is not None:
        if val1 == val2:
            combined_list.append(val1)  # If both values are the same, use it
        else:
            combined_list.append(val1)  # Prioritize list1's value
    elif val1 is not None:
        combined_list.append(val1)  # Use value from list1 if list2 is null
    elif val2 is not None:
        combined_list.append(val2)  # Use value from list2 if list1 is null
    else:
        combined_list.append(None)  # Both are null, append None

# Assign your output to the OUT variable
OUT = combined_list
