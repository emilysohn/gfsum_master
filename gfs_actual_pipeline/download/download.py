# === download.py ===
import os
import yaml
import requests
from datetime import datetime, timedelta

with open(os.path.join(os.path.dirname(__file__), "../config.yaml")) as f:
    config = yaml.safe_load(f)

start_time = datetime.strptime(config["start_time"], "%Y-%m-%d %H:%M")
end_time = datetime.strptime(config["end_time"], "%Y-%m-%d %H:%M")
step = timedelta(hours=config["step_hours"])
forecast_hour = int(config["forecast_hour"])

raw_dir = config["raw_grib_dir"]
os.makedirs(raw_dir, exist_ok=True)

def download_gfs_file(init_time):
    date_str = init_time.strftime("%Y%m%d")
    hour_str = init_time.strftime("%H")
    fxx = f"{forecast_hour:03d}"
    url = (
        f"https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{date_str}/{hour_str}/atmos/"
        f"gfs.t{hour_str}z.pgrb2.0p25.f{fxx}"
    )
    out_path = os.path.join(raw_dir, f"gfs_{date_str}_t{hour_str}z_f{fxx}.grib2")
    if os.path.exists(out_path):
        print(f"✅ Already exists: {out_path}")
        return
    print(f"⬇️ Downloading: {url}")
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved: {out_path}")
    else:
        print(f"❌ Failed: {url} ({r.status_code})")

current = start_time
while current <= end_time:
    download_gfs_file(current)
    current += step
