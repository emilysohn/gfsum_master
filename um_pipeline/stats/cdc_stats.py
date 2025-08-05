# cdc_stats.py (UM - daily version)
import os
import xarray as xr
import numpy as np
import pandas as pd

# Config
source = "um"
base_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/data/{source}/u-dq502/0716"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/cdc_daily_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# Files and variable names
files = {
    "LCDC": ("glm_low_type_cloud_area_fraction_m01s09i203.nc", "low_type_cloud_area_fraction"),
    "MCDC": ("glm_medium_type_cloud_area_fraction_m01s09i204.nc", "medium_type_cloud_area_fraction"),
    "HCDC": ("glm_high_type_cloud_area_fraction_m01s09i205.nc", "high_type_cloud_area_fraction"),
}

# Load datasets once
datasets = {}
for key, (filename, varname) in files.items():
    path = os.path.join(base_dir, filename)
    ds = xr.open_dataset(path)
    data = ds[varname]  # shape: (time, lat, lon)
    datasets[key] = data

# Combine into one dataset with daily means
daily_means = {}
for key, data in datasets.items():
    daily = data.groupby("time.date").mean(dim=["time", "latitude", "longitude"])
    daily_means[key] = daily

# Assemble into DataFrame
dates = daily_means["LCDC"]["date"].values.astype(str)
records = []
for i, date in enumerate(dates):
    lcdc_val = float(daily_means["LCDC"].isel(date=i).values)
    mcdc_val = float(daily_means["MCDC"].isel(date=i).values)
    hcdc_val = float(daily_means["HCDC"].isel(date=i).values)
    
    means = {
        "LCDC": lcdc_val,
        "MCDC": mcdc_val,
        "HCDC": hcdc_val
    }
    dominant_type = max(means, key=means.get)
    dominant_val = means[dominant_type] * 100  # convert to percent

    records.append({
        "date": date,
        "LCDC_mean": lcdc_val,
        "MCDC_mean": mcdc_val,
        "HCDC_mean": hcdc_val,
        "dominant_type": dominant_type.replace("CDC", "").title(),
        "dominant_coverage_percent": dominant_val
    })

# Save
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved daily CDC summary to {output_csv}")
