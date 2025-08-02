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

# === LOAD MAIN AND CONTOUR DATA ===
ds = load_main_variable(main_var, main_level)
ds_contour = load_main_variable(contour_var, main_level) if contour_var else None

# === COLOR CONFIG ===
config = COLOR_CONFIG[main_var]
cmap = config["cmap"]
bounds = config["bounds"]
label = config["label"]
convert = config["convert"]

# === OUTPUT DIRECTORY ===
out_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/plots/um/{main_var}/{main_level}"
if contour_var:
    out_dir = out_dir.replace(main_var, f"{main_var}_{contour_var}")
os.makedirs(out_dir, exist_ok=True)

# === LOOP THROUGH TIME STEPS ===
for i, timestamp in enumerate(ds.time.values):
    hour = pd.to_datetime(str(timestamp)).hour
    if hour % 6 != 0:
        continue

    print(f"🔄 Plotting {main_var} at {main_level} — time step {i+1}")

    var_name = list(ds.data_vars)[0]
    data = ds[var_name].sel(time=timestamp)

    # Select level if required
    if main_level not in ["surface", "column"]:
        if "model_level_number" in data.dims:
            data = data.sel(model_level_number=level_map[main_level])
        elif "pressure" in data.dims:
            data = data.sel(pressure=int(main_level.replace("mb", "")))
        else:
            raise ValueError(f"Unexpected vertical coordinate in data: {data.dims}")
    data = data.squeeze()

    # === PLOT BASE VARIABLE ===
    fig, ax, proj = setup_map()
    lon, lat = get_lon_lat(data)
    lon2d, lat2d = np.meshgrid(lon, lat)
    mesh = ax.pcolormesh(
        lon2d, lat2d, data,
        cmap=cmap, shading="auto", transform=proj,
        vmin=bounds[0], vmax=bounds[-1]
    )

    # === PLOT CONTOUR OVERLAY ===
    if contour_var:
        contour_name = list(ds_contour.data_vars)[0]
        contour_data = ds_contour[contour_name].sel(time=timestamp)

        if main_level not in ["surface", "column"]:
            if "model_level_number" in contour_data.dims:
                contour_data = contour_data.sel(model_level_number=level_map[main_level])
            elif "pressure" in contour_data.dims:
                contour_data = contour_data.sel(pressure=int(main_level.replace("mb", "")))
        contour_data = contour_data.squeeze()

        lon_c, lat_c = get_lon_lat(contour_data)
        lon2d_c, lat2d_c = np.meshgrid(lon_c, lat_c)
        contour_values = contour_data.values
        style = CONTOUR_CONFIG.get((main_var, contour_var), {})
        levels = np.linspace(np.nanmin(contour_values), np.nanmax(contour_values), 60)

        cs = ax.contour(lon2d_c, lat2d_c, contour_values, levels=levels, transform=proj, **style)
        ax.clabel(cs, inline=1, fontsize=8, fmt="%d")

    # === PLOT WIND QUIVERS ===
    if quiver:
        u_ds = load_main_variable("UGRD", main_level)
        v_ds = load_main_variable("VGRD", main_level)
        u = u_ds[list(u_ds.data_vars)[0]].sel(time=timestamp)
        v = v_ds[list(v_ds.data_vars)[0]].sel(time=timestamp)

        if main_level not in ["surface", "column"]:
            if "model_level_number" in u.dims:
                u = u.sel(model_level_number=level_map[main_level])
                v = v.sel(model_level_number=level_map[main_level])
            elif "pressure" in u.dims:
                pval = int(main_level.replace("mb", ""))
                u = u.sel(pressure=pval)
                v = v.sel(pressure=pval)
                u = u.squeeze()
        v = v.squeeze()
        lon, lat = get_lon_lat(u)
        plot_quivers(ax, u.values, v.values, lat, lon, proj)


    # === FINALIZE PLOT ===
    title = format_title(main_var, main_level, timestamp, contour_var)
    plt.title(title, fontsize=16)
    cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", pad=0.02, aspect=30)
    cbar.set_label(label)

    dt = pd.to_datetime(str(timestamp))
    timestamp_str = dt.strftime("%Y%m%d") + f"_t{dt.strftime('%H')}z"

    suffix = f"{main_var}_{contour_var}_{main_level}_{timestamp_str}.png" if contour_var else f"{main_var}_{main_level}_{timestamp_str}.png"
    plt.savefig(os.path.join(out_dir, suffix), dpi=150, bbox_inches="tight")
    plt.close()
