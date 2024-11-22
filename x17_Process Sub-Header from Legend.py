import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
import re

# Inputs
doc = DocumentManager.Instance.CurrentDBDocument
legend_views_data = IN[0]  # List of lists with "Name" and "ElementId"
target_sub_header_text = IN[1]  # The sub-header text to extract (e.g., "MULTI-DECK FROZEN FOOD")

# Collect all the TextNote elements from the given Legend Views using their IDs
all_text_notes = []

# Iterate through each legend data (each being a list of [name, ElementId])
for legend_data in legend_views_data:
    # Ensure the legend_data contains name and ID
    if isinstance(legend_data, list) and len(legend_data) == 2:
        legend_id_value = legend_data[1]
        
        # Ensure that the ID is an integer before creating an ElementId
        if isinstance(legend_id_value, int):
            legend_id = ElementId(legend_id_value)
            legend_element = doc.GetElement(legend_id)
            
            # Verify the legend_element is not None
            if legend_element is None:
                continue

            # Get all TextNote elements within the legend view
            collector = FilteredElementCollector(doc, legend_element.Id).OfClass(TextNote)
            for text_note in collector:
                location = text_note.Coord  # XYZ location of the Text Note
                element_data = {
                    "ElementId": text_note.Id.IntegerValue,
                    "Text": text_note.Text,
                    "Location": location
                }
                all_text_notes.append(element_data)

# Preprocess the target text to remove extra whitespace and normalize line breaks
target_sub_header_text_clean = re.sub(r'\s+', ' ', target_sub_header_text.strip()).upper()

# Group text notes by rows (based on Y-coordinate)
tolerance = 0.1  # Tolerance for determining whether two text notes are in the same row
rows = []

for text_note in all_text_notes:
    y_coord = text_note["Location"].Y
    found_row = False
    for row in rows:
        if abs(row[0]["Location"].Y - y_coord) < tolerance:
            row.append(text_note)
            found_row = True
            break
    if not found_row:
        rows.append([text_note])

# Sort rows by Y-coordinate (descending order for top to bottom)
sorted_rows = sorted(rows, key=lambda r: -r[0]["Location"].Y)

# Sort elements within each row by X-coordinate (ascending order for left to right)
for row in sorted_rows:
    row.sort(key=lambda e: e["Location"].X)

# Find the row that matches the target sub-header text
target_row_data = None

for row in sorted_rows:
    # Check each element in the row to find the target text
    for element in row:
        element_text_clean = re.sub(r'\s+', ' ', element["Text"].strip()).upper()
        if element_text_clean == target_sub_header_text_clean:
            target_row_data = row
            break
    if target_row_data:
        break

# Output the matched row (sub-header row)
OUT = target_row_data
