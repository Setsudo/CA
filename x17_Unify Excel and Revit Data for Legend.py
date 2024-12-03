import clr

# Import Revit API
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Access the active Revit document
doc = DocumentManager.Instance.CurrentDBDocument

# Inputs
excel_data = IN[0]  # Data from Excel
revit_legend = IN[1]  # Existing Revit Legend data structure
legend_view_id = UnwrapElement(IN[2])  # Legend View Element ID

# Function to update legend data
def update_legend_with_excel(excel_data, revit_legend):
    updated_legend = []

    # Iterate through each item in the Revit legend
    for revit_item in revit_legend[0]:
        # Each item is expected to have the structure: [Title, [Metrics]]
        title = revit_item[0]
        metrics = revit_item[1]

        # Search for a matching title in the Excel data
        matching_excel_item = None
        for excel_item in excel_data:
            if title == excel_item[0]:
                matching_excel_item = excel_item
                break

        # If a match is found, update the metrics
        if matching_excel_item:
            new_metrics = matching_excel_item[1]
            metrics[0] = new_metrics[0]  # LF or DR
            metrics[1] = new_metrics[1]  # First value
            metrics[2] = new_metrics[2]  # Second value
            metrics[3] = new_metrics[3]  # Third value

        # Append the updated item to the updated legend list
        updated_legend.append([title, metrics])

    return updated_legend

# Process and update the Legend data
updated_legend = update_legend_with_excel(excel_data, revit_legend)

# Write back to Revit
TransactionManager.Instance.EnsureInTransaction(doc)

# Collect all text notes in the specified legend view
collector = FilteredElementCollector(doc, legend_view_id).OfClass(TextNote).ToElements()

# Iterate through updated legend data and update corresponding text notes in Revit
for revit_item in updated_legend:
    title = revit_item[0]
    metrics = revit_item[1]

    # Construct the updated text for each legend item
    updated_text = f"{title}\n{metrics[0]} {metrics[1]} {metrics[2]} {metrics[3]}"

    for text_note in collector:
        # Update the corresponding text note in Revit
        if text_note.Text.startswith(title):
            text_note.Text = updated_text
            break

TransactionManager.Instance.TransactionTaskDone()

# Output updated data structure
OUT = updated_legend
