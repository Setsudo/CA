import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *

# Input Legend ID
legend_id = IN[0][0]

# Access the current Revit document
doc = DocumentManager.Instance.CurrentDBDocument

# Placeholder for output
text_notes = []

try:
    # Validate that the input is a valid integer before converting to ElementId
    if isinstance(legend_id, int):
        # Try to convert legend_id to an ElementId
        legend_element_id = ElementId(legend_id)
        
        # Get the Legend View from the document
        legend_view = doc.GetElement(legend_element_id)

        # Check if the view is a Legend type
        if isinstance(legend_view, View) and legend_view.ViewType == ViewType.Legend:
            # Collect all text notes within the legend view
            collector = FilteredElementCollector(doc, legend_view.Id)
            text_elements = collector.OfCategory(BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()
            
            # Extract text, Legend Index, position, and index from each TextNote element
            for index, text_element in enumerate(text_elements, start=1):
                if isinstance(text_element, TextNote):
                    text = text_element.Text.strip()
                    location = text_element.Coord  # Get XYZ position
                    text_notes.append([
                        text,
                        [
                            "Legend Index", index,
                            ["Position", location.X, location.Y, location.Z]
                        ]
                    ])
        else:
            text_notes.append(["Error: The provided ID does not correspond to a Legend View."])
    else:
        text_notes.append(["Error: Invalid input type. Please provide a valid integer ID."])
except Exception as e:
    text_notes.append([f"Error: An error occurred: {str(e)}"])

# Output the collected text notes
OUT = text_notes
