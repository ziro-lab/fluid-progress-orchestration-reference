def parse_threshold(text):
    if text.count('=') != 1:
        raise ValueError('invalid threshold')
    name, value = (part.strip() for part in text.split('='))
    if not name or not value:
        raise ValueError('invalid threshold')
    return name, int(value)
