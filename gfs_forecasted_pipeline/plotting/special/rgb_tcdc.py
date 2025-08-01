# gfs_forecasted_pipeline/plotting/special/rgb_tcdc.py

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from gfs_forecasted_pipeline.plotting.utils import setup_map, create_output_dir

# === CONFIGURATION ===
data_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_forecasted/processed_netcdf"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/gfs_forecasted/rgb_tcdc"
create_output_dir(output_dir)

forecast_hour = 48
start_time = datetime(2025, 7, 14, 0)
end_time = datetime(2025, 7, 19, 18)
time_step = timedelta(hours=6)

for init_time in [start_time + i*time_step for i in range(int((end_time - start_time) / time_step) + 1)]:
    timestamp = init_time.strftime("%Y%m%d_t%Hz")
    valid_time = init_time + timedelta(hours=forecast_hour)

    lcdc_path = os.path.join(data_dir, timestamp, "LCDC.nc")
    mcdc_path = os.path.join(data_dir, timestamp, "MCDC.nc")
    hcdc_path = os.path.join(data_dir, timestamp, "HCDC.nc")
    pres_path = os.path.join(data_dir, timestamp, "PRES.nc")

    if not all(os.path.exists(p) for p in [lcdc_path, mcdc_path, hcdc_path, pres_path]):
        print(f"⚠️ Missing one or more files for {timestamp}, skipping.")
        continue

    try:
        lcdc = xr.open_dataset(lcdc_path)["LCDC_lowcloudlayer"].squeeze()
        mcdc = xr.open_dataset(mcdc_path)["MCDC_midcloudlayer"].squeeze()
        hcdc = xr.open_dataset(hcdc_path)["HCDC_highcloudlayer"].squeeze()
        pres = xr.open_dataset(pres_path)["PRES_surface"].squeeze() / 100  # Pa → hPa

        lon = lcdc["longitude"]
        lat = lcdc["latitude"]
        lon2d, lat2d = np.meshgrid(lon, lat)

        fig, ax = setup_map()

        # Cloud layer shading
        r = ax.pcolormesh(lon2d, lat2d, hcdc, cmap="Reds", vmin=0, vmax=1, alpha=0.4, transform=ax.projection)
        g = ax.pcolormesh(lon2d, lat2d, mcdc, cmap="Greens", vmin=0, vmax=1, alpha=0.4, transform=ax.projection)
        b = ax.pcolormesh(lon2d, lat2d, lcdc, cmap="Blues", vmin=0, vmax=1, alpha=0.4, transform=ax.projection)

        # Sea-level pressure contours
        ax.contour(pres["longitude"], pres["latitude"], pres,
                   levels=np.arange(960, 1040, 4),
                   colors="tan", linewidths=0.7, transform=ax.projection)

        # Title with valid/init time
        ax.set_title(
            f"DLR-Style Layered Cloud Cover and MSLP\n"
            f"Valid: {valid_time:%Y-%m-%d %H:%MZ} (initialisation: {init_time:%Y-%m-%d %H:%MZ})",
            fontsize=13
        )

        # Add colorbars for each channel
        cbar_r = fig.colorbar(r, ax=ax, orientation="vertical", shrink=0.45, pad=0.01)
        cbar_r.set_label("High Cloud", fontsize=9)
        cbar_g = fig.colorbar(g, ax=ax, orientation="vertical", shrink=0.45, pad=0.05)
        cbar_g.set_label("Mid Cloud", fontsize=9)
        cbar_b = fig.colorbar(b, ax=ax, orientation="vertical", shrink=0.45, pad=0.09)
        cbar_b.set_label("Low Cloud", fontsize=9)

        # Save
        fname = f"dlr_combined_{timestamp}.png"
        plt.savefig(os.path.join(output_dir, fname), dpi=150, bbox_inches="tight")
        plt.close()

    except Exception as e:
        print(f"❌ Failed to plot RGB cloud cover for {timestamp}: {e}")
