# spfh_stats_5day_summary.py (UM - 5-day average)
import os
import xarray as xr
import pandas as pd

# === Configuration ===
source = "um"
levels = {
    "1000mb": 1,
    "850mb": 11,
    "700mb": 18,
    "500mb": 26,
    "300mb": 33
}
base_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/data/{source}/u-dq502/0716"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/spfh_5day_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# === Load dataset ===
file_path = os.path.join(base_dir, "glm_specific_humidity_m01s00i010.nc")
ds = xr.open_dataset(file_path)
spfh = ds["specific_humidity"]  # (time, model_level_number, lat, lon)

# Convert time to datetime
ds["time"] = pd.to_datetime(ds["time"].values)

# === Compute summary across all time steps for each level ===
records = []
for level_str, level_idx in levels.items():
    try:
        level_data = spfh[:, level_idx, :, :]  # shape: (time, lat, lon)
        records.append({
            "level": level_str,
            "SPFH_min": float(level_data.min().values),
            "SPFH_max": float(level_data.max().values),
            "SPFH_mean": float(level_data.mean().values)
        })
    except IndexError:
        print(f"⚠️ Level {level_str} index {level_idx} missing")
        continue

# === Save ===
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved 5-day SPFH summary to {output_csv}")
