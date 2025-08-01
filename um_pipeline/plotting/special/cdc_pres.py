# um_pipeline/plotting/special/cdc_pres.py

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from um_pipeline.plotting.utils import setup_map, create_output_dir

# === CONFIGURATION ===
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/um/NC_Files/u-dq502/0716"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/um/cdc_pres"
create_output_dir(output_dir)

start_time = datetime(2025, 6, 17, 0)
end_time = datetime(2025, 6, 24, 18)
time_step = timedelta(hours=3)

file_map = {
    "LCDC": ("glm_low_type_cloud_area_fraction_m01s09i203.nc", "low_type_cloud_area_fraction", "Blues", "Low Cloud Cover (0–1)"),
    "MCDC": ("glm_medium_type_cloud_area_fraction_m01s09i204.nc", "medium_type_cloud_area_fraction", "Greens", "Mid Cloud Cover (0–1)"),
    "HCDC": ("glm_high_type_cloud_area_fraction_m01s09i205.nc", "high_type_cloud_area_fraction", "Reds", "High Cloud Cover (0–1)"),
    "PRES": ("glm_air_pressure_at_surface_m01s16i222.nc", "air_pressure_at_surface")
}

for key in ["LCDC", "MCDC", "HCDC"]:
    filename, varname, cmap, label = file_map[key]
    for valid_time in [start_time + i*time_step for i in range(int((end_time - start_time) / time_step) + 1)]:
        timestamp = valid_time.strftime("%Y%m%d_t%Hz")
        cloud_path = os.path.join(base_dir, timestamp, filename)
        pres_path = os.path.join(base_dir, timestamp, file_map["PRES"][0])

        if not os.path.exists(cloud_path) or not os.path.exists(pres_path):
            print(f"⚠️ Missing files for {timestamp}, skipping {key}")
            continue

        try:
            cloud = xr.open_dataset(cloud_path)[varname].squeeze()
            pres = xr.open_dataset(pres_path)[file_map["PRES"][1]].squeeze() / 100  # Pa → hPa

            lon = cloud["longitude"]
            lat = cloud["latitude"]
            lon2d, lat2d = np.meshgrid(lon, lat)

            fig, ax = setup_map()

            pcm = ax.pcolormesh(lon2d, lat2d, cloud,
                                cmap=cmap, vmin=0, vmax=1,
                                transform=ax.projection)

            cbar = fig.colorbar(pcm, ax=ax, orientation="vertical", shrink=0.6, pad=0.02)
            cbar.set_label(label)

            ax.contour(pres["longitude"], pres["latitude"], pres,
                       levels=np.arange(960, 1040, 4),
                       colors="tan", linewidths=0.8, transform=ax.projection)

            ax.set_title(f"{label} with Sea-Level Pressure (hPa)\nValid: {valid_time:%Y-%m-%d %H:%MZ}")

            fname = f"{key.lower()}_pres_{timestamp}.png"
            plt.savefig(os.path.join(output_dir, fname), dpi=150, bbox_inches="tight")
            plt.close()

        except Exception as e:
            print(f"❌ Failed to plot {key} for {timestamp}: {e}")
