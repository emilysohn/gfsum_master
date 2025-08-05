# gfs_vertical_slice.py — Stable Version

import os
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from datetime import datetime, timedelta

# === CONFIG ===
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_actual/processed_netcdf"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/gfs_actual/vertical"
flight_csv = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/csv/interpolated_path_800.csv"
os.makedirs(output_dir, exist_ok=True)

flight_df = pd.read_csv(flight_csv)
x_axis = np.arange(len(flight_df))
flight_points = flight_df[['lon', 'lat']].values

# Only levels that exist in both TMP and TCDC
common_levels = [1000, 925, 850, 700, 500, 300, 250]

start_time = datetime(2025, 7, 16, 0)
end_time = datetime(2025, 7, 21, 18)
time_step = timedelta(hours=6)

# === Interpolation function ===
def interpolate_variable(paths, var_prefix, levels):
    results = []
    for path in paths:
        ds = xr.open_dataset(path)
        all_levels = []
        for level in levels:
            var_name = f"{var_prefix}_{int(level)}mb"
            if var_name not in ds:
                continue
            da = ds[var_name]
            lons, lats = np.meshgrid(da.longitude.values, da.latitude.values)
            values = da.values[0]
            interp_vals = griddata(
                (lons.flatten(), lats.flatten()),
                values.flatten(),
                (flight_df["lon"], flight_df["lat"]),
                method="linear"
            )
            all_levels.append(interp_vals)
        results.append(np.vstack(all_levels))
    return np.mean(results, axis=0)

# === Main time loop ===
current_time = start_time
while current_time + time_step <= end_time:
    t1 = current_time
    t2 = current_time + time_step
    t1_str = t1.strftime("%Y%m%d_t%Hz")
    t2_str = t2.strftime("%Y%m%d_t%Hz")

    paths_tcdc = [os.path.join(base_dir, t1_str, "TCDC.nc"),
                  os.path.join(base_dir, t2_str, "TCDC.nc")]
    paths_tmp = [os.path.join(base_dir, t1_str, "TMP.nc"),
                 os.path.join(base_dir, t2_str, "TMP.nc")]

    if not all(os.path.exists(p) for p in paths_tcdc + paths_tmp):
        print(f"⏭️ Skipping {t1_str} → {t2_str}: missing files")
        current_time += time_step
        continue

    print(f"🔄 Processing: {t1_str} → {t2_str}")
    try:
        tcdc_interp = interpolate_variable(paths_tcdc, "TCDC", common_levels)
        tmp_interp = interpolate_variable(paths_tmp, "TMP", common_levels)
        tmp_interp = gaussian_filter(tmp_interp, sigma=1.0)

        pressure = np.array(common_levels)
        X, Y = np.meshgrid(x_axis, pressure)

        fig, ax = plt.subplots(figsize=(14, 6))
        p1 = ax.pcolormesh(X, Y, tcdc_interp, shading="auto", cmap="Blues", vmin=0, vmax=1)
        cbar = fig.colorbar(p1, ax=ax, pad=0.01)
        cbar.set_label("Total Cloud Cover (0–1)")

        cs = ax.contour(X, Y, tmp_interp, colors="white", linewidths=1)
        ax.clabel(cs, fmt="%.0f", fontsize=8)

        ax.set_title(f"Vertical Slice: TCDC (shaded) + TMP (contours)\n{t1_str} → {t2_str}")
        ax.set_xlabel("Flight Path Position")
        ax.set_ylabel("Pressure (hPa)")
        ax.invert_yaxis()
        ax.yaxis.set_major_locator(MultipleLocator(100))

        save_path = os.path.join(output_dir, f"vertical_slice_{t1_str}_to_{t2_str}.png")
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"✅ Saved: {save_path}")
    except Exception as e:
        print(f"❌ Error during {t1_str} → {t2_str}: {e}")

    current_time += time_step
