# Import Revit and Dynamo modules
import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# Inputs
sheet_name = IN[0]  # The name of the sheet to find viewports on
new_type_name = IN[1]  # The new type name to set (e.g., "no label")

# Output list to store results
output_data = []

# Access the current document
doc = DocumentManager.Instance.CurrentDBDocument

# Start a transaction to modify Revit data
TransactionManager.Instance.EnsureInTransaction(doc)

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

            # Iterate over the viewport IDs to find the desired viewport containing the legend view
            viewport_to_modify = None
            for vp_id in viewport_ids:
                viewport = doc.GetElement(vp_id)
                view_id = viewport.ViewId
                view = doc.GetElement(view_id)
                
                # Check if this is the legend we want to modify
                if view.Name == "DSP Comp Ref":
                    output_data.append(f"Found Viewport containing the Legend View named '{view.Name}', Viewport ID: {viewport.Id.IntegerValue}")
                    viewport_to_modify = viewport
                    break

            if viewport_to_modify:
                # Collect the available viewport type information from all viewports
                viewport_type_dict = {}
                collector = FilteredElementCollector(doc).OfClass(Viewport)

                # Iterate through collected elements to gather viewport types
                for viewport in collector:
                    type_element = doc.GetElement(viewport.GetTypeId())
                    if type_element:
                        type_name = type_element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
                        if type_name and isinstance(type_name, str):
                            type_name_lower = type_name.lower()
                            if type_name_lower not in viewport_type_dict:
                                viewport_type_dict[type_name_lower] = type_element

                # List all collected viewport types for debugging
                collected_types = [key for key in viewport_type_dict.keys()]
                output_data.append(f"Collected viewport types: {collected_types}")

                # Normalize new type name for comparison (case insensitive)
                new_type_name_normalized = new_type_name.lower()

                # Check if the new type name exists in the project
                new_type_element = viewport_type_dict.get(new_type_name_normalized, None)

                if new_type_element is None:
                    output_data.append(f"No viewport type with the name '{new_type_name}' was found in the gathered viewport types.")
                else:
                    output_data.append(f"Viewport type '{new_type_name}' found, ID: {new_type_element.Id}")

                    # Deleting the old viewport and re-creating with new type
                    try:
                        # Capture existing location of viewport to recreate at same location
                        bbox = viewport_to_modify.GetBoxCenter()
                        view_id = viewport_to_modify.ViewId

                        # Delete the old viewport
                        doc.Delete(viewport_to_modify.Id)
                        output_data.append(f"Deleted original Viewport ID {viewport_to_modify.Id}.")

                        # Create a new viewport with the desired type
                        new_viewport = Viewport.Create(doc, sheet.Id, view_id, bbox)
                        new_viewport.ChangeTypeId(new_type_element.Id)

                        output_data.append(f"Re-created viewport with new type '{new_type_name}' successfully.")
                    except Exception as e:
                        output_data.append(f"Error re-creating viewport ID {viewport_to_modify.Id}: {str(e)}")

except Exception as e:
    output_data.append(f"General error accessing data: {str(e)}")

# Complete the transaction
TransactionManager.Instance.TransactionTaskDone()

# Output results
OUT = output_data
