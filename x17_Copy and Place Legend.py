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
legend_name = IN[1].strip().lower()  # Name of the Legend View to extract, strip and lower for consistency
sheet_name = IN[2].strip()  # Name of the sheet to place the legend on
placement_location = IN[3]  # XYZ coordinates for the placement of the legend (tuple/list)
append_text = IN[4]  # Text to append when renaming the existing legend
new_position = IN[5]  # New XYZ coordinates for the existing legend (tuple/list)
existing_legend_name = [name.strip().lower() for name in IN[6]] if isinstance(IN[6], list) else [IN[6].strip().lower()]  # Name(s) of the existing Legend View to search for in the current document, processed to list, stripped and lowered

# Initialize debug_info
debug_info = []
debug_info.append("Step: Initialization")

try:
    debug_info.append(f"Step: existing_legend_name input processed as a list with {len(existing_legend_name)} items.")

    # Start a transaction to rename and move any existing legends with the same name
    TransactionManager.Instance.EnsureInTransaction(doc)
    for legend_name_to_find in existing_legend_name:
        debug_info.append(f"Step: Processing existing legend with name: '{legend_name_to_find}'")
        
        existing_legend = next((view for view in FilteredElementCollector(doc).OfClass(View) if view.ViewType == ViewType.Legend and view.Name.strip().lower() == legend_name_to_find), None)
        
        if existing_legend is None:
            debug_info.append(f"Step: No existing legend found with the given name '{legend_name_to_find}'. Please verify the name.")
        else:
            # Rename the existing legend to mark it as old
            old_name = existing_legend.Name
            existing_legend.Name = f"{existing_legend.Name} {append_text}"
            debug_info.append(f"Step: Existing legend renamed from '{old_name}' to '{existing_legend.Name}'")

            # Find the viewport associated with the existing legend
            existing_viewport = next((vp for vp in FilteredElementCollector(doc).OfClass(Viewport) if vp.ViewId == existing_legend.Id), None)
            
            if existing_viewport is None:
                debug_info.append(f"Step: No existing viewport found for the renamed legend '{existing_legend.Name}'.")
            else:
                # Move the viewport to the new position
                x, y, z = new_position
                new_position_xyz = XYZ(x, y, z)
                current_position = existing_viewport.GetBoxCenter()
                debug_info.append(f"Step: Current viewport position before move: ({current_position.X}, {current_position.Y}, {current_position.Z})")

                try:
                    existing_viewport.SetBoxCenter(new_position_xyz)
                    debug_info.append(f"Step: Existing viewport moved to new position: ({x}, {y}, {z})")
                except Exception as e:
                    debug_info.append(f"Step: Error occurred while moving viewport: {e}")

    TransactionManager.Instance.TransactionTaskDone()
    debug_info.append("Step: Completed renaming and moving the existing legends (if any)")

    # Open the Revit template document
    app = doc.Application
    template_doc = app.OpenDocumentFile(template_path)
    debug_info.append("Step: Template document opened successfully")

    try:
        # Find the legend view by name in the template file
        legend_view = next((view for view in FilteredElementCollector(template_doc).OfClass(View) if view.ViewType == ViewType.Legend and view.Name.strip().lower() == legend_name), None)

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
            debug_info.append("Step: Legend view copied from template into the current project")
            debug_info.append(f"Copied Legend ID: {copied_legend_id.IntegerValue}")
    finally:
        # Ensure the template document is closed properly
        if template_doc.IsValidObject:
            template_doc.Close(False)
        debug_info.append("Step: Template document closed")

    # Locate the sheet where the legend should be placed
    sheet = next((s for s in FilteredElementCollector(doc).OfClass(ViewSheet) if s.Name.strip().lower() == sheet_name.lower()), None)

    if sheet is None:
        OUT = f"Error: Sheet named '{sheet_name}' not found in the current project."
    else:
        # Check if there is already a viewport for the same legend on the sheet
        existing_viewport_on_sheet = next((vp for vp in FilteredElementCollector(doc).OfClass(Viewport) if vp.SheetId == sheet.Id and vp.ViewId == copied_legend.Id), None)
        if existing_viewport_on_sheet:
            debug_info.append(f"Step: A viewport for the legend '{legend_name}' already exists on the sheet '{sheet_name}'. Skipping placement.")
        else:
            # Start a transaction to place the legend on the sheet
            TransactionManager.Instance.EnsureInTransaction(doc)
            debug_info.append("Step: Transaction started for placing new legend on the specified sheet")

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
                    debug_info.append(f"Step: Viewport for new legend placed successfully with Element ID: {legend_on_sheet_id.IntegerValue}")
                    debug_info.append("Step: New legend viewport created and placed at the specified position")

                    OUT = debug_info
            except Exception as e:
                TransactionManager.Instance.ForceCloseTransaction()
                debug_info.append(f"Step: Error during viewport placement: {e}")
                OUT = f"Error during placement: {e}"

            TransactionManager.Instance.TransactionTaskDone()
            debug_info.append("Step: Transaction completed successfully for placing the new legend")

except Exception as e:
    debug_info.append(f"Step: An error occurred: {e}")
    OUT = f"Error: {e}"

# Output only the relevant result, including debug information
OUT = debug_info
