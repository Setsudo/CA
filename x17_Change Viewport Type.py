# Reference Dynamo nodes and necessary Revit API libraries
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.DB import *

# Get the current Revit document
doc = DocumentManager.Instance.CurrentDBDocument

# Input data - using the output from the previous Python script in Dynamo
data = IN[0]  # Assuming IN[0] is the output from the previous script

# Start a transaction to make changes to the document
t = Transaction(doc, "Update Viewport Type")
t.Start()

try:
    # Loop over the data, assuming the viewport type information is in the 4th sublist (index 3)
    view_types = data[0][3]
    
    for index, view_type in enumerate(view_types):
        # If the type is "DSP Comp Ref", change it to "No Label"
        if view_type == "DSP Comp Ref":
            # Update the data structure (for internal consistency)
            view_types[index] = "No Label"

            # Get all Viewport elements in the model
            viewports = FilteredElementCollector(doc).OfClass(Viewport).ToElements()

            # Find the matching viewport and change its type
            for viewport in viewports:
                # Check if this viewport name matches the one to be updated
                if viewport.Name == "DSP Comp Ref":
                    # Change the name to "No Label" (or update type if more appropriate)
                    viewport.get_Parameter(BuiltInParameter.VIEWPORT_LABEL).Set("No Label")
                    print(f"Viewport '{viewport.Id}' updated to 'No Label'.")

    # Commit the transaction after successful modification
    t.Commit()
    print("Viewport type updated successfully.")
except Exception as e:
    # Rollback if any error occurs
    t.RollBack()
    print(f"Error updating viewport type: {e}")

# Output the modified data structure
OUT = data
