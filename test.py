#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests"
# ]
# ///

import requests
import json

# PROMPT USED: get a list of sites and output their IDs
def get_sites():
    # Note: In a real implementation, these would come from configuration
    base_url = "https://abcd-001.dx.commercecloud.salesforce.com/s/-/dw/data/v24.1"
    
    # This would normally use proper auth, but for demo we'll just show the structure
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{base_url}/sites", headers=headers)
    if response.status_code == 200:
        sites = response.json()
        print("Site IDs:")
        for site in sites.get('data', []):
            print(f"- {site['id']}")
    else:
        print(f"Error getting sites: {response.status_code}")

if __name__ == "__main__":
    get_sites()

