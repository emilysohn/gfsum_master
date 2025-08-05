# spfh_5day_summary.py (GFS version)
import os
import xarray as xr
import pandas as pd
import numpy as np

# === Configuration ===
source = "gfs_actual"
base_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_actual/processed_netcdf"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/spfh_5day_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# GFS timestamps (every 6 hours)
timestamps = pd.date_range("2025-07-16T00:00", "2025-07-21T18:00", freq="6H")
levels = ["1000mb", "850mb", "700mb", "500mb", "300mb"]

# Initialize storage
data = {level: [] for level in levels}

# Loop over timestamps
for timestamp in timestamps:
    ts_str = timestamp.strftime("%Y%m%d_t%Hz")
    filepath = os.path.join(base_dir, ts_str, "SPFH.nc")
    
    if not os.path.exists(filepath):
        print(f"⚠️ Missing file for {ts_str}")
        continue

    ds = xr.open_dataset(filepath)
    
    for level in levels:
        varname = f"SPFH_{level}"
        if varname in ds:
            arr = ds[varname].values  # shape: (lat, lon)
            data[level].append(arr)
        else:
            print(f"⚠️ {varname} missing in {ts_str}")

# Calculate stats across all timestamps
records = []
for level in levels:
    if not data[level]:
        print(f"⚠️ No data available for level {level}")
        continue
    
    stacked = np.stack(data[level], axis=0)  # shape: (time, lat, lon)
    records.append({
        "level": level,
        "SPFH_min": float(np.min(stacked)),
        "SPFH_max": float(np.max(stacked)),
        "SPFH_mean": float(np.mean(stacked))
    })

# Save
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved GFS 5-day SPFH summary to {output_csv}")
