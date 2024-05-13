# HomeAssistant Entity Renamer

This project provides a Python script that allows you to list and rename entities in HomeAssistant based on regular expressions. It leverages the HomeAssistant API and WebSockets to interact with the HomeAssistant server.

The `homeassistant-entity-renamer.py` script provides the following functionality:

- List entities: You can retrieve a list of entities in HomeAssistant and display their friendly names and entity IDs. You can optionally filter entities using a regular expression.
- Rename entities: You can rename entities by specifying a search regular expression and a replace regular expression (see pythons [re.sub()](https://docs.python.org/3/library/re.html#re.sub)). The script will display a table with the current entity IDs, new entity IDs, and friendly names. It will ask for confirmation before renaming the entities.
- Preserves the history of renamed entities since it uses the same code path for renaming as the HomeAssistant UI (which preserves history since the release 2022.4). See [this websocket callback](https://github.com/home-assistant/core/blob/2023.7.2/homeassistant/components/config/entity_registry.py#L147).


Tested on HomeAssistant 2023.7.2.

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

4. Check the output and confirm the renaming process if desired.

## Usage (with docker)

1. Rename `config.py.example` to `config.py` and modify the configuration variables according to your HomeAssistant setup.
2. `docker build -t homeassistant-renamer .`
3. `docker run --rm -i homeassistant-renamer --search sensor`

## Examples

```
$ ./homeassistant-entity-renamer.py --search "interesting"
| Friendly Name              | Entity ID                               |
|----------------------------|-----------------------------------------|
| Interesting Testbutton 1   | input_button.interesting_testbutton_1   |
| Interesting Testdropdown 1 | input_select.interesting_testdropdown_1 |
| Interesting Testentity 1   | input_button.interesting_testentity_1   |
| Interesting testnumber 1   | input_number.interesting_testnumber_1   |
| interesting testtext 1     |   input_text.interesting_testtext_1     |
```
```
$ ./homeassistant-entity-renamer.py --search "interesting_test(.*)_1" --replace "just_another_\1"
| Friendly Name              | Current Entity ID                       | New Entity ID                      |
|----------------------------|-----------------------------------------|------------------------------------|
| Interesting Testbutton 1   | input_button.interesting_testbutton_1   | input_button.just_another_button   |
| Interesting Testdropdown 1 | input_select.interesting_testdropdown_1 | input_select.just_another_dropdown |
| Interesting Testentity 1   | input_button.interesting_testentity_1   | input_button.just_another_entity   |
| Interesting testnumber 1   | input_number.interesting_testnumber_1   | input_number.just_another_number   |
| interesting testtext 1     |   input_text.interesting_testtext_1     |   input_text.just_another_text     |

Do you want to proceed with renaming the entities? (y/N): 
Renaming process aborted.
```
```
$ ./homeassistant-entity-renamer.py --search "interesting_test(.*)_1" --replace "just_another_\1"
| Friendly Name              | Current Entity ID                       | New Entity ID                      |
|----------------------------|-----------------------------------------|------------------------------------|
| Interesting Testbutton 1   | input_button.interesting_testbutton_1   | input_button.just_another_button   |
| Interesting Testdropdown 1 | input_select.interesting_testdropdown_1 | input_select.just_another_dropdown |
| Interesting Testentity 1   | input_button.interesting_testentity_1   | input_button.just_another_entity   |
| Interesting testnumber 1   | input_number.interesting_testnumber_1   | input_number.just_another_number   |
| interesting testtext 1     |   input_text.interesting_testtext_1     |   input_text.just_another_text     |

Do you want to proceed with renaming the entities? (y/N): y
Entity 'input_button.interesting_testbutton_1' renamed to 'input_button.just_another_button' successfully!
Entity 'input_select.interesting_testdropdown_1' renamed to 'input_select.just_another_dropdown' successfully!
Entity 'input_button.interesting_testentity_1' renamed to 'input_button.just_another_entity' successfully!
Entity 'input_number.interesting_testnumber_1' renamed to 'input_number.just_another_number' successfully!
Entity 'input_text.interesting_testtext_1' renamed to 'input_text.just_another_text' successfully!

```

## Acknowledgements

This project was developed in cooperation with ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture.

Feel free to explore and modify the script to suit your specific needs. If you encounter any issues or have suggestions for improvements, please submit them to the project's issue tracker.