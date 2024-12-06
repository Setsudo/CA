import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Importing Revit Nodes
clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Import Revit API
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# Main function for reformatting list structure
def reformat_list_structure(input_list):
    reformatted_list = []
    
    for sublist in input_list:
        # Ensure sublist is a list
        if isinstance(sublist, list):
            sub_header = None
            rest_items = []
            
            # Loop through each item in the sublist
            for item in sublist:
                # Extract the Sub-Header if present
                if isinstance(item, list) and len(item) > 1 and item[0] == "Sub-Header":
                    sub_header = item  # Retain the entire Sub-Header list, including the label
                else:
                    rest_items.append(item)
            
            # If a Sub-Header was found, add it to the reformatted list as the top-level key with the rest of the items
            if sub_header:
                reformatted_list.append([sub_header[0], sub_header[1], rest_items])
    
    return reformatted_list

# Inputs from Dynamo
input_list = IN[0]

# Perform the reformatting
output_list = reformat_list_structure(input_list)

# Assign the output to Dynamo
OUT = output_list
