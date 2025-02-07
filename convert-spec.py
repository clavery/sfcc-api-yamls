#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pyyaml"
# ]
# ///
import json
import yaml
import os
import copy
import sys
from pathlib import Path

def find_referenced_definitions(schema, all_definitions, collected_refs=None):
    """Recursively find all referenced definitions in a schema"""
    if collected_refs is None:
        collected_refs = set()
    
    if isinstance(schema, dict):
        # Check for $ref
        if '$ref' in schema:
            ref = schema['$ref']
            if ref.startswith('#/definitions/'):
                def_name = ref.split('/')[-1]
                if def_name not in collected_refs:
                    collected_refs.add(def_name)
                    # Recursively check the definition for more refs
                    if def_name in all_definitions:
                        find_referenced_definitions(all_definitions[def_name], 
                                                 all_definitions, 
                                                 collected_refs)
        
        # Recurse through all dictionary values
        for value in schema.values():
            find_referenced_definitions(value, all_definitions, collected_refs)
            
    elif isinstance(schema, list):
        # Recurse through all list items
        for item in schema:
            find_referenced_definitions(item, all_definitions, collected_refs)
            
    return collected_refs

def create_path_spec(base_spec, path, path_data):
    """Create a new spec file for a single path"""
    new_spec = copy.deepcopy(base_spec)
    
    # Remove all paths and add only the current path
    new_spec['paths'] = {path: path_data}
    
    # Find all referenced definitions
    refs = set()
    find_referenced_definitions(path_data, base_spec.get('definitions', {}), refs)
    
    # Only include referenced definitions
    if 'definitions' in new_spec:
        new_spec['definitions'] = {
            key: base_spec['definitions'][key]
            for key in refs
            if key in base_spec['definitions']
        }
    
    return new_spec

def sanitize_filename(path):
    """Convert path to valid filename"""
    # Remove leading slash and replace remaining slashes with underscore
    return path.lstrip('/').replace('/', '__')

def main(input_file, output_dir):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        spec = json.load(f)
    
    # Create base spec without paths and definitions
    base_spec = copy.deepcopy(spec)
    base_spec.pop('paths', None)
    base_spec.pop('definitions', None)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each path
    for path, path_data in spec['paths'].items():
        # Create new spec for this path
        path_spec = create_path_spec(spec, path, path_data)
        
        # Create filename from path
        filename = sanitize_filename(path) + '.yaml'
        output_path = os.path.join(output_dir, filename)
        
        # Write YAML file
        with open(output_path, 'w') as f:
            yaml.dump(path_spec, f, default_flow_style=False, sort_keys=False)
        
        print(f"Created {output_path}")

if __name__ == "__main__":
    # Example usage
    input_file = sys.argv[1]    # Input file
    output_dir = sys.argv[2]    # Output directory
    main(input_file, output_dir)
