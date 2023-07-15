#!/usr/bin/env python3

import websocket
import json
import config
import argparse

def update_entity_registry(old_entity_id, new_entity_id):
    websocket_url = 'wss://homeassistant.web.lion.dedyn.io/api/websocket'
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
    parser = argparse.ArgumentParser(description="Update entity registry in Home Assistant via WebSocket")
    parser.add_argument("old_entity_id", help="Old entity ID")
    parser.add_argument("new_entity_id", help="New entity ID")
    args = parser.parse_args()

    update_entity_registry(args.old_entity_id, args.new_entity_id)

