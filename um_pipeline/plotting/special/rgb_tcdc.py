# um_pipeline/plotting/special/rgb_tcdc.py

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime
from um_pipeline.plotting.utils import create_output_dir, setup_map
import cartopy.crs as ccrs

# === CONFIGURATION ===
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/um/u-dq502/0716"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/um/rgb_tcdc"
create_output_dir(output_dir)

file_map = {
    "LCDC": ("glm_low_type_cloud_area_fraction_m01s09i203.nc", "low_type_cloud_area_fraction"),
    "MCDC": ("glm_medium_type_cloud_area_fraction_m01s09i204.nc", "medium_type_cloud_area_fraction"),
    "HCDC": ("glm_high_type_cloud_area_fraction_m01s09i205.nc", "high_type_cloud_area_fraction"),
    "PRES": ("glm_air_pressure_at_sea_level_m01s16i222.nc", "air_pressure_at_sea_level")
}

# === Load full datasets once ===
lcdc = xr.open_dataset(os.path.join(base_dir, file_map["LCDC"][0]))[file_map["LCDC"][1]] 
mcdc = xr.open_dataset(os.path.join(base_dir, file_map["MCDC"][0]))[file_map["MCDC"][1]] 
hcdc = xr.open_dataset(os.path.join(base_dir, file_map["HCDC"][0]))[file_map["HCDC"][1]]
pres = xr.open_dataset(os.path.join(base_dir, file_map["PRES"][0]))[file_map["PRES"][1]] / 100

# === Loop through time every 6 hours
for i, timestamp in enumerate(lcdc.time.values):
    dt = np.datetime64(timestamp).astype('datetime64[h]').astype(datetime)
    if dt.hour % 6 != 0:
        continue

    try:
        lcdc_t = lcdc.sel(time=timestamp).squeeze()
        mcdc_t = mcdc.sel(time=timestamp).squeeze()
        hcdc_t = hcdc.sel(time=timestamp).squeeze()
        pres_t = pres.sel(time=timestamp).squeeze()

        lon = lcdc["longitude"]
        lat = lcdc["latitude"]
        lon2d, lat2d = np.meshgrid(lon, lat)

        fig, ax, proj = setup_map()
        b = ax.pcolormesh(lon2d, lat2d, lcdc_t, cmap="Blues", vmin=0, vmax=1, alpha=0.3, transform=proj)
        g = ax.pcolormesh(lon2d, lat2d, mcdc_t, cmap="YlGn", vmin=0, vmax=1, alpha=0.3, transform=proj)
        r = ax.pcolormesh(lon2d, lat2d, hcdc_t, cmap="OrRd", vmin=0, vmax=1, alpha=0.3, transform=proj)

        ax.contour(pres["longitude"], pres["latitude"], pres_t,
                   levels=np.arange(960, 1040, 4),
                   colors="tan", linewidths=0.7, transform=proj)

        ax.set_title(
            f"DLR-Style Layered Cloud Cover and MSLP\nValid: {dt:%Y-%m-%d %H:%MZ}",
            fontsize=14
        )

        # === Vertically stacked colorbars
        cbar_ax_r = fig.add_axes([0.92, 0.65, 0.015, 0.2])
        cbar_ax_g = fig.add_axes([0.92, 0.42, 0.015, 0.2])
        cbar_ax_b = fig.add_axes([0.92, 0.19, 0.015, 0.2])

        cbar_r = fig.colorbar(r, cax=cbar_ax_r)
        cbar_r.set_label("High Cloud", fontsize=9)
        cbar_g = fig.colorbar(g, cax=cbar_ax_g)
        cbar_g.set_label("Mid Cloud", fontsize=9)
        cbar_b = fig.colorbar(b, cax=cbar_ax_b)
        cbar_b.set_label("Low Cloud", fontsize=9)

        timestamp_str = dt.strftime("%Y%m%d_t%Hz")
        fname = f"dlr_combined_{timestamp_str}.png"
        plt.savefig(os.path.join(output_dir, fname), dpi=150, bbox_inches="tight")
        plt.close()

    except Exception as e:
        print(f"❌ Failed to plot for {timestamp}: {e}")
