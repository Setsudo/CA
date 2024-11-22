import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager

# Inputs
doc = DocumentManager.Instance.CurrentDBDocument

# Check if input is received
if len(IN) < 1 or not IN[0]:
    OUT = "Error: Please provide a list of legend names."
    raise SystemExit

# List of legend names to find
legend_names = IN[0]

# Ensure the input is a list of strings
if not isinstance(legend_names, list) or not all(isinstance(name, str) for name in legend_names):
    OUT = "Error: Input must be a list of strings representing legend names."
    raise SystemExit

# Get all views in the document
collector = FilteredElementCollector(doc).OfClass(View)

# Filter only Legend Views with names that match the list provided
matching_legends = []
for view in collector:
    if view.ViewType == ViewType.Legend and view.Name.strip() in [name.strip() for name in legend_names]:
        # Append name and Element ID as a list
        matching_legends.append([view.Name, view.Id.IntegerValue])

# Check if the legend was found and output the result
if not matching_legends:
    OUT = f"No legends found matching the provided names: {legend_names}"
else:
    OUT = matching_legends
