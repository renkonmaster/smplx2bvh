"""Convert a MAMMA ma_3d NPZ into the key schema expected by the SMPL-X add-on.

This script only rewrites the NPZ schema. It does not use bpy and does not create BVH.
Run with any Python containing NumPy, including Blender's bundled Python.
"""

import argparse
import sys
from pathlib import Path

import numpy as np


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Convert MAMMA SMPL-X NPZ to AMASS-compatible NPZ")
    parser.add_argument("input", type=Path, help="MAMMA smplx_params_body_id-XX.npz")
    parser.add_argument("output", type=Path, help="Output AMASS-compatible .npz")
    parser.add_argument("--fps", type=int, default=30, help="Actual source frame rate")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(args.input)
    if args.output.suffix.lower() != ".npz":
        raise ValueError("Output path must end in .npz")
    if args.fps <= 0:
        raise ValueError("FPS must be positive")

    with np.load(args.input, allow_pickle=True) as src:
        required = ("smplx_pose", "smplx_betas", "smplx_translation")
        missing = [key for key in required if key not in src]
        if missing:
            raise ValueError(f"Not a supported MAMMA parameter file; missing keys: {missing}")
        poses = np.asarray(src["smplx_pose"], dtype=np.float32)
        betas = np.asarray(src["smplx_betas"], dtype=np.float32).squeeze()
        trans = np.asarray(src["smplx_translation"], dtype=np.float32)

    if poses.ndim != 2 or poses.shape[1] != 165:
        raise ValueError(f"Expected smplx_pose shape (T, 165), got {poses.shape}")
    if trans.shape != (poses.shape[0], 3):
        raise ValueError(f"Expected smplx_translation shape ({poses.shape[0]}, 3), got {trans.shape}")
    if betas.ndim != 1:
        raise ValueError(f"Expected smplx_betas to reduce to one vector, got {betas.shape}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        poses=poses,
        betas=betas,
        trans=trans,
        gender=np.array("neutral"),
        mocap_framerate=np.array(args.fps, dtype=np.int32),
    )
    print(f"AMASS_OUTPUT={args.output.resolve()}")
    print(f"FRAMES={poses.shape[0]}")
    print(f"POSE_DIMS={poses.shape[1]}")
    print(f"FPS={args.fps}")


if __name__ == "__main__":
    main()
