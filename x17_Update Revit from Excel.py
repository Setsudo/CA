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

try:
    # Build a lookup dictionary for Revit data based on category names
    revit_lookup = {}
    for revit_category in revit_data:
        revit_category_name = revit_category[0][1]
        revit_lookup[revit_category_name] = revit_category

    # Iterate through each category in the Excel data
    for excel_category in excel_data:
        # Get the category name from Excel
        category_name = excel_category[1]
        
        # Attempt to find the matching category in Revit
        if category_name in revit_lookup:
            revit_category = revit_lookup[category_name]

            # Iterate through each sub-header in Excel and match with Revit
            for excel_sub_header in excel_category[2:]:
                if isinstance(excel_sub_header, list) and len(excel_sub_header) > 0:
                    excel_label = excel_sub_header[0]

                    # Iterate through Revit sub-headers to find the best match
                    for revit_sub_header in revit_category[1:]:
                        if isinstance(revit_sub_header, list) and len(revit_sub_header) > 0:
                            revit_label = revit_sub_header[0]

                            # Check if the labels match and are part of the specified fields to update
                            if excel_label == revit_label and excel_label in ["Type", "Existing", "Proposed", "Variation"]:
                                # Overwrite the Revit sub-header values with the Excel values
                                revit_sub_header[1] = excel_sub_header[1]

except Exception as e:
    raise e

# Output the updated Revit data
OUT = revit_data
