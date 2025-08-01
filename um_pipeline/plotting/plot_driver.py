import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
from um_pipeline.plotting.utils import (
    setup_map, format_title, plot_quivers, load_main_variable, level_map, get_lon_lat
)
from um_pipeline.plotting.color_config import COLOR_CONFIG, CONTOUR_CONFIG

# === CONFIGURATION ===
main_var = os.getenv("MAIN_VAR", "RH")
main_level = os.getenv("MAIN_LEVEL", "700mb")
contour_var = os.getenv("CONTOUR_VAR", None)
if contour_var in ["None", ""]:
    contour_var = None
quiver = os.getenv("QUIVER", "False") == "True"

# === Load Data ===
ds = load_main_variable(main_var, main_level)
ds_contour = load_main_variable(contour_var, main_level) if contour_var else None

# === Plotting Setup ===
config = COLOR_CONFIG[main_var]
cmap = config["cmap"]
bounds = config["bounds"]
label = config["label"]
convert = config["convert"]

out_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/plots/um/{main_var}/{main_level}"
if contour_var:
    out_dir = out_dir.replace(main_var, f"{main_var}_{contour_var}")
os.makedirs(out_dir, exist_ok=True)

# === Loop through time steps ===
for i, timestamp in enumerate(ds.time.values):
    hour = pd.to_datetime(str(timestamp)).hour
    if hour % 6 != 0:
        continue  # Skip non-6-hour timestamps

    print(f"🔄 Plotting {main_var} at {main_level} — time step {i+1}")

    actual_var = list(ds.data_vars)[0]
    data = ds[actual_var].sel(time=timestamp)
    if "model_level_number" in data.dims:
        data = data.sel(model_level_number=level_map[main_level]).squeeze()
    elif "pressure" in data.dims:
        data = data.sel(pressure=int(main_level.replace("mb", ""))).squeeze()
    else:
        raise ValueError(f"Unexpected vertical coordinate in data: {data.dims}")


    fig, ax, proj = setup_map()
    lon, lat = get_lon_lat(data)
    lon, lat = np.meshgrid(lon, lat)
    mesh = ax.pcolormesh(
        lon, lat, data,
        cmap=cmap,
        shading="auto",
        transform=proj,
        vmin=bounds[0],
        vmax=bounds[-1]
    )

    if contour_var:
        contour_actual = list(ds_contour.data_vars)[0]
        contour_data = ds_contour[contour_actual].sel(time=timestamp)

# ➤ If UM data
        if "model_level_number" in contour_data.dims:
            contour_data = contour_data.sel(model_level_number=level_map[main_level])
            contour_data = contour_data.squeeze()

# ➤ If pressure-level data
        elif "pressure" in contour_data.dims:
            contour_data = contour_data.sel(pressure=int(main_level.replace("mb", "")))

        lon, lat = get_lon_lat(contour_data)
        lon2d, lat2d = np.meshgrid(lon, lat)

        contour_data = contour_data.values
        style = CONTOUR_CONFIG.get((main_var, contour_var), {})
        vmin = np.nanmin(contour_data)
        vmax = np.nanmax(contour_data)
        contour_levels = np.linspace(vmin, vmax, 40)

# ➤ Now plot
        cs = ax.contour(lon2d, lat2d, contour_data, levels=contour_levels, transform=proj, **style)
        ax.clabel(cs, inline=1, fontsize=8, fmt="%d")

    if quiver:
        u_ds = load_main_variable("UGRD", main_level)
        v_ds = load_main_variable("VGRD", main_level)
        u = u_ds[list(u_ds.data_vars)[0]].sel(time=timestamp)
        v = v_ds[list(v_ds.data_vars)[0]].sel(time=timestamp)

    # ✅ Select the model level before converting to .values
        if "model_level_number" in u.dims:
            u = u.sel(model_level_number=level_map[main_level]).squeeze()
            v = v.sel(model_level_number=level_map[main_level]).squeeze()
        elif "pressure" in u.dims:
            u = u.sel(pressure=int(main_level.replace("mb", ""))).squeeze()
            v = v.sel(pressure=int(main_level.replace("mb", ""))).squeeze()

        lon, lat = get_lon_lat(u)
        plot_quivers(ax, u.values, v.values, lat, lon, proj)

    title = format_title(main_var, main_level, timestamp, contour_var)
    plt.title(title, fontsize=16)
    cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", pad=0.02, aspect=30)
    cbar.set_label(label)
    timestamp_str = pd.to_datetime(str(timestamp)).strftime("%Y%m%d_%H%M")
    if contour_var:
        fname = f"{main_var}_{contour_var}_{main_level}_{timestamp_str}.png"
    else:
        fname = f"{main_var}_{main_level}_{timestamp_str}.png"

    plt.savefig(os.path.join(out_dir, fname), dpi=150, bbox_inches="tight")
    plt.close()
