def sort_versions(values):
    def key(value):
        text = value if isinstance(value, str) else value['version']
        return tuple(int(part) for part in text.split('.'))
    return sorted(values, key=key)
