# Import Revit and Dynamo modules
import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# Inputs
input_data = IN[0]  # Expected to be a dictionary with specific keys
viewport_to_modify = IN[1]  # The name of the viewport to modify (e.g., "DSP Comp Ref")

# Output list to store results
output_data = []

# Access the current document
doc = DocumentManager.Instance.CurrentDBDocument

# Access the dictionary data using appropriate keys
try:
    # Use `.get()` to access dictionary keys to avoid KeyErrors
    view_ids = input_data.get('View IDs', [])
    viewport_ids = input_data.get('Viewport IDs', [])
    viewport_types = input_data.get('Viewport Types', [])
    viewport_names = input_data.get('Viewport Names', [])

    # Adding detailed debug messages for diagnostics
    output_data.append(f"View IDs: {view_ids}")
    output_data.append(f"Viewport IDs: {viewport_ids}")
    output_data.append(f"Viewport Types: {viewport_types}")
    output_data.append(f"Viewport Names: {viewport_names}")
    output_data.append(f"Viewport to Modify: {viewport_to_modify}")

    # Find the index that matches the viewport to modify
    matching_indexes = [i for i, name in enumerate(viewport_names) if name == viewport_to_modify]
    if matching_indexes:
        output_data.append(f"Matching viewport found for modification at index(es): {matching_indexes}")
    else:
        output_data.append(f"No matching viewport found for name '{viewport_to_modify}'")

    # Ensure all lists are of the same length
    if len(view_ids) == len(viewport_ids) == len(viewport_types) == len(viewport_names):
        for i in range(len(viewport_names)):
            # Only proceed if we have a matching index for modification
            if i in matching_indexes:
                try:
                    # Get the viewport element
                    viewport_id = ElementId(viewport_ids[i])
                    viewport = doc.GetElement(viewport_id)

                    if viewport and isinstance(viewport, Viewport):
                        # List all parameters of the viewport element
                        param_info_list = []
                        for param in viewport.Parameters:
                            param_name = param.Definition.Name
                            param_storage_type = param.StorageType
                            param_value = None
                            
                            if param_storage_type == StorageType.String:
                                param_value = param.AsString()
                            elif param_storage_type == StorageType.Integer:
                                param_value = param.AsInteger()
                            elif param_storage_type == StorageType.Double:
                                param_value = param.AsDouble()
                            elif param_storage_type == StorageType.ElementId:
                                param_value = param.AsElementId().IntegerValue

                            param_info_list.append(f"Parameter: {param_name}, Storage Type: {param_storage_type}, Value: {param_value}")

                        output_data.append(f"Parameters of Viewport ID {viewport.Id}: {param_info_list}")
                    else:
                        output_data.append(f"Viewport with ID {viewport_ids[i]} not found or not a Viewport.")
                except Exception as e:
                    output_data.append(f"Error processing viewport ID {viewport_ids[i]}: {str(e)}")
    else:
        output_data.append("Data lists are not of equal length. Unable to proceed.")
except Exception as e:
    output_data.append(f"Error accessing input data: {str(e)}")

# Output results
OUT = output_data
