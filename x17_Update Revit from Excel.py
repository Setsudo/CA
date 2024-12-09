excel_data = IN[0]
revit_data = IN[1]

def normalize_subheader_name(name):
    # Convert name to string, replace newlines with a space, and normalize spaces
    return " ".join(str(name).replace("\n", " ").split())

def extract_subheaders(data):
    subheader_names = []
    if len(data) > 0 and isinstance(data[0], list):
        # data[0] should be a list of sub-header blocks
        subheader_blocks = data[0]
        for block in subheader_blocks:
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

# Return results for inspection
OUT = (excel_subheaders, revit_subheaders)
