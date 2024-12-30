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

def create_textnotes_at_positions(revit_data_list, target_legend_id):
    # Find the first TextNoteType in the document
    text_note_type = FilteredElementCollector(doc)\
        .OfClass(TextNoteType)\
        .FirstElement()
    if not text_note_type:
        OUT.append("Error: No TextNoteType found in the document.")
        return

    OUT.append("Combined Revit and Excel Data Received.")

    # Check if the target LegendID exists in the document
    target_legend_element = doc.GetElement(target_legend_id)
    if not target_legend_element:
        OUT.append(f"Error: Target LegendID {target_legend_id.IntegerValue} not found in the document.")
        return
    else:
        OUT.append(f"Target LegendID {target_legend_id.IntegerValue} successfully located in the document.")

    # Start a transaction to create TextNotes
    TransactionManager.Instance.EnsureInTransaction(doc)
    try:
        for sublist in revit_data_list:
            if isinstance(sublist, list) and len(sublist) > 0:
                legend_id_entry = next((entry for entry in sublist if isinstance(entry, list) and entry[0] == "LegendID"), None)
                if legend_id_entry and len(legend_id_entry) > 1:
                    legend_id_value = legend_id_entry[1]
                    if isinstance(legend_id_value, list) and len(legend_id_value) == 1 and isinstance(legend_id_value[0], int):
                        legend_id = ElementId(legend_id_value[0])

                        # Only process notes for the targeted legend
                        if legend_id == target_legend_id:
                            OUT.append("LegendID Successfully Located.")
                            for item in sublist:
                                if isinstance(item, list) and item != legend_id_entry:
                                    position_data = None
                                    note_value = None

                                    # Extract position and note value
                                    for sub_item in item:
                                        if isinstance(sub_item, list) and sub_item[0] == "Position":
                                            try:
                                                position_data = XYZ(
                                                    float(sub_item[1]),
                                                    float(sub_item[2]),
                                                    float(sub_item[3])
                                                )
                                            except ValueError:
                                                OUT.append(f"Invalid position data: {sub_item[1:]}")
                                        elif isinstance(sub_item, list) and sub_item[0] != "Position":
                                            note_value = str(sub_item[1])

                                    # Create TextNote if position and value are valid
                                    if position_data and note_value:
                                        new_note = TextNote.Create(
                                            doc,
                                            legend_id,
                                            position_data,
                                            note_value,
                                            text_note_type.Id
                                        )
                                        OUT.append(
                                            f"Created TextNote '{note_value}' at {position_data} in Legend {legend_id}"
                                        )
    except Exception as ex:
        OUT.append(f"Error creating text notes: {str(ex)}")
    finally:
        TransactionManager.Instance.TransactionTaskDone()

# Example input structure from Dynamo
# IN[0] = Nested list with data for TextNotes, including LegendID
# IN[1] = Target LegendID
try:
    input_revit_data = IN[0]
    if isinstance(IN[1], list) and len(IN[1]) == 1 and isinstance(IN[1][0], int):
        target_legend_id = ElementId(IN[1][0])
        create_textnotes_at_positions(input_revit_data, target_legend_id)
    else:
        OUT.append("Error: Target LegendID input format is invalid.")
except Exception as e:
    OUT.append(f"Error initializing script: {str(e)}")
