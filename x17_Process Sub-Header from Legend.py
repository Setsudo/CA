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

def normalize_text(text):
    """
    Normalize text for consistent comparison:
    1. Convert to uppercase
    2. Replace special characters and multiple spaces
    3. Standardize common separators
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to uppercase
    text = text.upper()
    
    # Standardize separators
    text = text.replace('&', 'AND')
    text = text.replace('/', 'AND')
    text = text.replace('  ', ' ')  # Double spaces to single
    text = text.replace('-', '')    # Remove hyphens
    
    # Remove parentheses and their contents if they exist
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove special characters and extra spaces
    text = re.sub(r'[^A-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def are_strings_similar(str1, str2, threshold=0.9):
    """
    Compare two strings after normalization
    """
    norm1 = normalize_text(str1)
    norm2 = normalize_text(str2)
    return norm1 == norm2

# Handle view_id input
view_id_input = IN[0]
if isinstance(view_id_input, list) and len(view_id_input) > 0:
    view_id_input = view_id_input[0]

if isinstance(view_id_input, ElementId):
    view_id = view_id_input
elif isinstance(view_id_input, int):
    view_id = ElementId(view_id_input)
elif isinstance(view_id_input, str) and view_id_input.isdigit():
    view_id = ElementId(int(view_id_input))
else:
    raise TypeError("view_id_input must be an ElementId, an integer, or a string representing a valid ID.")

# Get and normalize sub-headers
sub_headers = [normalize_text(IN[i]) for i in range(1, len(IN))]

# Get legend view
legend_view = doc.GetElement(view_id)
if legend_view is None or legend_view.ViewType != ViewType.Legend:
    raise ValueError(f"Legend view with ID '{view_id_input}' was not found or is not a legend view.")

# Collect text notes
text_notes = FilteredElementCollector(doc, legend_view.Id).OfClass(TextNote).ToElements()

def organize_text_notes(text_notes, tolerance=0.1):
    """
    Organize text notes into rows based on Y-coordinate
    """
    rows = []
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
    
    # Sort rows top to bottom
    rows.sort(key=lambda r: -r[0].Coord.Y)
    
    # Sort within rows left to right
    for row in rows:
        row.sort(key=lambda tn: tn.Coord.X)
    
    return rows

def find_matching_row(sub_header, rows):
    """
    Find exact matching row for a sub-header
    """
    normalized_sub_header = normalize_text(sub_header)
    matched_rows = []
    
    for row in rows:
        for text_note in row:
            if are_strings_similar(text_note.Text, normalized_sub_header):
                # Verify this is a true match by checking context
                if verify_row_context(row):
                    matched_rows.append(row)
                break
    
    return matched_rows

def verify_row_context(row):
    """
    Verify the row contains expected context (type indicators, measurements)
    """
    row_text = ' '.join(note.Text.upper() for note in row)
    # Check for common type indicators
    has_type = bool(re.search(r'\b(LF|SLF|DR)\b', row_text))
    # Check for measurement patterns
    has_measurements = bool(re.search(r'\d+(\.\d+)?', row_text))
    
    return has_type or has_measurements

def extract_row_data(row):
    """
    Extract data from a matched row
    """
    data = {
        "type": "Type Not Found",
        "existing": {"value": "Not Found", "index": "Not Found"},
        "proposed": {"value": "Not Found", "index": "Not Found"},
        "variation": {"value": "Not Found", "index": "Not Found"}
    }
    
    for text_note in row:
        note_text = text_note.Text.upper().strip()
        
        # Extract type (LF, SLF, DR)
        type_match = re.search(r'\b(LF|SLF|DR)\b', note_text)
        if type_match:
            data["type"] = type_match.group(1)
        
        # Extract values and indices
        if "EXISTING" in note_text:
            data["existing"]["value"] = text_note.Text.strip()
            data["existing"]["index"] = text_note.Id.IntegerValue
        elif "PROPOSED" in note_text:
            data["proposed"]["value"] = text_note.Text.strip()
            data["proposed"]["index"] = text_note.Id.IntegerValue
        elif "VARIATION" in note_text:
            data["variation"]["value"] = text_note.Text.strip()
            data["variation"]["index"] = text_note.Id.IntegerValue
    
    return data

# Process data
rows = organize_text_notes(text_notes)
final_data = []

for sub_header in sub_headers:
    matched_rows = find_matching_row(sub_header, rows)
    
    if matched_rows:
        # Use only the first match if multiple matches found
        row_data = extract_row_data(matched_rows[0])
        final_data.append([
            sub_header,
            [
                matched_rows[0][0].Text.strip(),
                row_data["type"],
                row_data["existing"]["value"],
                row_data["existing"]["index"],
                row_data["proposed"]["value"],
                row_data["proposed"]["index"],
                row_data["variation"]["value"],
                row_data["variation"]["index"]
            ]
        ])
    else:
        final_data.append([
            sub_header,
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

OUT = final_data