# Import Revit and Dynamo modules
import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# Inputs
input_data = IN[0]  # Expected to be a dictionary with specific keys

# Output list to store results
output_data = []

# Access the current document
doc = DocumentManager.Instance.CurrentDBDocument

# Start a transaction to modify Revit data
TransactionManager.Instance.EnsureInTransaction(doc)

# Access the dictionary data using appropriate keys
try:
    view_ids = input_data.get('View IDs', [])
    viewport_ids = input_data.get('Viewport IDs', [])
    viewport_types = input_data.get('Viewport Types', [])
    viewport_names = input_data.get('Viewport Names', [])

    # Ensure all lists are of the same length
    if len(view_ids) == len(viewport_ids) == len(viewport_types) == len(viewport_names):
        for i in range(len(viewport_names)):
            if viewport_names[i] == "DSP Comp Ref":
                try:
                    viewport_id = ElementId(viewport_ids[i])
                    viewport = doc.GetElement(viewport_id)

                    if viewport and isinstance(viewport, Viewport):
                        # Access the Viewport Label parameter (if this isn't correct, we'll need to investigate further)
                        param = viewport.get_Parameter(BuiltInParameter.VIEWPORT_LABEL)

                        if param and not param.IsReadOnly:
                            # Change the parameter value to "No Label"
                            param.Set("No Label")
                            output_data.append(f"Viewport ID {viewport.Id} changed to 'No Label'")
                        else:
                            output_data.append(f"Viewport ID {viewport.Id} has no editable 'VIEWPORT_LABEL' parameter.")
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
