import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

doc = DocumentManager.Instance.CurrentDBDocument
OUT = []

def update_textnotes_from_data(revit_data_list):
    # Find the first TextNoteType in the document
    text_note_type = FilteredElementCollector(doc)\
        .OfClass(TextNoteType)\
        .FirstElement()
    if not text_note_type:
        OUT.append("Error: No TextNoteType found in the document.")
        return

    OUT.append("Combined Revit and Excel Data Received.")

    # Start a transaction to update TextNotes
    TransactionManager.Instance.EnsureInTransaction(doc)
    try:
        for sublist in revit_data_list:
            if isinstance(sublist, list) and len(sublist) > 0:
                # Process each Sub-Header
                sub_header_entries = [entry for entry in sublist if isinstance(entry, list) and entry[0] == "Sub-Header"]
                for sub_header_entry in sub_header_entries:
                    sub_header_name = sub_header_entry[1]
                    OUT.append(f"Processing Sub-Header: {sub_header_name}")

                    # Iterate through data fields like Existing, Proposed, Variation
                    for item in sublist:
                        if isinstance(item, list) and item[0] in ["Existing", "Proposed", "Variation"]:
                            field_name = item[0]
                            field_value = item[1]

                            # Debugging the specific field being processed
                            OUT.append(f"Processing Field: {field_name} with value: {field_value}")

                            # Locate Legend Index and Position
                            legend_index_entry = next((entry for entry in item if isinstance(entry, list) and entry[0] == "Legend Index"), None)
                            if legend_index_entry and len(legend_index_entry) > 2:
                                legend_index_value = legend_index_entry[1]
                                position_entry = next((entry for entry in legend_index_entry if isinstance(entry, list) and entry[0] == "Position"), None)

                                # Attempt to locate the TextNote using Legend Index
                                try:
                                    legend_element = doc.GetElement(ElementId(legend_index_value))
                                    if legend_element and isinstance(legend_element, TextNote):
                                        legend_element.Text = str(field_value)
                                        OUT.append(f"Updated TextNote for {field_name} (Legend Index: {legend_index_value}) with value: {field_value}")
                                    else:
                                        OUT.append(f"Legend Index {legend_index_value} does not correspond to a TextNote.")
                                except Exception as e:
                                    OUT.append(f"Error accessing Legend Index {legend_index_value}: {str(e)}")

                                # Fallback to Position if Legend Index fails
                                if not legend_element and position_entry:
                                    try:
                                        position_data = XYZ(
                                            float(position_entry[1]),
                                            float(position_entry[2]),
                                            float(position_entry[3])
                                        )
                                        new_note = TextNote.Create(
                                            doc,
                                            doc.ActiveView.Id,
                                            position_data,
                                            str(field_value),
                                            text_note_type.Id
                                        )
                                        OUT.append(f"Created TextNote at {position_data} for {field_name} with value: {field_value}")
                                    except Exception as e:
                                        OUT.append(f"Error creating TextNote at Position {position_entry}: {str(e)}")
    except Exception as ex:
        OUT.append(f"Error updating text notes: {str(ex)}")
    finally:
        TransactionManager.Instance.TransactionTaskDone()

# Example input structure from Dynamo
# IN[0] = Nested list with data for TextNotes
try:
    input_revit_data = IN[0]
    update_textnotes_from_data(input_revit_data)
except Exception as e:
    OUT.append(f"Error initializing script: {str(e)}")
