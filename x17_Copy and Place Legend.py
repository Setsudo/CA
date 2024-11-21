import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('System')

from System import Guid
from System.Collections.Generic import List
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Get the current Revit document (the active project)
doc = DocumentManager.Instance.CurrentDBDocument

# Inputs from Dynamo
template_path = IN[0]  # File path to the Revit template (RVT) file
legend_name = IN[1]
sheet_name = IN[2]   # Name of the sheet to place the legend on
placement_location = IN[3]  # XYZ coordinates for the placement of the legend (tuple/list)
append_text = IN[4]  # Text to append when renaming the existing legend  # Name of the Legend View to extract

copied_legend_id = None
legend_on_sheet_id = None

debug_info = []  # Using a list to make further processing in Dynamo easier

debug_info.append("Step: Initialization")

try:
    # Start a transaction to remove any existing legend with the same name
    TransactionManager.Instance.EnsureInTransaction(doc)
    
    existing_legend = next((view for view in FilteredElementCollector(doc).OfClass(View)
                            if view.ViewType == ViewType.Legend and view.Name == legend_name), None)

    if existing_legend:
        # Rename the existing legend to mark it as old
        existing_legend.Name = f"{existing_legend.Name} {append_text}"
        
        # Find the viewport associated with the existing legend
        existing_viewport = next((vp for vp in FilteredElementCollector(doc).OfClass(Viewport)
                                  if vp.ViewId == existing_legend.Id), None)
        
        # Move the viewport upwards by a few inches (assuming 1 inch = 0.0833 feet)
        if existing_viewport:
            move_vector = XYZ(0, 0.5, 0)  # Move upwards by 6 inches (0.5 feet)
            ElementTransformUtils.MoveElement(doc, existing_viewport.Id, move_vector)
        
    TransactionManager.Instance.TransactionTaskDone()
    debug_info.append("Step: Removed existing legend (if any)")

    # Open the Revit template document
    app = doc.Application
    template_doc = app.OpenDocumentFile(template_path)
    debug_info.append("Step: Template document opened")

    try:
        # Find the legend view by name in the template file
        legend_view = next((view for view in FilteredElementCollector(template_doc).OfClass(View)
                            if view.ViewType == ViewType.Legend and view.Name == legend_name), None)

        if legend_view is None:
            OUT = f"Error: Legend view named '{legend_name}' not found in the template."
        else:
            # Start a transaction to copy the legend into the current document
            TransactionManager.Instance.EnsureInTransaction(doc)

            # Copy the legend to the current project
            element_ids = List[ElementId]([legend_view.Id])
            copied_ids = ElementTransformUtils.CopyElements(template_doc, element_ids, doc, Transform.Identity, CopyPasteOptions())

            TransactionManager.Instance.TransactionTaskDone()

            # Get the copied legend
            copied_legend_id = copied_ids[0]
            copied_legend = doc.GetElement(copied_legend_id)
            debug_info.append("Step: Copied legend into the current project")
            debug_info.append(f"Copied Legend ID: {copied_legend_id.IntegerValue}")
    finally:
        # Ensure the template document is closed properly
        if template_doc.IsValidObject:
            template_doc.Close(False)
        debug_info.append("Step: Template document closed")

    # Locate the sheet where the legend should be placed
    sheet = next((s for s in FilteredElementCollector(doc).OfClass(ViewSheet) if s.Name == sheet_name), None)

    if sheet is None:
        OUT = f"Error: Sheet named '{sheet_name}' not found in the current project."
    else:
        # Start a transaction to either place or move the legend on the sheet
        TransactionManager.Instance.EnsureInTransaction(doc)
        debug_info.append("Step: Transaction started for placing legend")

        # Convert placement_location to XYZ
        x, y, z = placement_location
        position = XYZ(x, y, z)

        try:
            # Place the legend view on the sheet using Viewport.Create
            viewport = Viewport.Create(doc, sheet.Id, copied_legend.Id, position)

            if viewport is None:
                OUT = f"Error: Could not place the legend '{legend_name}' on sheet '{sheet_name}'."
            else:
                legend_on_sheet_id = viewport.Id

                # Simple output for viewport creation success
                debug_info.append(f"Viewport Element ID: {legend_on_sheet_id.IntegerValue}")
                debug_info.append("Step: Viewport successfully created")

                OUT = debug_info
        except Exception as e:
            TransactionManager.Instance.ForceCloseTransaction()
            debug_info.append(f"Step: Error during viewport placement: {e}")
            OUT = f"Error during placement: {e}"

        TransactionManager.Instance.TransactionTaskDone()
        debug_info.append("Step: Transaction completed for placing legend")

except Exception as e:
    debug_info.append(f"Step: Error: {e}")
    OUT = f"Error: {e}"

# Output only the relevant result, including debug information
OUT = OUT
