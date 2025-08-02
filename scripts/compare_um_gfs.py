import os
from PIL import Image
import matplotlib.pyplot as plt

# === CONFIGURATION ===
gfs_root = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/gfs_actual"
um_root = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/um"
output_root = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/comparisons"

# Special folders not structured by variable/level
special_vars = ["rgb_tcdc", "cdc_pres"]

def compare_and_save(gfs_img_path, um_img_path, output_path):
    gfs_img = Image.open(gfs_img_path)
    um_img = Image.open(um_img_path)

    if gfs_img.size != um_img.size:
        um_img = um_img.resize(gfs_img.size)

    fig, axs = plt.subplots(1, 2, figsize=(16, 6))
    axs[0].imshow(gfs_img)
    axs[0].set_title("GFS")
    axs[1].imshow(um_img)
    axs[1].set_title("UM")

    for ax in axs:
        ax.axis("off")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

# === Process standard variable/level plots ===
print("🔍 Scanning variable/level structure...")
for var in os.listdir(gfs_root):
    if var in special_vars or not os.path.isdir(os.path.join(gfs_root, var)):
        continue
    gfs_var_dir = os.path.join(gfs_root, var)
    um_var_dir = os.path.join(um_root, var)
    if not os.path.exists(um_var_dir):
        continue

    for level in os.listdir(gfs_var_dir):
        gfs_level_dir = os.path.join(gfs_var_dir, level)
        um_level_dir = os.path.join(um_var_dir, level)
        if not os.path.exists(um_level_dir):
            continue

        print(f"📂 Comparing {var} at {level}...")
        output_dir = os.path.join(output_root, var, level)

        gfs_files = sorted(f for f in os.listdir(gfs_level_dir) if f.endswith(".png"))
        um_files = sorted(f for f in os.listdir(um_level_dir) if f.endswith(".png"))
        common_files = set(gfs_files).intersection(um_files)

        for file in common_files:
            gfs_img_path = os.path.join(gfs_level_dir, file)
            um_img_path = os.path.join(um_level_dir, file)
            timestamp = file.replace(".png", "").split(f"{level}_")[-1]
            out_path = os.path.join(output_dir, f"compare_{timestamp}.png")
            compare_and_save(gfs_img_path, um_img_path, out_path)

special_base_gfs = os.path.join(gfs_root, "{var}")
special_base_um = os.path.join(um_root, "{var}")
special_output = os.path.join(output_root, "{var}")

for var in special_vars:
    if var == "cdc_pres":
        subcategories = ["low", "mid", "high"]
        for sub in subcategories:
            gfs_dir = os.path.join(special_base_gfs.format(var=var), sub)
            um_dir = os.path.join(special_base_um.format(var=var), sub)
            out_dir = os.path.join(special_output.format(var=var), sub)
            if not os.path.exists(gfs_dir) or not os.path.exists(um_dir):
                continue

            gfs_files = sorted(f for f in os.listdir(gfs_dir) if f.endswith(".png"))
            um_files = sorted(f for f in os.listdir(um_dir) if f.endswith(".png"))
            common_files = set(gfs_files).intersection(um_files)

            for file in common_files:
                gfs_img_path = os.path.join(gfs_dir, file)
                um_img_path = os.path.join(um_dir, file)
                timestamp = file.replace(".png", "")
                output_path = os.path.join(out_dir, f"compare_{timestamp}.png")
                compare_and_save(gfs_img_path, um_img_path, output_path)

    else:
        gfs_dir = special_base_gfs.format(var=var)
        um_dir = special_base_um.format(var=var)
        out_dir = special_output.format(var=var)
        if not os.path.exists(gfs_dir) or not os.path.exists(um_dir):
            continue

        gfs_files = sorted(f for f in os.listdir(gfs_dir) if f.endswith(".png"))
        um_files = sorted(f for f in os.listdir(um_dir) if f.endswith(".png"))
        common_files = set(gfs_files).intersection(um_files)

        for file in common_files:
            gfs_img_path = os.path.join(gfs_dir, file)
            um_img_path = os.path.join(um_dir, file)
            timestamp = file.replace(".png", "")
            output_path = os.path.join(out_dir, f"compare_{timestamp}.png")
            compare_and_save(gfs_img_path, um_img_path, output_path)


print("✅ All comparisons complete.")
