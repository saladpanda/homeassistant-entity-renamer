#!/usr/bin/env python3

import argparse
import re
import requests
import json
import csv
import sys
import websocket
import config

# Determine the protocol based on TLS configuration
protocol = 'https' if config.TLS else 'http'

# API endpoint for retrieving all entities
API_ENDPOINT = f'{protocol}://{config.HOST}/api/states'

# Header containing the access token
headers = {
    'Authorization': f'Bearer {config.ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def list_entities(regex=None, csv_output=False):
    # Send GET request to the API endpoint
    response = requests.get(API_ENDPOINT, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = json.loads(response.text)

        # Extract entity IDs and friendly names
        entity_data = [(entity['entity_id'], entity['attributes'].get('friendly_name', '')) for entity in data]

        # Filter the entity data if regex argument is provided
        if regex:
            filtered_entity_data = [(entity_id, friendly_name) for entity_id, friendly_name in entity_data if
                                    re.search(regex, entity_id)]
            entity_data = filtered_entity_data

        # Output the entity IDs as a list if csv_output is False
        if not csv_output:
            for entity_id, _ in entity_data:
                print(entity_id)
        else:
            # Output the entity data in CSV format to stdout with swapped columns
            writer = csv.writer(sys.stdout)
            writer.writerow(['Entity ID', 'Friendly Name'])
            writer.writerows(entity_data)

    else:
        print(f'Error: {response.status_code} - {response.text}')


def rename_entity(old_entity_id, new_entity_id):
    websocket_protocol = 'wss' if config.TLS else 'ws'
    websocket_url = f'{websocket_protocol}://{config.HOST}/api/websocket'
    ws = websocket.WebSocket()
    ws.connect(websocket_url)

    auth_req = ws.recv()

    # Authenticate with Home Assistant
    auth_msg = json.dumps({"type": "auth", "access_token": config.ACCESS_TOKEN})
    ws.send(auth_msg)
    auth_result = ws.recv()
    auth_result = json.loads(auth_result)
    if auth_result["type"] != "auth_ok":
        print("Authentication failed. Check your access token.")
        return

    # Update the entity registry
    entity_registry_update_msg = json.dumps({
        "id": 1,
        "type": "config/entity_registry/update",
        "entity_id": old_entity_id,
        "new_entity_id": new_entity_id
    })
    ws.send(entity_registry_update_msg)
    update_result = ws.recv()
    update_result = json.loads(update_result)
    if update_result["success"]:
        print("Entity registry updated successfully!")
    else:
        print("Failed to update entity registry:", update_result["error"]["message"])

    ws.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HomeAssistant Entity Renamer")
    parser.add_argument('--csv', action='store_true', help='Output the data in CSV format')
    parser.add_argument('regex', nargs='?', help='Filter the output using a regular expression')
    parser.add_argument('--old', help='Old entity ID')
    parser.add_argument('--new', help='New entity ID')
    args = parser.parse_args()

    if args.old and args.new:
        rename_entity(args.old, args.new)
    else:
        list_entities(args.regex, args.csv)
