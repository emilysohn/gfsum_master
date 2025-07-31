# gfs_pipeline/plotting/make_mp4s.py

import os
import subprocess

def make_mp4s(input_root, output_root, fps=1):

    for dirpath, _, filenames in os.walk(input_root):
        pngs = sorted([f for f in filenames if f.endswith(".png")])
        if not pngs:
            continue

        folder_name = os.path.basename(dirpath.rstrip("/"))
        rel_path = os.path.relpath(dirpath, input_root)
        output_dir = os.path.join(output_root, rel_path)
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{folder_name}.mp4")

        print(f"🎞️ Creating MP4: {output_path}")

        try:
            subprocess.run([
                "ffmpeg", "-y", "-framerate", str(fps),
                "-pattern_type", "glob", "-i", "*.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                output_path
            ], cwd=dirpath, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg failed in {dirpath}: {e}")


if __name__ == "__main__":
    input_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots"
    output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/mp4s"
    make_mp4s(input_dir, output_dir)
