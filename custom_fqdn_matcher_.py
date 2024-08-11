import re


def compare_strings(str1, str2):
    # Create a regex pattern that allows either a hyphen or a dot in corresponding positions
    pattern = re.escape(str1).replace(r'\-', '[-.]').replace(r'\.', '[-.]')

    # Compile the regex
    regex = re.compile(f"^{pattern}$")

    # Check if the second string matches the regex pattern generated from the first string
    return bool(regex.match(str2))


# Test strings
string1 = "my-fqdn.domain.com"
string2 = "my.fqdn.domain.com"
string3 = "example.sub-domain.com"
string4 = "example.sub.domain.com"
string5 = "not.matching-string.com"

# Compare the strings
print(compare_strings(string2, string1))  # Expected: True
print(compare_strings(string3, string4))  # Expected: True
print(compare_strings(string1, string3))  # Expected: False
print(compare_strings(string1, string5))  # Expected: False
