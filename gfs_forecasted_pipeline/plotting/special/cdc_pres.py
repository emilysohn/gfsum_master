# gfs_forecasted_pipeline/plotting/special/cdc_pres.py

import os
import numpy as np
import xarray as xr
import traceback
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from gfs_forecasted_pipeline.plotting.utils import setup_map, create_output_dir

# === CONFIGURATION ===
data_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_forecasted/processed_netcdf"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/plots/gfs_forecasted/cdc_pres"
create_output_dir(output_dir)

forecast_hour = 48
start_time = datetime(2025, 7, 14, 0)
end_time = datetime(2025, 7, 19, 18)
time_step = timedelta(hours=6)

cloud_types = {
    "LCDC": {
        "filename": "LCDC.nc",
        "var": "LCDC_lowcloudlayer",
        "label": "Low Cloud Cover (0–1)",
        "cmap": "Blues",
        "subfolder": "low"
    },
    "MCDC": {
        "filename": "MCDC.nc",
        "var": "MCDC_middlecloudlayer",
        "label": "Mid Cloud Cover (0–1)",
        "cmap": "Greens",
        "subfolder": "mid"
    },
    "HCDC": {
        "filename": "HCDC.nc",
        "var": "HCDC_highcloudlayer",
        "label": "High Cloud Cover (0–1)",
        "cmap": "Reds",
        "subfolder": "high"
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
            # Load data
            cloud_ds = xr.open_dataset(cloud_path)
            pres_ds = xr.open_dataset(pres_path)

            cloud = cloud_ds[config["var"]].squeeze() / 100
            pres = pres_ds["PRES_surface"].squeeze() / 100  # Pa → hPa

            # Extract coordinates safely
            lon = cloud["longitude"].values
            lat = cloud["latitude"].values
            lon2d, lat2d = np.meshgrid(lon, lat)

            pres_lon = pres["longitude"].values
            pres_lat = pres["latitude"].values
            pres2d_lon, pres2d_lat = np.meshgrid(pres_lon, pres_lat)

            # Setup plot
            fig, ax, proj = setup_map()
            fig.set_size_inches(12, 8)


            # Plot cloud cover
            pcm = ax.pcolormesh(
                lon2d, lat2d, cloud,
                cmap=config["cmap"], vmin=0, vmax=1,
                transform=proj
            )

            # Add a clean manual colorbar (right side)
            cbar_ax = fig.add_axes([0.92, 0.25, 0.015, 0.5])  # [left, bottom, width, height]
            cbar = fig.colorbar(pcm, cax=cbar_ax)
            cbar.set_label(config["label"])


            # Plot pressure contours
            ax.contour(
                pres2d_lon, pres2d_lat, pres,
                levels=np.arange(960, 1040, 4),
                colors="tan", linewidths=0.8,
                transform=proj
            )

            # Title
            ax.set_title(
                f"{config['label']} with Sea-Level Pressure (hPa)\n"
                f"Valid: {valid_time:%Y-%m-%d %H:%MZ} (initialisation: {init_time:%Y-%m-%d %H:%MZ})"
            )

        # Save
            subfolder = config["subfolder"]
            out_path = os.path.join(output_dir, subfolder)
            os.makedirs(out_path, exist_ok=True)

            fname = f"{cloud_key.lower()}_pres_{timestamp}.png"
            plt.savefig(os.path.join(out_path, fname), dpi=150, bbox_inches="tight")

            plt.close()

        except Exception as e:
            print(f"❌ Failed to plot {cloud_key} for {timestamp}: {e}")
            traceback.print_exc()
