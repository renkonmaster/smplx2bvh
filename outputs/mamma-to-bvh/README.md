# MAMMA SMPL-X → BVH

MAMMA `ma_3d` の `smplx_params_body_id-XX.npz` をSMPL-X Blender Add-on経由でBVHへ変換します。

## 手動読込エラーの原因

MAMMAのキーは `smplx_pose`、`smplx_betas`、`smplx_translation` です。Add Animationが要求するAMASSキーは `poses`、`betas`、`trans`、`gender`、`mocap_framerate` です。キーが一致しないため `Invalid AMASS animation data file` になりました。

この問題を直すのは `01_convert_mamma_to_amass.py` です。

```text
smplx_pose        → poses
smplx_betas       → betas
smplx_translation → trans
追加              → gender="neutral"
追加              → mocap_framerate=<指定FPS>
```

## ファイル

```text
01_convert_mamma_to_amass.py   MAMMA NPZ → AMASS互換NPZ
02_amass_to_bvh_blender.py     Add Animation → BVH
03_validate_bvh_blender.py     BVH再読込検証
convert.ps1                    一括実行
```

## 一括実行

```powershell
.\convert.ps1 `
  -InputNpz "C:\path\to\smplx_params_body_id-00.npz" `
  -OutputBvh "C:\path\to\result.bvh" `
  -Fps 30 `
  -Validate
```

正立しているものの正面が180度逆の場合のみ `-RotateZ 180` を追加します。

## 手動操作

まずAMASS互換NPZだけ生成します。

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" `
  --background --factory-startup `
  --python ".\01_convert_mamma_to_amass.py" `
  -- "C:\path\to\input.npz" "C:\path\to\result_amass.npz" --fps 30
```

次にBlender GUIでSMPL-Xパネルを開き、`Add Animation` から変換済みNPZを選びます。

```text
Type: SMPL-X
Version: SMPL-X Locked Head
Body: Neutral
Format: AMASS
Body rest position: SMPL-X
Hand pose reference: Relaxed
Target framerate: 30
Keyframed corrective pose weights: OFF
```

生成されたArmatureだけを選び、`File → Export → Motion Capture (.bvh)` を実行します。

```text
Frame Start: 1
Frame End: アニメーション最終フレーム
Scale: 1.0
Rotation: Native
Root Translation Only: OFF
```

## 制約

- FPSは元NPZにないため入力映像に合わせて指定します。
- MotionBuilder用骨名、Tスタンス、Character Definitionは作りません。
- 足滑り除去やリターゲティングは行いません。
- 撮影空間の正面方向は自動判定しません。
