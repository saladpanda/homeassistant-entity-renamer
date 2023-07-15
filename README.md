# HomeAssistant Entity Renamer

This project provides a Python script that allows you to list and rename entities in HomeAssistant based on regular expressions. It leverages the HomeAssistant API and WebSocket to interact with the HomeAssistant server.

The `homeassistant-entity-renamer.py` script provides the following functionality:

- List entities: You can retrieve a list of entities in HomeAssistant and display their friendly names and entity IDs. You can optionally filter entities using a regular expression.
- Rename entities: You can rename entities by specifying a search regular expression and a replace regular expression. The script will display a table with the current entity IDs, new entity IDs, and friendly names. It will ask for confirmation before renaming the entities.
- Preserves the history of renamed entities since it uses the same code paths as the HomeAssistant UI (which preserves history since the release 2022.4)

## Requirements

- Python 3.6 or above
- Packages listed in `requirements.txt`

## Usage

1. Install the required packages by running the following command:
   ```
   pip install -r requirements.txt
   ```

2. Rename `config.py.example` to `config.py` and modify the configuration variables according to your HomeAssistant setup.

3. Run the script with the desired options:

   ```
   ./homeassistant-entity-renamer.py --search <search_regex> --replace <replace_regex>
   ```

   Replace `<search_regex>` with the regular expression that matches the entities you want to rename. Replace `<replace_regex>` with the regular expression used to rename the entities. Note that you can use all the regex magic that Python's `re.sub()` function allows.

   **Example:**

   ```
   ./homeassistant-entity-renamer.py --search "light.*" --replace "new_light_\\1"
   ```

   This example will search for entities starting with "light" and rename them by appending "new_light_" to their current entity IDs.

4. Follow the instructions and confirm the renaming process when prompted.

## Acknowledgements

This project was developed in cooperation with ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture.

Feel free to explore and modify the script to suit your specific needs. If you encounter any issues or have suggestions for improvements, please submit them to the project's issue tracker.

**Note:** Make sure to review the code and test it in your environment before running it in a production setup.

