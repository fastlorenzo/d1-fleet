"""
Script to generate a new app component
It takes all files from the templates folder and replaces the placeholders
with the provided values using the jinja2 template engine
The output folder is ../../tenants/apps/components/{{component_name}}
"""

import os
import sys
import re
from jinja2 import Environment, FileSystemLoader

# Set to True to overwrite the component if it already exists, False otherwise
OVERWRITE = True
PREPEND_NAME = "app-"


def is_valid_k8s_namespace_name(name: str) -> bool:
    """
    Check if the provided name is a valid kubernetes namespace name
    """
    namespace_regex = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")

    if len(name) < 1 or len(name) > 63:
        return False

    return bool(namespace_regex.match(name))


# Get the component name from the command line arguments; handle arguments errors
if len(sys.argv) < 2:
    print("Component name is required")
    sys.exit(1)

component_name = sys.argv[1]

# Prepend the component name if it doesn't start with it
if not component_name.startswith(PREPEND_NAME):
    component_name = PREPEND_NAME + component_name


# Check the format of the component name
if not is_valid_k8s_namespace_name(component_name):
    print(f"Invalid component name: {component_name}")
    sys.exit(1)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the templates directory
templates_dir = os.path.join(current_dir, "templates")

# Check if the component directory exists
if not os.path.exists(templates_dir):
    print(f"Templates directory not found: {templates_dir}")
    sys.exit(1)

# Get the output directory
output_dir = os.path.join(
    current_dir, "..", "..", "tenants", "apps", "components", component_name
)

# Check if the output directory already exists
if os.path.exists(output_dir) and not OVERWRITE:
    print(f"Component {component_name} already exists")
    sys.exit(1)

# Create the output directory
os.makedirs(output_dir, exist_ok=OVERWRITE)

# Create the jinja2 environment
env = Environment(loader=FileSystemLoader(templates_dir))

# Get all files from the templates directory
files = os.listdir(templates_dir)

# Process each file
for file in files:
    # Get the template
    template = env.get_template(file)
    # Render the template
    content = template.render(component_name=component_name)
    # Remove the .j2 extension from the file name
    file_name = file.replace(".j2", "")
    target_file = os.path.join(output_dir, file_name)

    # Check if the target file already exists
    if os.path.exists(target_file) and OVERWRITE:
        os.remove(target_file)

    # Write the content to the output file
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Component {component_name} created successfully")
