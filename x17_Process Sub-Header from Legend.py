import clr
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')

import Revit
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
import Revit.Elements as RevitElements
from Revit.Elements import TextNote as RevitTextNote
clr.ImportExtensions(Revit.Elements)
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.DB import FilteredElementCollector, Viewport, BuiltInCategory, TextNote, View, ViewType, ElementId
import re

# Dynamo Inputs
doc = DocumentManager.Instance.CurrentDBDocument

# Handle direct input of view_id, ensuring it's treated properly as an integer ElementId
view_id_input = IN[0]

# Ensure the input is a valid single value (e.g., if it is a list, extract the first element)
if isinstance(view_id_input, list) and len(view_id_input) > 0:
    view_id_input = view_id_input[0]

# Check if the input is already an integer or can be converted to an integer
if isinstance(view_id_input, ElementId):
    view_id = view_id_input
elif isinstance(view_id_input, int):
    view_id = ElementId(view_id_input)
elif isinstance(view_id_input, str) and view_id_input.isdigit():
    view_id = ElementId(int(view_id_input))
else:
    raise TypeError("view_id_input must be an ElementId, an integer, or a string representing a valid ID.")

# Gather all sub-header inputs dynamically
sub_headers = [str(IN[i]).strip() for i in range(1, len(IN))]  # Strip any leading/trailing whitespace or line breaks
sub_headers_cleaned = [re.sub(r'\s+', ' ', sh.strip()).upper() for sh in sub_headers]  # Clean sub-header inputs

# Step 1: Find the Legend View in Revit using its ID
legend_view = doc.GetElement(view_id)

if legend_view is None or legend_view.ViewType != ViewType.Legend:
    raise ValueError("Legend view with ID '{}' was not found in the document.".format(view_id_input))

# Step 2: Collect All Text Notes in the Legend View
text_notes = FilteredElementCollector(doc, legend_view.Id).OfClass(TextNote).ToElements()

# Step 3: Group TextNotes by rows and columns
tolerance = 0.1  # Tolerance for grouping elements by rows
rows = []

# Organize text notes into rows based on Y-coordinate
for text_note in text_notes:
    y_coord = text_note.Coord.Y
    found_row = False
    for row in rows:
        if abs(row[0].Coord.Y - y_coord) < tolerance:
            row.append(text_note)
            found_row = True
            break
    if not found_row:
        rows.append([text_note])

# Sort rows by Y-coordinate (descending order for top-to-bottom)
rows = sorted(rows, key=lambda r: -r[0].Coord.Y)

# Sort text notes within each row by X-coordinate (ascending order for left-to-right)
for row in rows:
    row.sort(key=lambda tn: tn.Coord.X)

# Step 4: Extract data for each sub-header
sub_header_data = []

for sub_header in sub_headers_cleaned:
    matched_row = None

    # Find the row that matches the sub-header
    for row in rows:
        for text_note in row:
            note_text_clean = re.sub(r'\s+', ' ', text_note.Text.strip()).upper()
            if sub_header == note_text_clean:
                matched_row = row
                break
        if matched_row:
            break

    # If a matching row is found, extract the type, existing, proposed, and variation values
    if matched_row:
        # Extract Type, Existing, Proposed, and Variation from the matched row
        type_value = "Type Not Found"
        existing_value, proposed_value, variation_value = "Not Found", "Not Found", "Not Found"
        existing_index, proposed_index, variation_index = "Not Found", "Not Found", "Not Found"

        for text_note in matched_row:
            note_text = text_note.Text.strip().upper()

            # Determine Type (e.g., LF, SLF, DR)
            type_match = re.search(r'\b(LF|SLF|DR)\b', note_text)
            if type_match:
                type_value = type_match.group(1)

            # Determine Existing, Proposed, and Variation Values
            if "EXISTING" in note_text:
                existing_value = note_text
                existing_index = text_note.Id.IntegerValue
            elif "PROPOSED" in note_text:
                proposed_value = note_text
                proposed_index = text_note.Id.IntegerValue
            elif "VARIATION" in note_text:
                variation_value = note_text
                variation_index = text_note.Id.IntegerValue

        # Compile the extracted information for the sub-header
        sub_header_entry = [
            sub_header,          # Sub-Header
            [
                matched_row[0].Text if matched_row else "No Matching Sub-Header",  # The matching TextNote or "No Matching Sub-Header"
                type_value,          # Type
                existing_value,      # Existing Value
                existing_index,      # Existing Index
                proposed_value,      # Proposed Value
                proposed_index,      # Proposed Index
                variation_value,     # Variation Value
                variation_index      # Variation Index
            ]
        ]
        sub_header_data.append(sub_header_entry)
    else:
        # If no matching row is found, append a "not found" entry
        sub_header_data.append([
            sub_header,    # Sub-Header
            [
                "No Matching Sub-Header",
                "Type Not Found",
                "Existing Value Not Found",
                "Existing Index Not Found",
                "Proposed Value Not Found",
                "Proposed Index Not Found",
                "Variation Not Found",
                "Variation Index Not Found"
            ]
        ])

# Ensure each sub-header input results in an output in the final list
final_data = []
for i, sub_header in enumerate(sub_headers_cleaned):
    if i < len(sub_header_data):
        final_data.append(sub_header_data[i])
    else:
        final_data.append([
            sub_header,    # Sub-Header
            [
                "No Matching Sub-Header",
                "Type Not Found",
                "Existing Value Not Found",
                "Existing Index Not Found",
                "Proposed Value Not Found",
                "Proposed Index Not Found",
                "Variation Not Found",
                "Variation Index Not Found"
            ]
        ])

# Output the collected sub-header data as a list of lists
OUT = final_data
