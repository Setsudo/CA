import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Get the current Revit document
doc = DocumentManager.Instance.CurrentDBDocument

# Inputs from Dynamo
legend_on_sheet_id = IN[0]  # Element ID of the legend on the sheet

try:
    # Convert input to ElementId
    legend_on_sheet_element_id = ElementId(legend_on_sheet_id)
    legend_on_sheet = doc.GetElement(legend_on_sheet_element_id)

    # Verify if the element is found
    if legend_on_sheet is None:
        OUT = f"Error: No element found with ID {legend_on_sheet_id}."
    else:
        # Output the type of the element to confirm it
        element_category = legend_on_sheet.Category.Name if legend_on_sheet.Category else "<None>"
        element_type_name = legend_on_sheet.GetType().Name
        element_name = legend_on_sheet.Name if hasattr(legend_on_sheet, 'Name') else "<No Name>"

        # Output information to verify the correct element is being targeted
        debug_info = {
            "legend_on_sheet_id": legend_on_sheet_id,
            "element_name": element_name,
            "element_type_name": element_type_name,
            "element_category": element_category
        }

        OUT = f"Debug Info: {debug_info}"

except Exception as e:
    OUT = f"Error: {e}"

# Output the result
OUT = OUT
