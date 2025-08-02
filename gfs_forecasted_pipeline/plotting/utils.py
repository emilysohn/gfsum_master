import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import matplotlib.ticker as mticker

from gfs_forecasted_pipeline.plotting.color_config import COLOR_CONFIG

def create_output_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_lon_lat(data):
    lat = data.coords["lat"] if "lat" in data.coords else data.coords["latitude"]
    lon = data.coords["lon"] if "lon" in data.coords else data.coords["longitude"]
    return lon, lat

def setup_map():
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={"projection": proj})
    ax.set_extent([145, 180, -65, -30], crs=proj)
    ax.set_aspect("auto")
    ax.coastlines(resolution="50m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)

    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", alpha=0.5, linestyle="--")
    gl.xlocator = mticker.FixedLocator(np.linspace(145, 180, 8))
    gl.ylocator = mticker.FixedLocator(np.linspace(-65, -30, 8))
    gl.top_labels = False
    gl.right_labels = False

    return fig, ax, proj

def plot_quivers(ax, u, v, lat, lon, proj, stride=10, scale=500):
    try:
        # Ensure same shape for u and v
        min_lat = min(u.shape[0], v.shape[0])
        min_lon = min(u.shape[1], v.shape[1])
        u = u[:min_lat, :min_lon]
        v = v[:min_lat, :min_lon]
        lat = lat[:min_lat]
        lon = lon[:min_lon]

        lon2d, lat2d = np.meshgrid(lon, lat)
        u_vals = u.values if hasattr(u, "values") else u
        v_vals = v.values if hasattr(v, "values") else v

        q = ax.quiver(
            lon2d[::stride, ::stride], lat2d[::stride, ::stride],
            u_vals[::stride, ::stride], v_vals[::stride, ::stride],
            transform=proj,
            color="black", scale=scale,
            width=0.0025, zorder=3
        )
        return q
    except Exception as e:
        print(f"❌ Quiver plot error: {e}")

def format_title(main_var, level, valid_time, contour_var=None, init_time=None):
    if isinstance(valid_time, np.datetime64):
        valid_time = pd.to_datetime(valid_time)
    if isinstance(init_time, np.datetime64):
        init_time = pd.to_datetime(init_time)

    var_label = COLOR_CONFIG.get(main_var, {}).get("label", main_var)
    level_str = f"at {level}" if level else ""

    if contour_var:
        contour_label = COLOR_CONFIG.get(contour_var, {}).get("label", contour_var)
        var_label += f" and {contour_label}"

    valid_str = f"Valid: {valid_time.strftime('%Y-%m-%d %H:%M')}"
    time_str = f"{valid_str} (initialisation: {init_time.strftime('%Y-%m-%d %H:%M')})" if init_time else valid_str

    return f"{var_label} {level_str}\n{time_str}"

def calculate_potential_temperature(temp, pressure):
    p0 = 100000  # reference pressure in Pa (1000 hPa)
    Rd = 287.05  # specific gas constant for dry air [J/kg·K]
    cp = 1004.0  # specific heat at constant pressure for dry air [J/kg·K]
    kappa = Rd / cp
    theta = temp * (p0 / pressure) ** kappa
    return theta

def load_main_variable(var, level, timestamp):
    base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/gfs_forecasted/processed_netcdf"
    if isinstance(timestamp, np.datetime64):
        timestamp_str = str(np.datetime_as_string(timestamp, unit="s")).replace(":", "")
    else:
        timestamp_str = str(timestamp)
    timestamp_dir = os.path.join(base_dir, timestamp_str)

    # Special case: Potential temperature
    if var == "POT":
        tmp_ds = xr.open_dataset(os.path.join(timestamp_dir, "TMP.nc"))
        pressure_pa = int(level.replace("mb", "")) * 100
        tmp_var = f"TMP_{level}"
        if tmp_var not in tmp_ds:
            raise KeyError(f"Missing {tmp_var} in TMP.nc")
        temperature = tmp_ds[tmp_var]
        pot = calculate_potential_temperature(temperature, pressure_pa)
        pot.attrs = temperature.attrs
        return pot.to_dataset(name=f"{var}_{level}")

    file_path = os.path.join(timestamp_dir, f"{var}.nc")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"NetCDF file not found: {file_path}")

    ds = xr.open_dataset(file_path)
    if var == "HPBL" and level == "surface":
        var_name = "HPBL_surface" if "HPBL_surface" in ds else "HPBL"
    else:
        var_name = f"{var}_{level}" if f"{var}_{level}" in ds else var

    if var_name not in ds:
        raise KeyError(f"Variable {var_name} not found in {file_path}")

    data = ds[var_name]

    # === Manual conversions for specific variables ===
    if var == "RH" and data.max() < 1.5:
        data *= 100  # Convert from [0–1] to [%]
    elif var == "LWC":
        data *= 1000  # Convert from kg/m³ to g/m³

    return data.to_dataset(name=var_name)
