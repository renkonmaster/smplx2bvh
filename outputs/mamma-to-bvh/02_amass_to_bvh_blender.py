"""Load an AMASS-compatible SMPL-X NPZ with the installed add-on and export BVH.

This script must be executed by Blender with the SMPL-X Blender Add-on enabled.
"""

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Import AMASS-compatible SMPL-X animation and export BVH")
    parser.add_argument("input", type=Path, help="AMASS-compatible SMPL-X .npz")
    parser.add_argument("output", type=Path, help="Output .bvh")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--save-blend", type=Path, default=None)
    parser.add_argument("--rotate-z", type=float, default=0.0)
    return parser.parse_args(argv)


def main():
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(args.input)
    if args.output.suffix.lower() != ".bvh":
        raise ValueError("Output path must end in .bvh")
    if not hasattr(bpy.ops.object, "smplx_add_animation"):
        raise RuntimeError("SMPL-X Blender Add-on is not installed or enabled")

    result = bpy.ops.object.smplx_add_animation(
        "EXEC_DEFAULT",
        filepath=str(args.input.resolve()),
        anim_format="AMASS",
        rest_position="SMPL-X",
        hand_reference="RELAXED",
        keyframe_corrective_pose_weights=False,
        target_framerate=args.fps,
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"SMPL-X animation import failed: {result}")

    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    if len(armatures) != 1:
        raise RuntimeError(f"Expected one armature after import, found {len(armatures)}")
    armature = armatures[0]
    action = armature.animation_data.action if armature.animation_data else None
    if action is None:
        raise RuntimeError("Imported animation has no action")
    frame_start, frame_end = (int(value) for value in action.frame_range)

    if args.rotate_z:
        armature.matrix_world = Matrix.Rotation(math.radians(args.rotate_z), 4, "Z") @ armature.matrix_world

    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    bpy.context.scene.render.fps = args.fps

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = bpy.ops.export_anim.bvh(
        filepath=str(args.output.resolve()),
        frame_start=frame_start,
        frame_end=frame_end,
        global_scale=1.0,
        rotate_mode="NATIVE",
        root_transform_only=False,
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"BVH export failed: {result}")

    if args.save_blend:
        args.save_blend.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.save_blend.resolve()))

    print(f"BVH_OUTPUT={args.output.resolve()}")
    print(f"FRAME_RANGE={frame_start}:{frame_end}")
    print(f"FPS={args.fps}")


if __name__ == "__main__":
    main()
