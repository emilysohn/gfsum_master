# tmp_5day_summary_um.py — 5-day summary of TMP (min, max, mean)

import os
import xarray as xr
import pandas as pd
import numpy as np

# === Config ===
source = "um"
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/um/u-dq502/0716"
output_csv = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/tmp_5day_summary.csv"
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

pot_path = os.path.join(base_dir, "glm_air_potential_temperature_m01s00i004.nc")
pres_path = os.path.join(base_dir, "glm_air_pressure_m01s00i408.nc")

ds_pot = xr.open_dataset(pot_path)
ds_pres = xr.open_dataset(pres_path)

theta = ds_pot["air_potential_temperature"]  # (time, level, lat, lon)
pres = ds_pres["air_pressure"]               # (time, level, lat, lon)

# Constants
p0 = 100000  # reference pressure in Pa
R_over_cp = 0.286  # Rd/cp

# Target pressures in Pa
target_pressures = [100000, 85000, 70000, 50000, 30000]
pressure_labels = ["1000mb", "850mb", "700mb", "500mb", "300mb"]

summary_records = []

for p_target, label in zip(target_pressures, pressure_labels):
    print(f"📍 Processing level: {label}")
    all_temps = []

    for t in range(len(theta.time)):
        theta_t = theta.isel(time=t)
        pres_t = pres.isel(time=t)

        # Compute temperature field
        temp_t = theta_t * (pres_t / p0) ** R_over_cp

        # Get vertical mean pressure profile (1D: model_level_number)
        p_profile = pres_t.mean(dim=["latitude", "longitude"])

        try:
            # Find nearest model level to target pressure
            level_idx = np.abs(p_profile - p_target).argmin(dim="model_level_number")
            level_val = p_profile.model_level_number[level_idx].item()

            # Interpolate temperature at that model level
            temp_interp = temp_t.interp(model_level_number=level_val)
            all_temps.append(temp_interp)
        except Exception as e:
            print(f"⚠️ Skipping level {label} at time {t}: {e}")

    if all_temps:
        all_data = xr.concat(all_temps, dim="time")
        summary_records.append({
            "Level": label,
            "TMP_min": float(all_data.min().values),
            "TMP_max": float(all_data.max().values),
            "TMP_mean": float(all_data.mean().values)
        })

# Save CSV
df = pd.DataFrame(summary_records)
df.to_csv(output_csv, index=False)
print(f"✅ Saved 5-day TMP summary to {output_csv}")
