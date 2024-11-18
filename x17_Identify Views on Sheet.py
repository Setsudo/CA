# Import Revit and Dynamo modules
import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# Inputs
sheet_name = IN[0]  # The name of the sheet to find viewports on

# Output list
output_data = []

# Access the current document
doc = DocumentManager.Instance.CurrentDBDocument

try:
    # Find the sheet with the given name
    sheet = None
    sheet_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType()

    for s in sheet_collector:
        if s.Name == sheet_name:
            sheet = s
            break

    if sheet is None:
        output_data.append(f"No sheet found with the name '{sheet_name}'.")
    else:
        # Get viewports on the sheet
        viewport_ids = sheet.GetAllViewports()

        if len(viewport_ids) == 0:
            output_data.append(f"No viewports found on sheet '{sheet_name}'.")
        else:
            output_data.append(f"Found {len(viewport_ids)} viewports on sheet '{sheet_name}'.")

            # Iterate over the viewport IDs and get the corresponding Viewport elements
            viewports = []
            for vp_id in viewport_ids:
                try:
                    viewport = doc.GetElement(vp_id)
                    if viewport:
                        viewports.append(viewport)
                        view_id = viewport.ViewId
                        view = doc.GetElement(view_id)
                        view_name = view.Name if view else "Unknown View"

                        output_data.append(f"Viewport ID: {viewport.Id}, View Name: {view_name}, View Type: {type(view).__name__}")
                except Exception as ve:
                    output_data.append(f"Error retrieving viewport with ID {vp_id}: {str(ve)}")

except Exception as e:
    output_data.append(f"General error accessing data: {str(e)}")

# Output results
OUT = output_data
