import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager

# Get the active document
doc = DocumentManager.Instance.CurrentDBDocument

# Get all views
collector = FilteredElementCollector(doc).OfClass(View)

# Filter only Legend Views
legend_views = [view for view in collector if view.ViewType == ViewType.Legend]

# Output the list of legend views
OUT = legend_views
