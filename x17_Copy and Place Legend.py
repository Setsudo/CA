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
legend_name = IN[1]  # Name of the Legend View to extract
sheet_name = IN[2]   # Name of the sheet to place the legend on
placement_location = IN[3]  # XYZ coordinates for the placement of the legend (tuple/list)

copied_legend_id = None
legend_on_sheet_id = None

try:
    # Check if the legend view already exists in the current project
    existing_legend = next((view for view in FilteredElementCollector(doc).OfClass(View)
                            if view.ViewType == ViewType.Legend and view.Name == legend_name), None)

    if existing_legend:
        copied_legend = existing_legend
    else:
        # Open the Revit template document
        app = doc.Application
        template_doc = app.OpenDocumentFile(template_path)

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
        finally:
            # Ensure the template document is closed properly
            if template_doc.IsValidObject:
                template_doc.Close(False)

    # Locate the sheet where the legend should be placed
    sheet = next((s for s in FilteredElementCollector(doc).OfClass(ViewSheet) if s.Name == sheet_name), None)

    if sheet is None:
        OUT = f"Error: Sheet named '{sheet_name}' not found in the current project."
    else:
        # Start a transaction to either place or move the legend on the sheet
        TransactionManager.Instance.EnsureInTransaction(doc)

        # Convert placement_location to XYZ
        x, y, z = placement_location
        position = XYZ(x, y, z)

        try:
            # Place the legend view on the sheet at the specified location
            viewport = Viewport.Create(doc, sheet.Id, copied_legend.Id, position)

            if viewport is None:
                OUT = f"Error: Could not place the legend '{legend_name}' on sheet '{sheet_name}'."
            else:
                legend_on_sheet_id = viewport.Id
                OUT = [
                    f"Legend '{legend_name}' successfully placed on sheet '{sheet_name}' at position ({x}, {y}, {z}).",
                    copied_legend_id.IntegerValue,
                    legend_on_sheet_id.IntegerValue
                ]
        except Exception as e:
            TransactionManager.Instance.ForceCloseTransaction()
            OUT = f"Error during placement: {e}"

        TransactionManager.Instance.TransactionTaskDone()

except Exception as e:
    OUT = f"Error: {e}"

# Output only the relevant result
OUT = OUT
