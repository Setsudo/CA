# Import Revit API and necessary libraries
import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

# Ensure the script doesn't crash if `IN` is missing or Revit is not ready
try:
    # Get the current Revit document
    doc = DocumentManager.Instance.CurrentDBDocument

    # Main logic: Process all viewports
    viewport_ids = []
    viewport_names = []
    viewport_types = []
    view_ids = []

    # Filter to get all Viewports in the document
    collector = FilteredElementCollector(doc).OfClass(Viewport)

    for viewport in collector:
        # Get the name of the view associated with the viewport
        view_id = viewport.ViewId
        view = doc.GetElement(view_id)
        viewport_name = view.Name if view else "Unknown Name"

        # Get the type of the viewport by accessing the Element Type Name directly
        type_element = doc.GetElement(viewport.GetTypeId())
        viewport_type_name = type_element.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() if type_element else "Unknown Type"

        # Append to the output lists
        viewport_ids.append(viewport.Id.IntegerValue)
        viewport_names.append(viewport_name)
        viewport_types.append(viewport_type_name)
        view_ids.append(view_id.IntegerValue if view else "Unknown View ID")

    # Output results to Dynamo
    OUT = {
        "Viewport IDs": viewport_ids,
        "Viewport Names": viewport_names,
        "Viewport Types": viewport_types,
        "View IDs": view_ids
    }

except Exception as e:
    # Gracefully handle errors
    OUT = f"An error occurred: {e}"
