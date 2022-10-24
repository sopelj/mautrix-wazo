# Test Bridge between Wazo and Matrix using Mautrix.

**Notice**: This plugin was a project for our 2022 Hackathon and requires modifications to the `wazo-chatd` event system to function.
Webhooks in `wazo-webhookd` must also be created to push message notifications to this bridge.
This is not intended to be functional as is, but more a discovery on the subject.

## Installation

1. Install dependencies
    ```bash
    python -m venv env
    . ./env/bin/activate
    pip install -r requirements.txt
   ```
2. Create config file
   ```bash
   cp ./mautrix_wazo/example-config.yaml config.yaml 
   ```
   And make desired changes
3. Generate registration and add registration information to your Synapse Homeserver
   ```bash
   python -m mautrix_wazo -g 
   ```
   This will generate a `registration.yaml` that must be placed on your synapse server and included in your config.
4. Create a webhook for messages and point it to the server running this bridge on the port `5000`
5. Run bridge:
   ```bash
   python -m mautrix_wazo
   ```
