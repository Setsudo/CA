excel_data = IN[0]
revit_data = IN[1]

def normalize_name(name):
    # Normalize names by removing extra spaces and newlines
    return " ".join(str(name).replace("\n", " ").replace("\r", " ").split()).strip()

def extract_subheaders(data):
    subheader_names = []
    if isinstance(data, list):
        for block in data:
            if isinstance(block, list) and len(block) > 1 and "Sub-Header" in str(block[0]):
                raw_name = str(block[1])
                subheader_name = normalize_name(raw_name)
                subheader_names.append(subheader_name)
    return subheader_names

def extract_values(data):
    values = {}
    if isinstance(data, list):
        for block in data:
            subheader = None
            if isinstance(block, list):
                for item in block:
                    if isinstance(item, list) and len(item) > 1:
                        if "Sub-Header" in str(item[0]):
                            subheader = normalize_name(str(item[1]))
                            if subheader not in values:
                                values[subheader] = {"Type": [], "Existing": [], "Proposed": [], "Variation": []}
                        elif subheader:
                            normalized_item = normalize_name(str(item[0])).lower()
                            for label in ["Type", "Existing", "Proposed", "Variation"]:
                                if label.lower() in normalized_item:
                                    normalized_name = normalize_name(str(item[1])) if item[1] else "EMPTY"
                                    values[subheader][label].append(normalized_name)
    return values

# Debugging logs
print("Starting Debugging Logs")

def log_structure(name, data, limit=5):
    print(f"{name} Sample (First {limit} entries):", data[:limit])

# Extract and debug Excel data
excel_subheaders = extract_subheaders(excel_data)
excel_values = extract_values(excel_data)
log_structure("Excel Data Structure", excel_data)
print("Excel Sub-Headers:", excel_subheaders)
print("Extracted Values from Excel:", excel_values)

# Enhanced Logging for Extract Values
if not excel_values:
    print("Extract Values Debug: No data extracted from Excel. Possible issues:")
    for block in excel_data:
        print("Inspecting block:", block)
        if isinstance(block, list):
            for item in block:
                if isinstance(item, list):
                    print("Item:", item)
                    if "Sub-Header" in str(item[0]):
                        print("Potential Sub-Header Detected:", item[1])

# Extract and debug Revit data
revit_subheaders = [normalize_name(block[1]) for block in revit_data if "Sub-Header" in block[0]]
log_structure("Revit Data Structure", revit_data)
print("Revit Sub-Headers:", revit_subheaders)

# Log Excel and Revit sub-header comparison
print("Comparing Sub-Headers:")
unmatched_headers = [header for header in revit_subheaders if header not in excel_subheaders]
print(f"Unmatched Revit Sub-Headers ({len(unmatched_headers)}):", unmatched_headers)

if not excel_values:
    print("No values were extracted from Excel. Verify data format.")

# Add debug notes to Revit data
def add_debug_notes(block, label, subheader, excel_values):
    for item in block:
        if isinstance(item, list) and len(item) > 1 and label in str(item[0]):
            raw_name = str(item[1])
            normalized_name = normalize_name(raw_name)
            if subheader in excel_values and excel_values[subheader][label]:
                excel_value = excel_values[subheader][label][0]
                original_value = item[1]
                item[1] = excel_value
                item.insert(2, f"{label} Matched. Excel Value: '{excel_value}' replaced '{original_value}'.")
            else:
                item.insert(2, f"{label} Not Found for Sub-Header '{subheader}'.")

# Process Revit data
for block in revit_data:
    if isinstance(block, list):
        subheader_name = None
        if len(block) > 1 and "Sub-Header" in str(block[0]):
            raw_subheader = str(block[1])
            subheader_name = normalize_name(raw_subheader)
            if subheader_name in excel_subheaders:
                block.insert(2, "Subheader Matched in Excel")
            else:
                block.insert(2, "Subheader Not Matched in Excel")
        
        if subheader_name:
            for label in ["Type", "Existing", "Proposed", "Variation"]:
                add_debug_notes(block, label, subheader_name, excel_values)

# Log final processed Revit data
log_structure("Final Processed Revit Data", revit_data, limit=10)

OUT = revit_data
