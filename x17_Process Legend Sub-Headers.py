import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from collections import defaultdict
import re

# Inputs
doc = DocumentManager.Instance.CurrentDBDocument
legend_view = UnwrapElement(IN[0])  # Legend View input
target_row_text = IN[1]  # The text of the sub-header to extract (e.g., "MULTI-DECK FROZEN FOOD")

# Collect all TextNote elements in the Legend View
collector = FilteredElementCollector(doc, legend_view.Id).OfClass(TextNote)
text_notes = []

for text_note in collector:
    location = text_note.Coord  # XYZ location of the Text Note
    element_data = {
        "ElementId": text_note.Id.IntegerValue,
        "Text": text_note.Text,
        "Location": location
    }
    text_notes.append(element_data)

# Preprocess the target text to remove extra whitespace and normalize line breaks
target_row_text_clean = re.sub(r'\s+', ' ', target_row_text.strip()).upper()

# Group text notes by rows (based on Y-coordinate)
tolerance = 0.1  # Tolerance for determining whether two text notes are in the same row
rows = defaultdict(list)

for text_note in text_notes:
    y_coord = text_note["Location"].Y
    found_row = False
    for key in rows.keys():
        if abs(y_coord - key) < tolerance:
            rows[key].append(text_note)
            found_row = True
            break
    if not found_row:
        rows[y_coord].append(text_note)

# Sort rows by Y-coordinate (descending order for top to bottom)
sorted_rows = sorted(rows.items(), key=lambda x: -x[0])

# Sort elements within each row by X-coordinate (ascending order for left to right)
sorted_rows_data = []
for y_value, elements in sorted_rows:
    sorted_elements = sorted(elements, key=lambda e: e["Location"].X)
    sorted_rows_data.append(sorted_elements)

# Find the row that matches the target sub-header text
target_row_data = None

for row in sorted_rows_data:
    # Check each element in the row to find the target text
    for element in row:
        element_text_clean = re.sub(r'\s+', ' ', element["Text"].strip()).upper()
        if element_text_clean == target_row_text_clean:
            target_row_data = row
            break
    if target_row_data:
        break

# Output the matched row (sub-header row)
OUT = target_row_data
