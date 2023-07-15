#!/usr/bin/env python3

import argparse
import re
import requests
import json
import websocket
import config
import tabulate
tabulate.PRESERVE_WHITESPACE = True

# Determine the protocol based on TLS configuration
TLS_S = 's' if config.TLS else ''

# Header containing the access token
headers = {
    'Authorization': f'Bearer {config.ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def align_strings_in_column(table, column, c="."):
    # Get the column data from the table
    column_data = [row[column] for row in table]

    # Find the maximum length of the first part of the split strings
    max_length = max(len(s.split(c)[0]) for s in column_data)

    def align_string(s):
        s_split = s.split(c)
        return f"{s_split[0]:>{max_length}}.{s_split[1]}"

    # Create the modified table by replacing the column with aligned strings
    modified_table = [
        tuple(align_string(value) if i == column else value for i, value in enumerate(row))
        for row in table
    ]

    return modified_table

def list_entities(regex=None):
    # API endpoint for retrieving all entities
    api_endpoint = f'http{TLS_S}://{config.HOST}/api/states'

    # Send GET request to the API endpoint
    response = requests.get(api_endpoint, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = json.loads(response.text)

        # Extract entity IDs and friendly names
        entity_data = [(entity['attributes'].get('friendly_name', ''), entity['entity_id']) for entity in data]

        # Filter the entity data if regex argument is provided
        if regex:
            filtered_entity_data = [(friendly_name, entity_id) for friendly_name, entity_id in entity_data if
                                    re.search(regex, entity_id)]
            entity_data = filtered_entity_data

        # Sort the entity data by friendly name
        entity_data = sorted(entity_data, key=lambda x: x[0])

        # Output the entity data
        return entity_data

    else:
        print(f'Error: {response.status_code} - {response.text}')
        return []


def rename_entities(entity_data, search_regex, replace_regex):
    renamed_data = []
    for friendly_name, entity_id in entity_data:
        new_entity_id = re.sub(search_regex, replace_regex, entity_id)
        renamed_data.append((friendly_name, entity_id, new_entity_id))

    # Print the table with friendly name and entity ID
    table = [("Friendly Name", "Current Entity ID", "New Entity ID")] + align_strings_in_column(align_strings_in_column(renamed_data, 1), 2)
    print(tabulate.tabulate(table, headers="firstrow", tablefmt="github"))

    # Ask user for confirmation if replace_regex is provided
    if replace_regex:
        answer = input("\nDo you want to proceed with renaming the entities? (y/N): ")
        if answer.lower() == "y" or answer.lower() == "yes":
            websocket_url = f'ws{TLS_S}://{config.HOST}/api/websocket'
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
            for index, (_, entity_id, new_entity_id) in enumerate(renamed_data, start=1):
                entity_registry_update_msg = json.dumps({
                    "id": index,
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
    parser.add_argument('--search', dest='search_regex', help='Regular expression for search. Note: Only searches entity IDs.')
    parser.add_argument('--replace', dest='replace_regex', help='Regular expression for replace')
    args = parser.parse_args()

    if args.search_regex:
        entity_data = list_entities(args.search_regex)

        if entity_data:
            if args.replace_regex:
                rename_entities(entity_data, args.search_regex, args.replace_regex)
            else:
                # Print the table with friendly name and entity ID
                table = [("Friendly Name", "Entity ID")] + align_strings_in_column(entity_data, 1)
                print(tabulate.tabulate(table, headers="firstrow", tablefmt="github"))
        else:
            print("No entities found matching the search regex.")
    else:
        parser.print_help()
