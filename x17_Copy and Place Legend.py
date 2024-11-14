import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('System')

from System import Guid
from System.Collections.Generic import List  # Fix: Import List from System.Collections.Generic
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Get the current Revit document (the active project)
doc = DocumentManager.Instance.CurrentDBDocument

# Inputs from Dynamo
template_path = IN[0]  # File path to the Revit template (RVT) file
legend_name = IN[1]  # Name of the Legend View to extract
sheet_name = IN[2]   # Name of the sheet to place the legend on
placement_location = IN[3]  # XYZ coordinates for the placement of the legend

# Open the Revit template document
try:
    # Check if the legend view already exists in the current project
    existing_legend = None
    for view in FilteredElementCollector(doc).OfClass(View):
        if view.ViewType == ViewType.Legend and view.Name == legend_name:
            existing_legend = view
            break

    if existing_legend is not None:
        copied_legend = existing_legend
    else:
        app = doc.Application
        template_doc = app.OpenDocumentFile(template_path)

        # Find the legend view by name in the template file
        legend_view = None
        for view in FilteredElementCollector(template_doc).OfClass(View):
            if view.ViewType == ViewType.Legend and view.Name == legend_name:
                legend_view = view
                break

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

        # Close the template document if it is not the active document
        if template_doc.IsReadOnly:
            template_doc.Close(False)

    # Locate the sheet where the legend should be placed
    sheet = None
    for s in FilteredElementCollector(doc).OfClass(ViewSheet):
        if s.Name == sheet_name:
            sheet = s
            break

    if sheet is None:
        OUT = f"Error: Sheet named '{sheet_name}' not found in the current project."
    else:
        # Check if the legend is already on the sheet
        legend_on_sheet = None
        for vp_id in sheet.GetAllViewports():
            viewport = doc.GetElement(vp_id)
            if viewport.ViewId == copied_legend.Id:
                legend_on_sheet = viewport
                break

        # Start a transaction to either place or move the legend on the sheet
        TransactionManager.Instance.EnsureInTransaction(doc)

        # Convert placement_location to XYZ
        x, y, z = placement_location
        position = XYZ(x, y, z)

        if legend_on_sheet:
            # Move the existing legend to the new position
            try:
                legend_on_sheet.SetBoxCenter(position)
                OUT = f"Legend '{legend_name}' position updated on sheet '{sheet_name}' to ({x}, {y}, {z})."
            except Exception as e:
                OUT = f"Error: {e}"
        else:
            # Place the legend view on the sheet at the specified location
            try:
                # Use Viewport.Create to place the legend on the sheet
                viewport = Viewport.Create(doc, sheet.Id, copied_legend.Id, position)

                if viewport is None:
                    OUT = f"Error: Could not place the legend '{legend_name}' on sheet '{sheet_name}'."
                else:
                    OUT = f"Legend '{legend_name}' successfully placed on sheet '{sheet_name}' at position ({x}, {y}, {z})."

            except Exception as e:
                TransactionManager.Instance.ForceCloseTransaction()
                OUT = f"Error: {e}"

        TransactionManager.Instance.TransactionTaskDone()

except Exception as e:
    OUT = f"Error: {e}"
