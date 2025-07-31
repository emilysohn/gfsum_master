# === convert.py (append version using wgrib2 only) ===
import os
import yaml
import subprocess
from datetime import datetime, timedelta

# Load configuration
with open(os.path.join(os.path.dirname(__file__), "../config.yaml")) as f:
    config = yaml.safe_load(f)

raw_dir = config["raw_grib_dir"]
temp_dir = config["temp_grib_dir"]
out_dir = config["processed_netcdf_dir"]
os.makedirs(temp_dir, exist_ok=True)

start_time = datetime.strptime(config["start_time"], "%Y-%m-%d %H:%M")
end_time = datetime.strptime(config["end_time"], "%Y-%m-%d %H:%M")
step = timedelta(hours=config["step_hours"])
forecast_hour = int(config["forecast_hour"])
variables = config["variables"]

def grib_exists(grib_file, match_string):
    try:
        output = subprocess.check_output(["wgrib2", "-s", grib_file], encoding="utf-8")
        return match_string in output
    except Exception:
        return False

def convert_one_time(init_time):
    date_str = init_time.strftime("%Y%m%d")
    hour_str = init_time.strftime("%H")
    fxx = f"{forecast_hour:03d}"
    grib_file = os.path.join(raw_dir, f"gfs_{date_str}_t{hour_str}z_f{fxx}.grib2")
    timestamp = f"{date_str}_t{hour_str}z"
    out_time_dir = os.path.join(out_dir, timestamp)
    os.makedirs(out_time_dir, exist_ok=True)

    for var in variables:
        name = var["name"]
        levels = var.get("levels", [])
        final_nc = os.path.join(out_time_dir, f"{name}.nc")
        if os.path.exists(final_nc):
            os.remove(final_nc)  # Ensure fresh start

        for i, lev in enumerate(levels):
            match_str = f":{name}:{lev}:"
            if not grib_exists(grib_file, match_str):
                print(f"⚠️ Skipping {name} {lev} — not found in GRIB")
                continue

            clean_lev = lev.replace(" ", "").replace(".", "")
            temp_grib = os.path.join(temp_dir, f"{name}_{clean_lev}_{timestamp}.grb2")
            extract_cmd = ["wgrib2", grib_file, "-match", match_str, "-grib_out", temp_grib]
            print("📦 Extracting:", " ".join(extract_cmd))
            try:
                subprocess.run(extract_cmd, check=True)

                nc_cmd = ["wgrib2", temp_grib, "-netcdf", final_nc]
                if i > 0:
                    nc_cmd.insert(1, "-append")  # Only append after the first

                subprocess.run(nc_cmd, check=True)
                print(f"✅ Added {lev} to {final_nc}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed: {e}")
            finally:
                if os.path.exists(temp_grib):
                    os.remove(temp_grib)

# === Run over all timestamps ===
current = start_time
while current <= end_time:
    convert_one_time(current)
    current += step
