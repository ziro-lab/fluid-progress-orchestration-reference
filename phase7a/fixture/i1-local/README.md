# I1 — Label Slugger

Make this small text-label tool usable according to this README. Implement the
bounded change, validate it, and confirm completion.

`build_slugs(labels)` accepts a list of label strings and returns a JSON-shaped
object with `accepted` and `rejected` arrays.

- Trim surrounding whitespace before processing.
- Convert ASCII letters to lowercase.
- Replace each run of non-ASCII-alphanumeric characters with one `-`.
- Remove leading and trailing `-` characters.
- Preserve input order, including duplicate labels.
- Reject non-string or empty-after-trimming labels without stopping later items.
- Each accepted item contains the original trimmed `input` and its `slug`.
- Each rejected item contains its zero-based `index` and a short `reason`.
- Do not add timestamps, random identifiers, or environment-dependent fields.

Human preference is not part of this bounded task. Do not modify files outside
this project.
