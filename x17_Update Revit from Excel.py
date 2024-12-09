excel_data = IN[0]
revit_data = IN[1]

def normalize_subheader_name(name):
    # Convert name to string, replace newlines with a space, and normalize spaces
    return " ".join(str(name).replace("\n", " ").replace("\r", " ").split())

def extract_subheaders(data):
    subheader_names = []
    if isinstance(data, list):
        # Iterate through the blocks directly
        for block in data:
            # Each block should have something like ["Sub-Header", "<Name>", ...]
            if isinstance(block, list) and len(block) > 1:
                # Check if block[0] indicates a sub-header
                if "Sub-Header" in str(block[0]):
                    raw_name = str(block[1])
                    subheader_name = normalize_subheader_name(raw_name)
                    subheader_names.append(subheader_name)
    return subheader_names

# Extract Excel and Revit Sub-Headers
excel_subheaders = extract_subheaders(excel_data)
revit_subheaders = extract_subheaders(revit_data)

# Add debug notes directly within the Sub-Header block
for block in revit_data:
    if isinstance(block, list) and len(block) > 1 and "Sub-Header" in str(block[0]):
        raw_name = str(block[1])
        subheader_name = normalize_subheader_name(raw_name)
        if subheader_name in excel_subheaders:
            block.insert(2, "Debug Note: Subheader Matched in Excel")

# Return the modified Revit data
OUT = revit_data
