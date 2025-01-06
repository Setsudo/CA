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

def update_textnotes_from_data(revit_data_list, target_legend_id):
    # Find the first TextNoteType in the document
    text_note_type = FilteredElementCollector(doc)\
        .OfClass(TextNoteType)\
        .FirstElement()
    if not text_note_type:
        OUT.append("Error: No TextNoteType found in the document.")
        return

    OUT.append("Combined Revit and Excel Data Received.")

    # Verify the target LegendID exists in the document
    target_legend_element = doc.GetElement(target_legend_id)
    if not target_legend_element:
        OUT.append(f"Error: Target LegendID {target_legend_id.IntegerValue} not found in the document.")
        return
    else:
        OUT.append(f"Target LegendID {target_legend_id.IntegerValue} successfully located in the document.")

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

                    # Track if any fields were processed for the Sub-Header
                    fields_processed = []

                    # Iterate through all sub-items under the current Sub-Header
                    for item in sublist:
                        if isinstance(item, list) and len(item) > 0 and item[0] in ["Existing", "Proposed", "Variation"]:
                            field_name = item[0]
                            field_value = item[1]

                            # Locate Legend Index and Position
                            legend_index_entry = next((entry for entry in item if isinstance(entry, list) and entry[0] == "Legend Index"), None)
                            if legend_index_entry and len(legend_index_entry) > 1:
                                legend_index_value = legend_index_entry[1]
                                position_entry = next((entry for entry in legend_index_entry if isinstance(entry, list) and entry[0] == "Position"), None)

                                # Attempt to locate the TextNote using Legend Index
                                try:
                                    legend_element = doc.GetElement(ElementId(legend_index_value))
                                    if legend_element and isinstance(legend_element, TextNote):
                                        legend_element.Text = str(field_value)
                                        OUT.append(f"Updated TextNote for {field_name} (Legend Index: {legend_index_value}) with value: {field_value}")
                                        fields_processed.append(field_name)
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
                                            target_legend_id,
                                            position_data,
                                            str(field_value),
                                            text_note_type.Id
                                        )
                                        OUT.append(f"Created TextNote at {position_data} for {field_name} with value: {field_value}")
                                        fields_processed.append(field_name)
                                    except Exception as e:
                                        OUT.append(f"Error creating TextNote at Position {position_entry}: {str(e)}")
                            else:
                                OUT.append(f"No Legend Index found for {field_name} under Sub-Header {sub_header_name}.")

                    # Debug the processed fields for the Sub-Header
                    if fields_processed:
                        OUT.append(f"Processed fields for Sub-Header {sub_header_name}: {', '.join(fields_processed)}")
                    else:
                        OUT.append(f"No fields were processed for Sub-Header {sub_header_name}.")
    except Exception as ex:
        OUT.append(f"Error updating text notes: {str(ex)}")
    finally:
        TransactionManager.Instance.TransactionTaskDone()

# Example input structure from Dynamo
# IN[0] = Nested list with data for TextNotes
# IN[1] = Target LegendID
try:
    input_revit_data = IN[0]
    target_legend_id = ElementId(int(IN[1][0]))  # Correctly extract LegendID from list
    update_textnotes_from_data(input_revit_data, target_legend_id)
except Exception as e:
    OUT.append(f"Error initializing script: {str(e)}")
