#!/usr/bin/env python3

import argparse
import re
import requests
import json
import config
import csv
import sys

# Replace with your Home Assistant base URL and access token
BASE_URL = 'https://homeassistant.web.lion.dedyn.io'

# API endpoint for retrieving all entities
API_ENDPOINT = f'{BASE_URL}/api/states'

# Header containing the access token
headers = {
    'Authorization': f'Bearer {config.ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Create the argument parser
parser = argparse.ArgumentParser(description='Home Assistant Entity Filter')
parser.add_argument('--csv', action='store_true', help='Output the data in CSV format')
parser.add_argument('regex', nargs='?', help='Filter the output using a regular expression')

# Parse the command-line arguments
args = parser.parse_args()

# Send GET request to the API endpoint
response = requests.get(API_ENDPOINT, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = json.loads(response.text)

    # Extract entity IDs and friendly names
    entity_data = [(entity['entity_id'], entity['attributes'].get('friendly_name', '')) for entity in data]

    # Filter the entity data if regex argument is provided
    if args.regex:
        filtered_entity_data = [(entity_id, friendly_name) for entity_id, friendly_name in entity_data if
                                re.search(args.regex, entity_id)]
        entity_data = filtered_entity_data

    # Output the entity IDs as a list if --csv option is not provided
    if not args.csv:
        for entity_id, _ in entity_data:
            print(entity_id)
    else:
        # Output the entity data in CSV format to stdout with swapped columns
        writer = csv.writer(sys.stdout)
        writer.writerow(['Entity ID', 'Friendly Name'])
        writer.writerows(entity_data)

else:
    print(f'Error: {response.status_code} - {response.text}')
