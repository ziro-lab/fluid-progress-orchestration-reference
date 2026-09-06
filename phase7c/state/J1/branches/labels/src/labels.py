import re

def normalize_label(value):
    words = re.findall(r'[a-z0-9]+', value.lower())
    return '-'.join(words)
