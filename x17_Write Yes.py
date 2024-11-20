# Load the Python Standard and DesignScript Libraries
import sys
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# The inputs to this node will be stored as a list in the IN variables.
dataEnteringNode = IN

# Inputs
Indices = IN[0]         # Indices with row numbers where "Yes" should be written (and None elsewhere)
yes_value = IN[1]       # Value to write for "Yes" entries
no_value = IN[2]        # Value to write for "No" entries
drop_rows = IN[3]       # Number of rows to drop from the beginning

# Determine the length of the output list
list_length = len(Indices)

# Initialize output list with "No" values for each row
outputList = [no_value] * list_length

# Iterate through Indices and replace the default "No" values with "Yes" at specified positions
for i in range(list_length):
    if Indices[i] is not None and i >= drop_rows:
        # Write the "Yes" value at the specified index
        outputList[i] = yes_value

# Output the final list with "Yes" and "No" values based on the indices
OUT = outputList
