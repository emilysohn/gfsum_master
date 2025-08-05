# hpbl_stats.py
import os
import xarray as xr
import pandas as pd

source = "gfs_forecasted"
dates = pd.date_range("2025-07-14", "2025-07-19", freq="D")
base_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/data/{source}/processed_netcdf"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/hpbl_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

records = []
for date in dates:
    timestamp = date.strftime("%Y%m%d")
    try:
        path = os.path.join(base_dir, f"{timestamp}_t00z/HPBL.nc")
        ds = xr.open_dataset(path)
        hpbl = list(ds.data_vars.values())[0]

        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "mean_HPBL_m": float(hpbl.mean().values),
            "min_HPBL_m": float(hpbl.min().values),
            "max_HPBL_m": float(hpbl.max().values)
        })

    except FileNotFoundError:
        print(f"⚠️ Missing data for {timestamp}")
        continue

df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved HPBL summary to {output_csv}")

