# gfs_forecasted_pipeline/plotting/special/cdc_pres.py

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from gfs_forecasted_pipeline.plotting.utils import setup_map, create_output_dir

# === CONFIGURATION ===
data_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_forecasted/processed_netcdf"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/gfs_forecasted/cdc_pres"
create_output_dir(output_dir)

forecast_hour = 48  # hardcoded for now
start_time = datetime(2025, 7, 14, 0)
end_time = datetime(2025, 7, 19, 18)
time_step = timedelta(hours=6)

cloud_types = {
    "LCDC": {
        "filename": "LCDC.nc",
        "var": "LCDC_lowcloudlayer",
        "label": "Low Cloud Cover (0–1)",
        "cmap": "Blues"
    },
    "MCDC": {
        "filename": "MCDC.nc",
        "var": "MCDC_midcloudlayer",
        "label": "Mid Cloud Cover (0–1)",
        "cmap": "Greens"
    },
    "HCDC": {
        "filename": "HCDC.nc",
        "var": "HCDC_highcloudlayer",
        "label": "High Cloud Cover (0–1)",
        "cmap": "Reds"
    }
}

for cloud_key, config in cloud_types.items():
    for init_time in [start_time + i*time_step for i in range(int((end_time - start_time) / time_step) + 1)]:
        timestamp = init_time.strftime("%Y%m%d_t%Hz")
        valid_time = init_time + timedelta(hours=forecast_hour)

        cloud_path = os.path.join(data_dir, timestamp, config["filename"])
        pres_path = os.path.join(data_dir, timestamp, "PRES.nc")

        if not (os.path.exists(cloud_path) and os.path.exists(pres_path)):
            print(f"⚠️ Missing files for {timestamp}, skipping {cloud_key}")
            continue

        try:
            cloud = xr.open_dataset(cloud_path)[config["var"]].squeeze()
            pres = xr.open_dataset(pres_path)["PRES_surface"].squeeze() / 100  # Pa → hPa

            lon = cloud["longitude"]
            lat = cloud["latitude"]
            lon2d, lat2d = np.meshgrid(lon, lat)

            fig, ax = setup_map()

            # Plot cloud cover
            pcm = ax.pcolormesh(lon2d, lat2d, cloud,
                                cmap=config["cmap"], vmin=0, vmax=1,
                                transform=ax.projection)

            # Colorbar
            cbar = fig.colorbar(pcm, ax=ax, orientation="vertical", shrink=0.6, pad=0.02)
            cbar.set_label(config["label"])

            # Contours for sea-level pressure
            ax.contour(pres["longitude"], pres["latitude"], pres,
                       levels=np.arange(960, 1040, 4),
                       colors="tan", linewidths=0.8, transform=ax.projection)

            # Title with valid and init time
            ax.set_title(
                f"{config['label']} with Sea-Level Pressure (hPa)\n"
                f"Valid: {valid_time:%Y-%m-%d %H:%MZ} (initialisation: {init_time:%Y-%m-%d %H:%MZ})"
            )

            # Save
            fname = f"{cloud_key.lower()}_pres_{timestamp}.png"
            plt.savefig(os.path.join(output_dir, fname), dpi=150, bbox_inches="tight")
            plt.close()

        except Exception as e:
            print(f"❌ Failed to plot {cloud_key} for {timestamp}: {e}")
