import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('System')

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
new_type_name = "No Label"  # Viewport type name we want to set

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
        doc.Delete(existing_legend.Id)
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
        # Start a transaction to place the legend on the sheet
        TransactionManager.Instance.EnsureInTransaction(doc)
        debug_info.append("Step: Transaction started for placing legend")

        # Convert placement_location to XYZ
        x, y, z = placement_location
        position = XYZ(x, y, z)

        try:
            # Place the legend view on the sheet using Viewport.Create
            viewport = Viewport.Create(doc, sheet.Id, copied_legend.Id, position)

            # Check if viewport was created
            if viewport is None:
                debug_info.append(f"Error: Could not place the legend '{legend_name}' on sheet '{sheet_name}'. Viewport is None.")
            else:
                # Capture Viewport ID
                legend_on_sheet_id = viewport.Id
                debug_info.append(f"Viewport Element ID: {legend_on_sheet_id.IntegerValue}")
                debug_info.append("Step: Viewport successfully created")

                # Check if the viewport exists in the document
                created_viewport = doc.GetElement(legend_on_sheet_id)
                if created_viewport is None or not created_viewport.IsValidObject:
                    debug_info.append("Error: Created viewport is not valid or could not be retrieved.")
                else:
                    debug_info.append(f"Created viewport is valid: Viewport ID {created_viewport.Id.IntegerValue}")

        except Exception as e:
            TransactionManager.Instance.ForceCloseTransaction()
            debug_info.append(f"Step: Error during viewport placement: {e}")
            OUT = f"Error during placement: {e}"

        # Commit the transaction for placing the legend
        TransactionManager.Instance.TransactionTaskDone()
        debug_info.append("Step: Transaction completed for placing legend")

    # Step 2: Start a new transaction to change the viewport type to "No Label"
    if legend_on_sheet_id:
        try:
            TransactionManager.Instance.EnsureInTransaction(doc)

            # Collect available viewport types and find the "No Label" type
            collector = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_Viewports)
            viewport_type = None

            for symbol in collector:
                type_name = symbol.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
                if type_name and type_name.lower() == new_type_name.lower():
                    viewport_type = symbol
                    break

            if viewport_type is None:
                debug_info.append(f"Error: Viewport type named '{new_type_name}' not found in the current project.")
            else:
                debug_info.append(f"Viewport type '{new_type_name}' found, ID: {viewport_type.Id}")

                # Get the viewport element that was created
                viewport = doc.GetElement(legend_on_sheet_id)

                # Activate the viewport type before setting it
                if not viewport_type.IsActive:
                    viewport_type.Activate()
                    doc.Regenerate()

                # Change the type to the desired symbol type (as FamilySymbols control Viewport types)
                try:
                    viewport.ChangeTypeId(viewport_type.Id)
                    debug_info.append(f"Viewport ID {viewport.Id} type successfully changed to '{new_type_name}'.")
                except Exception as e:
                    debug_info.append(f"Error changing type of viewport ID {viewport.Id}: {str(e)}")

        except Exception as e:
            debug_info.append(f"Step: Error during viewport type change: {e}")
        finally:
            TransactionManager.Instance.TransactionTaskDone()
            debug_info.append("Step: Transaction completed for changing viewport type")

except Exception as e:
    debug_info.append(f"Step: General error: {e}")
    OUT = f"Error: {e}"

# Output only the relevant result, including debug information
OUT = debug_info
