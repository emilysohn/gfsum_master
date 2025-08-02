import os
import subprocess

def make_mp4s(input_root, output_root, fps=1):
    for root, _, files in os.walk(input_root):
        png_files = sorted([f for f in files if f.endswith(".png")])
        if not png_files:
            continue

        rel_path = os.path.relpath(root, input_root)
        output_dir = os.path.join(output_root, rel_path)
        os.makedirs(output_dir, exist_ok=True)
        mp4_name = os.path.join(output_dir, f"{os.path.basename(root)}.mp4")

        print(f"🎞️ Creating MP4: {mp4_name}")
        
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-pattern_type", "glob",
                "-i", "*.png",
                "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                mp4_name
            ], cwd=root, check=True)

        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg failed in {root}: {e}")

if __name__ == "__main__":
    input_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots"
    output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/mp4s"
    make_mp4s(input_dir, output_dir)
