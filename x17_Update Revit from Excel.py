excel_data = IN[0]
revit_data = IN[1]

def normalize_name(name):
    # Normalize names by removing extra spaces and newlines
    return " ".join(str(name).replace("\n", " ").replace("\r", " ").split()).strip()

def extract_subheaders(data):
    subheader_names = []
    if isinstance(data, list):
        # Iterate through blocks directly
        for block in data:
            # Each block should have something like ["Sub-Header", "<Name>", ...]
            if isinstance(block, list) and len(block) > 1 and "Sub-Header" in str(block[0]):
                raw_name = str(block[1])
                subheader_name = normalize_name(raw_name)
                subheader_names.append(subheader_name)
    return subheader_names

def extract_values(data):
    # Extract hierarchical values from data
    values = {}
    if isinstance(data, list):
        for block in data:
            if isinstance(block, list) and len(block) > 1:
                subheader = None
                for item in block:
                    if isinstance(item, list) and len(item) > 1:
                        if "Sub-Header" in str(item[0]):
                            subheader = normalize_name(str(item[1]))
                            if subheader not in values:
                                values[subheader] = {"Type": [], "Existing": [], "Proposed": [], "Variation": []}
                        elif subheader and any(label in str(item[0]) for label in ["Type", "Existing", "Proposed", "Variation"]):
                            label = next(label for label in ["Type", "Existing", "Proposed", "Variation"] if label in str(item[0]))
                            normalized_name = normalize_name(str(item[1]))
                            values[subheader][label].append(normalized_name)
    return values

# Extract subheaders and hierarchical data from Excel
excel_subheaders = extract_subheaders(excel_data)
excel_values = extract_values(excel_data)

print("Normalized Excel Sub-Headers:", excel_subheaders)
print("Normalized Excel Values:", excel_values)

def add_debug_notes(block, label, subheader, excel_values):
    # Add debug notes for matching values under each label
    for item in block:
        if isinstance(item, list) and len(item) > 1 and label in str(item[0]):
            raw_name = str(item[1])
            normalized_name = normalize_name(raw_name)
            if subheader in excel_values and normalized_name in excel_values[subheader][label]:
                item.insert(2, f"{label} Matched in Excel under Sub-Header '{subheader}'")
            else:
                item.insert(2, f"{label} Not Matched in Excel under Sub-Header '{subheader}'")

# Iterate through Revit data and add debug notes
for block in revit_data:
    if isinstance(block, list):
        subheader_name = None
        # Match sub-header at the top level
        if len(block) > 1 and "Sub-Header" in str(block[0]):
            raw_subheader = str(block[1])
            subheader_name = normalize_name(raw_subheader)
            if subheader_name in excel_subheaders:
                block.insert(2, "Subheader Matched in Excel")
            else:
                block.insert(2, "Subheader Not Matched in Excel")
        
        # Add debug notes for each label if sub-header is determined
        if subheader_name:
            for label in ["Type", "Existing", "Proposed", "Variation"]:
                add_debug_notes(block, label, subheader_name, excel_values)

# Debugging output for review
print("Processed Revit Data:", revit_data)

OUT = revit_data
