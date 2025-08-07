# gfs_actual_pipeline/plotting/special/tcdc_tmp_sliced.py

import os
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.ticker import MultipleLocator
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from datetime import datetime, timedelta

# === CONFIGURATION ===
base_tcdc_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_actual/processed_netcdf"
base_tmp_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_actual/processed_netcdf"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/gfs_actual/vertical"
flight_csv = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/csv/interpolated_path_800.csv"

tcdc_levels = [1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50]
start_time = datetime(2025, 7, 16, 0)
end_time = datetime(2025, 7, 21, 18)
time_step = timedelta(hours=6)

# === SETUP ===
os.makedirs(output_dir, exist_ok=True)
flight_df = pd.read_csv(flight_csv)
flight_points = flight_df[['lon', 'lat', 'pressure_hPa']].values
x_axis = np.arange(len(flight_points))

# === Function to load and interpolate a variable ===
def stack_variable(file_paths, var_prefix, levels, label):
    var_interp_all = []
    for path in file_paths:
        ds = xr.open_dataset(path)
        all_interp_vals = []
        for level in levels:
            var_name = f"{var_prefix}_{int(level)}mb"
            if var_name not in ds:
                print(f"⚠️ Missing {var_name} in {path}, skipping.")
                continue
            da = ds[var_name]
            lons, lats = np.meshgrid(da.longitude.values, da.latitude.values)
            interp_vals = griddata(
                (lons.flatten(), lats.flatten()),
                da.values[0].flatten(),
                (flight_df["lon"], flight_df["lat"]),
                method="linear"
            )
            all_interp_vals.append(interp_vals)
        if all_interp_vals:
            stacked = np.vstack(all_interp_vals)
            var_interp_all.append(stacked)
        else:
            print(f"❌ No valid levels found in {path} for {label}")
    if var_interp_all:
        return np.mean(var_interp_all, axis=0)
    else:
        return None

# === Loop over 6-hour slices ===
current_time = start_time
while current_time + time_step <= end_time:
    t1 = current_time
    t2 = current_time + time_step
    t1_str = t1.strftime("%Y%m%d_t%Hz")
    t2_str = t2.strftime("%Y%m%d_t%Hz")

    tcdc_paths = [os.path.join(base_tcdc_dir, t1_str, "TCDC.nc"),
                  os.path.join(base_tcdc_dir, t2_str, "TCDC.nc")]
    tmp_paths = [os.path.join(base_tmp_dir, t1_str, "TMP.nc"),
                 os.path.join(base_tmp_dir, t2_str, "TMP.nc")]

    if not all(os.path.exists(p) for p in tcdc_paths + tmp_paths):
        print(f"⏭️ Skipping {t1_str}–{t2_str}, missing files.")
        current_time += time_step
        continue

    print(f"🔄 Processing: {t1_str} → {t2_str}")
    try:
        tcdc_interp = stack_variable(tcdc_paths, "TCDC", tcdc_levels, "TCDC")
        tmp_interp = stack_variable(tmp_paths, "TMP", tcdc_levels, "TMP")

        if tcdc_interp is None or tmp_interp is None:
            print(f"⚠️ Skipping {t1_str}–{t2_str} due to missing data.")
            current_time += time_step
            continue

        tmp_interp = gaussian_filter(tmp_interp, sigma=1.0)

        pressure = np.array(tcdc_levels)
        X, Y = np.meshgrid(x_axis, pressure)

        fig, ax = plt.subplots(figsize=(14, 6))
        cf = ax.pcolormesh(X, Y, tcdc_interp, shading="auto", cmap="Blues", vmin=0, vmax=1)
        cbar = fig.colorbar(cf, ax=ax, pad=0.01)
        cbar.set_label("Total Cloud Cover (0–1)")

        cs = ax.contour(X, Y, tmp_interp, levels=np.arange(200, 301, 5), colors="white", linewidths=1)
        ax.clabel(cs, fmt="%.0f", fontsize=8)

        ax.set_title(f"TCDC (shaded) + TMP (contours)\n{t1_str} to {t2_str}", fontsize=13)
        ax.set_xlabel("Flight Path Position")
        ax.set_ylabel("Pressure (hPa)")
        ax.invert_yaxis()
        ax.yaxis.set_major_locator(MultipleLocator(100))

        out_path = os.path.join(output_dir, f"tcdc_tmp_slice_{t1_str}_to_{t2_str}.png")
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"✅ Saved: {out_path}")
    except Exception as e:
        print(f"❌ Error for {t1_str} → {t2_str}: {e}")

    current_time += time_step
