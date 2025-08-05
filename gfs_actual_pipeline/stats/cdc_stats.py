# cdc_stats.py
import os
import xarray as xr
import numpy as np
import pandas as pd

source = "gfs_actual"
dates = pd.date_range("2025-07-16", "2025-07-21", freq="D")
base_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/data/{source}/processed_netcdf"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/cdc_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

records = []
for date in dates:
    timestamp = date.strftime("%Y%m%d")
    try:
        lcdc_path = os.path.join(base_dir, f"{timestamp}_t00z/LCDC.nc")
        mcdc_path = os.path.join(base_dir, f"{timestamp}_t00z/MCDC.nc")
        hcdc_path = os.path.join(base_dir, f"{timestamp}_t00z/HCDC.nc")

        lcdc = list(xr.open_dataset(lcdc_path).data_vars.values())[0]
        mcdc = list(xr.open_dataset(mcdc_path).data_vars.values())[0]
        hcdc = list(xr.open_dataset(hcdc_path).data_vars.values())[0]

        lcdc_mean = float(lcdc.mean().values)
        mcdc_mean = float(mcdc.mean().values)
        hcdc_mean = float(hcdc.mean().values)

        dominant_vals = {"Low": lcdc_mean, "Mid": mcdc_mean, "High": hcdc_mean}
        dominant_type = max(dominant_vals, key=dominant_vals.get)
        dominant_val = dominant_vals[dominant_type] * 100

        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "LCDC_mean": lcdc_mean,
            "MCDC_mean": mcdc_mean,
            "HCDC_mean": hcdc_mean,
            "dominant_type": dominant_type,
            "dominant_coverage_percent": dominant_val
        })

    except FileNotFoundError:
        print(f"⚠️ Missing data for {timestamp}")
        continue

df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved CDC summary to {output_csv}")
