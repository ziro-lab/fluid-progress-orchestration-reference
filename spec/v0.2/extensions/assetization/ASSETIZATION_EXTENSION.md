# Assetization Extension
## FPO v0.2 optional extension

### 位置づけ

AssetizationはFPO work closureの必須工程ではない。
closed workから再利用価値が十分にある場合だけ、post-actionまたは別workとして起動する。

### Gate

- original workはclosed
- source/evidence/permissionがassetization範囲を許す
- 再利用価値が維持負担を上回る
- shared asset変更はstaging→validate→publish
- 失敗してもoriginal closedを取り消さない

`M08_資産化・成長.md` はこのextensionでのみ使用する。
