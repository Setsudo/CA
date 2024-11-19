import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager

# Inputs
doc = DocumentManager.Instance.CurrentDBDocument

# Debugging step: check if input exists and its type
if len(IN) < 1:
    OUT = "Error: Input list is empty. Please provide an input string for the legend name."
    raise SystemExit

# Attempt to retrieve the legend name, and handle if it fails
try:
    legend_name = IN[0]
    # Debugging: print input type and content to see what is being received
    OUT = f"Input received: Type = {type(legend_name)}, Content = {legend_name}"
except IndexError:
    OUT = "Error: Unable to read input from IN[0]. Please verify the input connection."
    raise SystemExit

# Ensure the input is of the correct type (str)
if not isinstance(legend_name, str):
    OUT = f"Error: Input must be a string, received type {type(legend_name)}. Please use a string node."
    raise SystemExit

# Get all views in the document
collector = FilteredElementCollector(doc).OfClass(View)

# Filter only Legend Views with the specified name
specific_legend = None
for view in collector:
    if view.ViewType == ViewType.Legend and view.Name.strip() == legend_name.strip():
        specific_legend = view
        break

# Check if the legend was found and output the result
if specific_legend is None:
    OUT = f"Legend with name '{legend_name}' not found."
else:
    OUT = specific_legend
