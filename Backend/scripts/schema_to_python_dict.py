import json
import pprint

# 1. Read the JSON file into a Python object
with open("presentation_final.schema.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# 2. Format the dictionary as a clean Python string
# pprint automatically converts true -> True, false -> False, null -> None
py_dict_string = pprint.pformat(data, indent=4, width=120)

# 3. Write it into a new .py file as a variable
with open("JSON_SHEMAS1.py", "w+", encoding="utf-8") as py_file:
    py_file.write(f"JSON_SCHEMA = {py_dict_string}\n")

print("Conversion complete! Saved as schema.py")
