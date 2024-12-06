import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.DB import TextNote, ElementId

# Inputs
excel_data = IN[0]  # Correct values from Excel
revit_data = IN[1]  # Revit data containing Legend Index and Position information

# Get current document
doc = DocumentManager.Instance.CurrentDBDocument

def sync_data(excel_data, revit_data):
    # Build lookup dictionary for Excel data based on category name
    excel_lookup = {cat[1]: cat for cat in excel_data}
    
    # Create a copy of revit_data to avoid modifying the input directly
    updated_revit_data = [list(cat) for cat in revit_data]
    
    fields_to_update = ["Type", "Existing", "Proposed", "Variation"]

    for i, revit_category in enumerate(updated_revit_data):
        category_name = revit_category[0][1]
        
        if category_name in excel_lookup:
            excel_category = excel_lookup[category_name]
            
            # Create dictionaries for faster lookup
            excel_values = {item[0]: item[1] for item in excel_category[2:] 
                            if isinstance(item, list) and len(item) > 0 and item[0] in fields_to_update}
            
            # Update matching fields in Revit data
            for j, sub_header in enumerate(revit_category[1:], start=1):
                if isinstance(sub_header, list) and len(sub_header) > 0:
                    field_name = sub_header[0]
                    if field_name in excel_values:
                        updated_revit_data[i][j][1] = excel_values[field_name]
    
    return updated_revit_data

# Main execution
try:
    OUT = sync_data(excel_data, revit_data)
except Exception as e:
    import traceback
    OUT = f"Error: {str(e)}\n{traceback.format_exc()}"
