"""Re-import a BVH into a clean Blender scene and validate its basic structure."""

import argparse
import sys
from pathlib import Path

import bpy


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Validate a generated BVH")
    parser.add_argument("input", type=Path)
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--fps", type=int, default=30)
    return parser.parse_args(argv)


def main():
    args = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    result = bpy.ops.import_anim.bvh(
        filepath=str(args.input.resolve()),
        frame_start=1,
        global_scale=1.0,
        use_fps_scale=False,
        update_scene_fps=True,
        update_scene_duration=True,
        rotate_mode="NATIVE",
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"BVH import failed: {result}")
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    if len(armatures) != 1:
        raise RuntimeError(f"Expected one armature, found {len(armatures)}")
    armature = armatures[0]
    action = armature.animation_data.action if armature.animation_data else None
    if action is None:
        raise RuntimeError("Imported BVH contains no animation")
    actual_range = tuple(int(value) for value in action.frame_range)
    if actual_range[0] != 1 or actual_range[1] < 1:
        raise RuntimeError(f"Invalid frame range: {actual_range}")
    if args.frames is not None and actual_range != (1, args.frames):
        raise RuntimeError(f"Frame range mismatch: {actual_range}, expected (1, {args.frames})")
    if bpy.context.scene.render.fps != args.fps:
        raise RuntimeError(f"FPS mismatch: {bpy.context.scene.render.fps}, expected {args.fps}")
    print(f"VALIDATED bones={len(armature.data.bones)} frames={actual_range[1]} fps={args.fps}")


if __name__ == "__main__":
    main()
