from labels import normalize_label
from versions import sort_versions

def build_report(records):
    ordered = sort_versions(records)
    return "\n".join(f"{normalize_label(item['label'])}: {item['version']}" for item in ordered)
