# um_pipeline/plotting/special/cdc_pres.py

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime
from um_pipeline.plotting.utils import setup_map, create_output_dir
import cartopy.crs as ccrs

# === CONFIGURATION ===
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/um/u-dq502/0716"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/um/cdc_pres"
create_output_dir(output_dir)

file_map = {
    "LCDC": ("glm_low_type_cloud_area_fraction_m01s09i203.nc", "low_type_cloud_area_fraction", "Blues", "Low Cloud Cover (0–1)"),
    "MCDC": ("glm_medium_type_cloud_area_fraction_m01s09i204.nc", "medium_type_cloud_area_fraction", "Greens", "Mid Cloud Cover (0–1)"),
    "HCDC": ("glm_high_type_cloud_area_fraction_m01s09i205.nc", "high_type_cloud_area_fraction", "Reds", "High Cloud Cover (0–1)"),
    "PRES": ("glm_air_pressure_at_sea_level_m01s16i222.nc", "air_pressure_at_sea_level")
}
subfolder_map = {
    "LCDC": "low",
    "MCDC": "mid",
    "HCDC": "high"
}

# === Load full cloud and pressure datasets
cloud_datasets = {}
for key in ["LCDC", "MCDC", "HCDC"]:
    filename, varname, *_ = file_map[key]
    cloud_datasets[key] = xr.open_dataset(os.path.join(base_dir, filename))[varname]

pres = xr.open_dataset(os.path.join(base_dir, file_map["PRES"][0]))[file_map["PRES"][1]] / 100

# === Loop over time steps in LCDC only (all cloud types should share time dim)
for timestamp in cloud_datasets["LCDC"].time.values:
    dt = np.datetime64(timestamp).astype("datetime64[h]").astype(datetime)
    if dt.hour % 6 != 0:
        continue

    for key in ["LCDC", "MCDC", "HCDC"]:
        try:
            cloud = cloud_datasets[key].sel(time=timestamp).squeeze()
            pres_t = pres.sel(time=timestamp).squeeze()

            _, _, cmap, label = file_map[key]
            subfolder = subfolder_map[key]
            out_dir = os.path.join(output_dir, subfolder)
            os.makedirs(out_dir, exist_ok=True)

            lon = cloud["longitude"]
            lat = cloud["latitude"]
            lon2d, lat2d = np.meshgrid(lon, lat)

            fig, ax, proj = setup_map()

            pcm = ax.pcolormesh(lon2d, lat2d, cloud,
                                cmap=cmap, vmin=0, vmax=1,
                                transform=proj)

            cbar = fig.colorbar(pcm, ax=ax, orientation="vertical", shrink=0.6, pad=0.02)
            cbar.set_label(label)

            ax.contour(pres["longitude"], pres["latitude"], pres_t,
                       levels=np.arange(960, 1040, 4),
                       colors="tan", linewidths=0.8, transform=proj)

            ax.set_title(f"{label} with Sea-Level Pressure (hPa)\nValid: {dt:%Y-%m-%d %H:%MZ}")

            timestamp_str = dt.strftime("%Y%m%d_t%Hz")
            fname = f"{key.lower()}_pres_{timestamp_str}.png"
            plt.savefig(os.path.join(out_dir, fname), dpi=150, bbox_inches="tight")
            plt.close()

        except Exception as e:
            print(f"❌ Failed to plot {key} for {timestamp}: {e}")
