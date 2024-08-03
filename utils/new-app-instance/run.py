"""
Script to generate a new app instance
It takes all files from the templates folder and replaces the placeholders
with the provided values using the jinja2 template engine
The output folder is ../../tenants/apps/components/{{ instance_name }}
"""

import os
import sys
import re
from jinja2 import Environment, FileSystemLoader

# Set to True to overwrite the instance if it already exists, False otherwise
OVERWRITE = True
PREPEND_NS_NAME = "apps-"


def is_valid_k8s_namespace_name(name: str) -> bool:
    """
    Check if the provided name is a valid kubernetes namespace name
    """
    namespace_regex = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")

    if len(name) < 1 or len(name) > 63:
        return False

    return bool(namespace_regex.match(name))


# Get the instance name from the command line arguments; handle arguments errors
if len(sys.argv) < 2:
    print("Instance name is required")
    sys.exit(1)

instance_name = sys.argv[1]

# Prepend the instance name if it doesn't start with it to generate the namespace name
if not instance_name.startswith(PREPEND_NS_NAME):
    instance_namespace_name = PREPEND_NS_NAME + instance_name
else:
    # Save the instance name as the namespace name
    instance_namespace_name = instance_name

    # Remove the prefix for the instance name
    instance_name = instance_name[len(PREPEND_NS_NAME) :]


# Check the format of the namespace name
if not is_valid_k8s_namespace_name(instance_namespace_name):
    print(f"Invalid namespace name: {instance_namespace_name}")
    sys.exit(1)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the templates directory
templates_dir = os.path.join(current_dir, "templates")

# Check if the templates directory exists
if not os.path.exists(templates_dir):
    print(f"Templates directory not found: {templates_dir}")
    sys.exit(1)

# Get the output directory
output_dir = os.path.join(
    current_dir, "..", "..", "tenants", "apps", "instances", instance_name
)

# Check if the output directory already exists
if os.path.exists(output_dir) and not OVERWRITE:
    print(f"Instance {instance_name} already exists in {output_dir}")
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
    content = template.render(
        instance_name=instance_name,
        namespace_name=instance_namespace_name,
    )
    # Remove the .j2 extension from the file name
    file_name = file.replace(".j2", "")
    target_file = os.path.join(output_dir, file_name)

    # Check if the target file already exists
    if os.path.exists(target_file) and OVERWRITE:
        os.remove(target_file)

    # Write the content to the output file
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)

print(f"App instance {instance_name} created successfully")
