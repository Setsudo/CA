import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager

# Inputs
doc = DocumentManager.Instance.CurrentDBDocument

# Debugging step: check if input exists and its type
if len(IN) < 1:
    OUT = "Error: Input list is empty. Please provide an input list of legend names."
    raise SystemExit

# Attempt to retrieve the list of legend names, and handle if it fails
try:
    legend_names = IN[0]
    # Debugging: print input type and content to see what is being received
    OUT = f"Input received: Type = {type(legend_names)}, Content = {legend_names}"
except IndexError:
    OUT = "Error: Unable to read input from IN[0]. Please verify the input connection."
    raise SystemExit

# Ensure the input is of the correct type (list of strings)
if not isinstance(legend_names, list):
    OUT = f"Error: Input must be a list of strings, received type {type(legend_names)}. Please use a list node."
    raise SystemExit

# Ensure every element in the list is a string
if not all(isinstance(name, str) for name in legend_names):
    OUT = f"Error: All elements in the input list must be strings. Please verify that the input list only contains strings."
    raise SystemExit

# Get all views in the document
collector = FilteredElementCollector(doc).OfClass(View)

# Filter Legend Views based on the list of specified names
matching_legends = []
legend_names = [name.strip() for name in legend_names]  # Clean up whitespace in legend names

for view in collector:
    if view.ViewType == ViewType.Legend and view.Name.strip() in legend_names:
        matching_legends.append(view)

# Check if any legends were found and output the result
if len(matching_legends) == 0:
    OUT = f"No legends found matching the provided names: {legend_names}."
else:
    OUT = matching_legends
