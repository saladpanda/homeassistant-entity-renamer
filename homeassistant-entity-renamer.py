#!/usr/bin/env python3

import argparse
import re
import requests
import json
import websocket
import config
from tabulate import tabulate

# Determine the protocol based on TLS configuration
protocol = 'https' if config.TLS else 'http'

# API endpoint for retrieving all entities
API_ENDPOINT = f'{protocol}://{config.HOST}/api/states'

# Header containing the access token
headers = {
    'Authorization': f'Bearer {config.ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def list_entities(regex=None):
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

        # Output the entity IDs
        return entity_data

    else:
        print(f'Error: {response.status_code} - {response.text}')
        return []


def rename_entities(entity_data, search_regex, replace_regex):
    renamed_data = []
    for entity_id, friendly_name in entity_data:
        new_entity_id = re.sub(search_regex, replace_regex, entity_id)
        renamed_data.append((entity_id, new_entity_id, friendly_name))

    # Print the table with original and new entity names
    print("\nOriginal Entity Names vs New Entity Names:")
    table = [("Original Entity Name", "New Entity Name", "Friendly Name")] + renamed_data
    print(tabulate(table, headers="firstrow"))

    # Ask user for confirmation
    answer = input("\nDo you want to proceed with renaming the entities? (y/N): ")
    if answer.lower() == "y" or answer.lower() == "yes":
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

        # Rename the entities
        for index, (entity_id, new_entity_id, _) in enumerate(renamed_data):
            entity_registry_update_msg = json.dumps({
                "id": index+1,
                "type": "config/entity_registry/update",
                "entity_id": entity_id,
                "new_entity_id": new_entity_id
            })
            ws.send(entity_registry_update_msg)
            update_result = ws.recv()
            update_result = json.loads(update_result)
            if update_result["success"]:
                print(f"Entity '{entity_id}' renamed to '{new_entity_id}' successfully!")
            else:
                print(f"Failed to rename entity '{entity_id}': {update_result['error']['message']}")

        ws.close()
    else:
        print("Renaming process aborted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HomeAssistant Entity Renamer")
    parser.add_argument('search_regex', help='Regular expression for search')
    parser.add_argument('replace_regex', help='Regular expression for replace')
    args = parser.parse_args()

    entity_data = list_entities(args.search_regex)

    if entity_data:
        rename_entities(entity_data, args.search_regex, args.replace_regex)
    else:
        print("No entities found matching the search regex.")