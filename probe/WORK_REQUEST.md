# Canonical Probe Work Request

`workspace/input.txt` の英字を大文字に変換し、元ファイルを変更せず、
`workspace/output/output.txt` として保存する。

## Intent

この作業自体の価値を測るのではなく、FPO Runtime が以下を安全に扱えるかを検証する。

- Definition → Design → Dispatch → Operation → Return → Adoption → Validation → Closure
- crash/restart
- duplicate/stale/unknown
- pause/cancel/amendment
- budget exhaustion
- untrusted Return
- digest mismatch
- projection rebuild
