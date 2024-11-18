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
new_type_name = IN[2]  # The new type name to set (e.g., "No Label")

# Output list to store results
output_data = []

# Access the current document
doc = DocumentManager.Instance.CurrentDBDocument

# Start a transaction to modify Revit data
TransactionManager.Instance.EnsureInTransaction(doc)

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
    output_data.append(f"New Type Name to Set: {new_type_name}")

    # Find the index that matches the viewport to modify
    matching_indexes = [i for i, name in enumerate(viewport_names) if name == viewport_to_modify]
    if matching_indexes:
        output_data.append(f"Matching viewport found for modification at index(es): {matching_indexes}")
    else:
        output_data.append(f"No matching viewport found for name '{viewport_to_modify}'")

    # Collect all existing viewport types by iterating over the current viewports
    available_viewport_types = {}
    collector = FilteredElementCollector(doc).OfClass(Viewport)
    for viewport in collector:
        type_element = doc.GetElement(viewport.GetTypeId())
        type_name = type_element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        if type_name not in available_viewport_types:
            available_viewport_types[type_name] = type_element

    # List available viewport types for diagnostics
    available_type_names = list(available_viewport_types.keys())
    output_data.append(f"Available viewport types in project: {available_type_names}")

    # Find the type that matches the desired new type name
    new_type_element = available_viewport_types.get(new_type_name, None)

    if new_type_element is None:
        output_data.append(f"No viewport type with the name '{new_type_name}' was found in the project.")
    else:
        output_data.append(f"Viewport type '{new_type_name}' found, ID: {new_type_element.Id}")

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
                            # Change the type of the viewport to the desired new type
                            viewport.ChangeTypeId(new_type_element.Id)
                            output_data.append(f"Viewport ID {viewport.Id} type changed to '{new_type_name}'")
                        else:
                            output_data.append(f"Viewport with ID {viewport_ids[i]} not found or not a Viewport.")
                    except Exception as e:
                        output_data.append(f"Error processing viewport ID {viewport_ids[i]}: {str(e)}")
        else:
            output_data.append("Data lists are not of equal length. Unable to proceed.")
except Exception as e:
    output_data.append(f"Error accessing input data: {str(e)}")

# Complete the transaction
TransactionManager.Instance.TransactionTaskDone()

# Output results
OUT = output_data
