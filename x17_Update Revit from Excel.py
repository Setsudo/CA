import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# Inputs from Dynamo
revit_data_list = IN[0]  # Expected to be a list of Revit-related data structures
excel_data_list = IN[1]  # Expected to be a list of Excel-related data structures

# Output container
OUT = []

# Access the active Revit document
doc = DocumentManager.Instance.CurrentDBDocument

def find_subheader_index(data_list, subheader):
    """Find the index of the subheader in the data list."""
    for index, item in enumerate(data_list):
        if isinstance(item, list) and len(item) > 1 and item[1] == subheader:
            return index
    return None

def update_revit_data(revit_data, excel_data):
    """Update the Revit data list with values from the Excel data list based on the Sub-Header key."""
    for excel_item in excel_data:
        if isinstance(excel_item, list) and len(excel_item) > 1:
            subheader = excel_item[1]
            revit_index = find_subheader_index(revit_data, subheader)
            if revit_index is not None:
                revit_item = revit_data[revit_index]
                for i in range(2, len(excel_item)):
                    if isinstance(excel_item[i], list) and len(excel_item[i]) > 1:
                        key = excel_item[i][0]
                        value = excel_item[i][1]
                        for j in range(2, len(revit_item)):
                            if isinstance(revit_item[j], list) and len(revit_item[j]) > 1 and revit_item[j][0] == key:
                                revit_item[j][1] = value

# Update the Revit data list with Excel data
try:
    update_revit_data(revit_data_list, excel_data_list)
    OUT.append("Update completed for input: revit_data_list with excel_data_list")
    OUT.append(revit_data_list)
except Exception as e:
    OUT.append(f"Error during update of revit_data_list with excel_data_list: {str(e)}")