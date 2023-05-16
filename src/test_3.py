import re

sample_string = "Failers(1): This is : a [sample]: string with [multiple] substrings[...] postfixed by [brackets]."

# Define a regular expression pattern to match substrings postfixed by "[...]"
pattern = r"Failers.*\)\:(.*)\[\.\.\.\]"

# Use the re.findall() function to find all substrings postfixed by "[...]" in the sample string
matches = re.findall(pattern, sample_string)

# Print the matches
print(matches[0])