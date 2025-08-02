# gfs_forecasted_pipeline/plotting/plot_driver.py

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd

from gfs_forecasted_pipeline.plotting.utils import (
    setup_map, format_title, plot_quivers, load_main_variable, get_lon_lat
)
from gfs_forecasted_pipeline.plotting.color_config import COLOR_CONFIG, CONTOUR_CONFIG

# === CONFIGURATION ===
main_var = os.getenv("MAIN_VAR", "RH")
main_level = os.getenv("MAIN_LEVEL", "700mb")
contour_var = os.getenv("CONTOUR_VAR", None)
if contour_var in ["None", ""]:
    contour_var = None
quiver = os.getenv("QUIVER", "False") == "True"
forecast_hour = 48
base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_forecasted/processed_netcdf"

# === Load plotting config ===
config = COLOR_CONFIG[main_var]
cmap = config["cmap"]
bounds = config["bounds"]
label = config["label"]

# === Loop through timestamps ===
timestamp_dirs = sorted(os.listdir(base_dir))
if not timestamp_dirs:
    raise FileNotFoundError(f"No timestamp directories found in {base_dir}")

for timestamp_str in timestamp_dirs:
    print(f"\n🔄 Plotting {main_var} at {main_level} — {timestamp_str}")
    timestamp_path = os.path.join(base_dir, timestamp_str)

    # Load main variable
    ds = load_main_variable(main_var, main_level, timestamp_str)
    var_name = f"{main_var}_{main_level}" if f"{main_var}_{main_level}" in ds else main_var
    data = ds[var_name].squeeze()

    # Plot setup
    fig, ax, proj = setup_map()
    lon, lat = get_lon_lat(data)
    lon2d, lat2d = np.meshgrid(lon, lat)

    mesh = ax.pcolormesh(
        lon2d, lat2d, data,
        cmap=cmap,
        shading="auto",
        transform=proj,
        vmin=bounds[0],
        vmax=bounds[-1]
    )

    # === Contour overlay ===
    if contour_var:
        ds_contour = load_main_variable(contour_var, main_level, timestamp_str)
        contour_var_name = f"{contour_var}_{main_level}" if f"{contour_var}_{main_level}" in ds_contour else contour_var

        if contour_var_name not in ds_contour:
            print(f"⚠️ {contour_var_name} not found in dataset for {timestamp_str}. Skipping contour overlay.")
        else:
            contour_data = ds_contour[contour_var_name].squeeze()
            style = CONTOUR_CONFIG.get((main_var, contour_var), {})

            lon_c, lat_c = get_lon_lat(contour_data)
            lon2d_c, lat2d_c = np.meshgrid(lon_c, lat_c)

            contour_data = contour_data.values
            vmin = np.nanmin(contour_data)
            vmax = np.nanmax(contour_data)
            contour_levels = np.linspace(vmin, vmax, 60)
            cs = ax.contour(lon2d_c, lat2d_c, contour_data, levels=contour_levels, transform=proj, **style)
            ax.clabel(cs, inline=1, fontsize=8, fmt="%d")

    # === Quiver overlay ===
    if quiver:
        u_ds = load_main_variable("UGRD", main_level, timestamp_str)
        v_ds = load_main_variable("VGRD", main_level, timestamp_str)
        
        u_var = list(u_ds.data_vars)[0]
        u = u_ds[u_var].squeeze()
        v_var = list(v_ds.data_vars)[0]
        v = v_ds[v_var].squeeze()
        lon_q, lat_q = get_lon_lat(u)
        plot_quivers(ax, u.values, v.values, lat_q, lon_q, proj)

    # === Title + Colorbar ===
    date_str = timestamp_str.split("_t")[0]
    hour_str = timestamp_str.split("_t")[1].replace("z", "")
    init_time_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}T{hour_str}:00"
    init_time = pd.to_datetime(init_time_str)
    valid_time = np.datetime64(init_time + pd.Timedelta(hours=forecast_hour))

    title = format_title(main_var, main_level, valid_time, contour_var, np.datetime64(init_time))
    plt.title(title, fontsize=10)
    cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", pad=0.02, aspect=30)
    cbar.set_label(label)

    # === Save figure ===
    out_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/plots/gfs_forecasted/{main_var}/{main_level}"
    if contour_var:
        out_dir = out_dir.replace(main_var, f"{main_var}_{contour_var}")
    os.makedirs(out_dir, exist_ok=True)

    fname = f"{main_var}_{main_level}_{timestamp_str}.png" if not contour_var else f"{main_var}_{contour_var}_{main_level}_{timestamp_str}.png"
    print(f"💾 Saving to {os.path.join(out_dir, fname)}")
    plt.savefig(os.path.join(out_dir, fname), dpi=150, bbox_inches="tight")
    plt.close()
