import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# Inputs from Dynamo
subheader_list = IN[0]  # Expected to be a list of various nested structures

# Output container
OUT = []

# Access the active Revit document
doc = DocumentManager.Instance.CurrentDBDocument

def preprocess_input(data):
    """Recursively process the input to flatten it and convert into dictionaries with type_name."""
    processed = []

    if isinstance(data, list):
        for item in data:
            processed.extend(preprocess_input(item))  # Recursively handle nested lists
    elif isinstance(data, str):
        # Convert string to a dictionary with type_name
        processed.append({
            'view_name': data,
            'type_name': 'SubHeader'
        })
    elif isinstance(data, dict):
        # Ensure required keys are present and set type_name
        processed.append({
            'view_name': data.get('view_name', 'UnnamedView'),
            'type_name': 'SubHeader'
        })
    else:
        # Log unsupported types
        OUT.append(f"Unsupported type encountered: {type(data)} - {data}")

    return processed

# Preprocess the input list
try:
    normalized_list = preprocess_input(subheader_list)
    OUT.append("Preprocessing completed for input: subheader_list")
    OUT.append(normalized_list)
except Exception as e:
    OUT.append(f"Error during preprocessing: {str(e)}")
