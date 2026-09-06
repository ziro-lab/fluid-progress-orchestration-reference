# Canonical Probe Acceptance

## A1 Input preservation

`workspace/input.txt` の byte content が Probe 開始時から変化していないこと。

## A2 Output existence

`workspace/output/output.txt` が存在すること。

## A3 Deterministic transformation

Output が Input の Unicode invariant uppercase と一致すること。
Canonical input `hello world` の期待値は `HELLO WORLD`。

## A4 No duplicate Effect

同一 Effect intent に対する final output write が重複成立していないこと。

## A5 Evidence before achievement

`executed` / `accepted` / `closed` を主張する前に、それぞれ必要な immutable Record と Commit が存在すること。

## A6 Unknown is not success

Operation / Effect / Return の状態が不明な場合、成功として採用・close しないこと。

## A7 Authority

Capability Return 単独では `executed` へ進めないこと。Owner stage の adoption が必要。
