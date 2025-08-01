# um_pipeline/plotting/special/rgb_tcdc.py

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from um_pipeline.plotting.utils import setup_map, create_output_dir

# === CONFIGURATION ===
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/um/NC_Files/u-dq502/0716"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/um/rgb_tcdc"
create_output_dir(output_dir)

start_time = datetime(2025, 6, 17, 0)
end_time = datetime(2025, 6, 24, 18)
time_step = timedelta(hours=3)

file_map = {
    "LCDC": ("glm_low_type_cloud_area_fraction_m01s09i203.nc", "low_type_cloud_area_fraction"),
    "MCDC": ("glm_medium_type_cloud_area_fraction_m01s09i204.nc", "medium_type_cloud_area_fraction"),
    "HCDC": ("glm_high_type_cloud_area_fraction_m01s09i205.nc", "high_type_cloud_area_fraction"),
    "PRES": ("glm_air_pressure_at_surface_m01s16i222.nc", "air_pressure_at_surface")
}

for valid_time in [start_time + i*time_step for i in range(int((end_time - start_time) / time_step) + 1)]:
    timestamp = valid_time.strftime("%Y%m%d_t%Hz")

    lcdc_path = os.path.join(base_dir, timestamp, file_map["LCDC"][0])
    mcdc_path = os.path.join(base_dir, timestamp, file_map["MCDC"][0])
    hcdc_path = os.path.join(base_dir, timestamp, file_map["HCDC"][0])
    pres_path = os.path.join(base_dir, timestamp, file_map["PRES"][0])

    if not all(os.path.exists(p) for p in [lcdc_path, mcdc_path, hcdc_path, pres_path]):
        print(f"⚠️ Missing one or more files for {timestamp}, skipping.")
        continue

    try:
        lcdc = xr.open_dataset(lcdc_path)[file_map["LCDC"][1]].squeeze()
        mcdc = xr.open_dataset(mcdc_path)[file_map["MCDC"][1]].squeeze()
        hcdc = xr.open_dataset(hcdc_path)[file_map["HCDC"][1]].squeeze()
        pres = xr.open_dataset(pres_path)[file_map["PRES"][1]].squeeze() / 100

        lon = lcdc["longitude"]
        lat = lcdc["latitude"]
        lon2d, lat2d = np.meshgrid(lon, lat)

        fig, ax = setup_map()

        r = ax.pcolormesh(lon2d, lat2d, hcdc, cmap="Reds", vmin=0, vmax=1, alpha=0.4, transform=ax.projection)
        g = ax.pcolormesh(lon2d, lat2d, mcdc, cmap="Greens", vmin=0, vmax=1, alpha=0.4, transform=ax.projection)
        b = ax.pcolormesh(lon2d, lat2d, lcdc, cmap="Blues", vmin=0, vmax=1, alpha=0.4, transform=ax.projection)

        ax.contour(pres["longitude"], pres["latitude"], pres,
                   levels=np.arange(960, 1040, 4),
                   colors="tan", linewidths=0.7, transform=ax.projection)

        ax.set_title(
            f"DLR-Style Layered Cloud Cover and MSLP\n"
            f"Valid: {valid_time:%Y-%m-%d %H:%MZ}",
            fontsize=13
        )

        cbar_r = fig.colorbar(r, ax=ax, orientation="vertical", shrink=0.45, pad=0.01)
        cbar_r.set_label("High Cloud", fontsize=9)
        cbar_g = fig.colorbar(g, ax=ax, orientation="vertical", shrink=0.45, pad=0.05)
        cbar_g.set_label("Mid Cloud", fontsize=9)
        cbar_b = fig.colorbar(b, ax=ax, orientation="vertical", shrink=0.45, pad=0.09)
        cbar_b.set_label("Low Cloud", fontsize=9)

        fname = f"dlr_combined_{timestamp}.png"
        plt.savefig(os.path.join(output_dir, fname), dpi=150, bbox_inches="tight")
        plt.close()

    except Exception as e:
        print(f"❌ Failed to plot RGB cloud cover for {timestamp}: {e}")
