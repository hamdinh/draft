def dict_to_hcl(data):
    def format_value(value):
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, list):
            return f"[{', '.join(format_value(v) for v in value)}]"
        elif isinstance(value, dict):
            return f"{{\n{dict_to_hcl(value)}\n}}"
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")

    hcl_lines = []
    for key, value in data.items():
        hcl_lines.append(f'{key} = {format_value(value)}')

    return "\n".join(hcl_lines)

# Example usage
my_dict = {
    "variable1": "value1",
    "variable2": 123,
    "variable3": True,
    "nested_variable": {
        "sub_variable1": "sub_value1",
        "sub_variable2": False
    },
    "list_variable": [1, 2, 3]
}

hcl_output = dict_to_hcl(my_dict)
print(hcl_output)