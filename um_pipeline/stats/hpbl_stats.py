# hpbl_stats.py (UM - daily version)
import os
import xarray as xr
import pandas as pd

# Configuration
source = "um"
base_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/data/{source}/u-dq502/0716"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/hpbl_daily_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# Load dataset
filepath = os.path.join(base_dir, "glm_m01s03i073_m01s03i073.nc")
ds = xr.open_dataset(filepath)
hpbl = ds["m01s03i073"]  # (time, lat, lon)

# Convert time to datetime and group by day
hpbl["time"] = pd.to_datetime(hpbl.time.values)
daily_groups = hpbl.groupby("time.date")

# Compute stats
records = []
for day, data in daily_groups:
    records.append({
        "date": str(day),
        "mean_HPBL_m": float(data.mean().values),
        "min_HPBL_m": float(data.min().values),
        "max_HPBL_m": float(data.max().values)
    })

# Save
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved daily HPBL summary to {output_csv}")
