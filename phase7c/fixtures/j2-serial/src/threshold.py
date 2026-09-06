def parse_threshold(text):
    name, value = text.split('=')
    if not name or not value:
        raise ValueError('invalid threshold')
    return name, int(value)
