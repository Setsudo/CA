import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('System')

from System.Collections.Generic import List
from Autodesk.Revit.DB import *  # Import all necessary Revit DB types
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Get the current Revit document (the active project)
doc = DocumentManager.Instance.CurrentDBDocument

# Inputs from Dynamo
template_path = IN[0]  # File path to the Revit template (RVT) file
legend_name = IN[1]  # Name of the Legend View to extract
sheet_name = IN[2]   # Name of the sheet to place the legend on
placement_location = IN[3]  # XYZ coordinates for the placement of the legend (tuple/list)

debug_info = []  # Using a list to make further processing in Dynamo easier

debug_info.append("Step: Initialization")

try:
    # Step 1: Remove any existing legend from the project
    TransactionManager.Instance.EnsureInTransaction(doc)
    existing_legend = next((view for view in FilteredElementCollector(doc).OfClass(View)
                            if view.ViewType == ViewType.Legend and view.Name == legend_name), None)

    if existing_legend:
        doc.Delete(existing_legend.Id)
        debug_info.append("Step: Removed existing legend (if any)")
    TransactionManager.Instance.TransactionTaskDone()

    # Step 2: Open the Revit template document
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
        if template_doc.IsValidObject:
            template_doc.Close(False)
        debug_info.append("Step: Template document closed")

    # Step 3: Locate the sheet where the legend should be placed
    sheet = next((s for s in FilteredElementCollector(doc).OfClass(ViewSheet) if s.Name == sheet_name), None)

    if sheet is None:
        OUT = f"Error: Sheet named '{sheet_name}' not found in the current project."
    else:
        # Start a transaction to place the legend on the sheet
        TransactionManager.Instance.EnsureInTransaction(doc)
        debug_info.append("Step: Transaction started for placing legend")

        # Convert placement_location to XYZ
        x, y, z = placement_location
        position = XYZ(x, y, z)

        try:
            # Place the legend view on the sheet using Viewport.Create
            viewport = Viewport.Create(doc, sheet.Id, copied_legend.Id, position)

            if viewport is None:
                debug_info.append(f"Error: Could not place the legend '{legend_name}' on sheet '{sheet_name}'. Viewport is None.")
            else:
                # Successfully created the viewport
                debug_info.append(f"Viewport Element ID: {viewport.Id.IntegerValue}")
                debug_info.append("Step: Viewport successfully created")

        except Exception as e:
            debug_info.append(f"Step: Error during viewport placement: {e}")

        # Complete the transaction for placing the legend
        TransactionManager.Instance.TransactionTaskDone()
        debug_info.append("Step: Transaction completed for placing legend")

except Exception as e:
    debug_info.append(f"Step: General error: {e}")
    OUT = f"Error: {e}"

# Output only the relevant result, including debug information
OUT = debug_info
