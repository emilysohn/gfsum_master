# tmp_stats_gfs.py
import os
import xarray as xr
import pandas as pd
import numpy as np

# === Config ===
source = "gfs_actual"
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_actual/processed_netcdf"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/tmp_5day_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

levels = ["1000mb", "850mb", "700mb", "500mb", "300mb"]
start_date = pd.to_datetime("2025-07-16")
end_date = pd.to_datetime("2025-07-21")

# Accumulate stats per level
level_data = {lvl: [] for lvl in levels}

for date in pd.date_range(start_date, end_date, freq="6H"):
    timestamp = date.strftime("%Y%m%d_t%Hz")
    file_path = os.path.join(base_dir, timestamp, "TMP.nc")
    if not os.path.exists(file_path):
        print(f"⚠️ Missing: {file_path}")
        continue

    ds = xr.open_dataset(file_path)
    for level in levels:
        varname = f"TMP_{level}"
        if varname in ds:
            level_data[level].append(ds[varname].values)

# Compute daily stats
records = []
for level in levels:
    arr = np.stack(level_data[level])
    records.append({
        "Level": level,
        "TMP_min": float(np.nanmin(arr)),
        "TMP_max": float(np.nanmax(arr)),
        "TMP_mean": float(np.nanmean(arr))
    })

df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved GFS TMP summary to {output_csv}")
