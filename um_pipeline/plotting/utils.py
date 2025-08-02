import os
import numpy as np
import xarray as xr
import pandas as pd

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from um_pipeline.plotting.color_config import CONTOUR_CONFIG, COLOR_CONFIG
import matplotlib.ticker as mticker

def create_output_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# === Map setup ===
def setup_map():
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={"projection": proj})
    ax.set_extent([145, 180, -65, -30], crs=proj)
    ax.set_aspect("auto")
    ax.coastlines(resolution="50m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    gl=ax.gridlines(draw_labels=True, linewidth=0.3, color="gray", alpha=0.5,linestyle="--")
    gl.top_labels = False
    gl.right_labels = False

    gl.xlocator = mticker.FixedLocator(np.linspace(145, 180, 8))
    gl.ylocator = mticker.FixedLocator(np.linspace(-65, -30, 8))
    return fig, ax, proj

# === Title formatting ===
def format_title(var, level, timestamp, contour_var=None):
    valid_time = pd.to_datetime(str(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
    label = COLOR_CONFIG[var]["label"]
    if contour_var:
        clabel = COLOR_CONFIG[contour_var]["label"]
        return f"{label} and {clabel} at {level}\nValid: {valid_time}"
    return f"{label} at {level}\nValid: {valid_time}"

def plot_quivers(ax, u, v, lat, lon, proj, stride=4):
    """
    Plot wind quivers, making sure that the dimensions of u, v, lat, lon align.
    """
    # Convert lat/lon to 2D grid if needed
    lon2d, lat2d = np.meshgrid(lon, lat)

    # Trim all arrays to the same shape
    min_y = min(u.shape[0], v.shape[0], lat2d.shape[0])
    min_x = min(u.shape[1], v.shape[1], lon2d.shape[1])
    u = u[:min_y, :min_x]
    v = v[:min_y, :min_x]
    lon2d = lon2d[:min_y, :min_x]
    lat2d = lat2d[:min_y, :min_x]

    # Optional debug
    # print(f"[DEBUG] u shape: {u.shape}, v shape: {v.shape}, lon2d shape: {lon2d.shape}")

    ax.quiver(
        lon2d[::stride, ::stride], lat2d[::stride, ::stride],
        u[::stride, ::stride], v[::stride, ::stride],
        transform=proj,
        color="black",
        scale=500
    )


# === File mapping ===
file_map = {
    "RH": "glm_relative_humidity_m01s16i256.nc",
    "HGT": "glm_geopotential_height_m01s16i202.nc",
    "UGRD": "glm_x_wind_m01s00i002.nc",
    "VGRD": "glm_y_wind_m01s00i003.nc",
    "POT": "glm_air_potential_temperature_m01s00i004.nc",
    "PRES": "glm_air_pressure_m01s00i408.nc",
    "LWC": "glm_mass_fraction_of_cloud_liquid_water_in_air_m01s00i254.nc",
    "HPBL": "glm_m01s03i073_m01s03i073.nc",
    "SPFH": "glm_specific_humidity_m01s00i010.nc",
    "VVEL": "glm_upward_air_velocity_m01s00i150.nc",
    "TCDC": "glm_cloud_volume_fraction_in_atmosphere_layer_m01s00i266.nc",
    "APCP": "glm_precipitation_amount_m01s05i226.nc"
}

level_map = {
    "1000mb": 1,
    "925mb": 6,
    "850mb": 11,
    "700mb": 18,
    "500mb": 26,
    "300mb": 35,
    "250mb": 37
}

def get_lon_lat(data):
    lat = data.coords["lat"] if "lat" in data.coords else data.coords["latitude"]
    lon = data.coords["lon"] if "lon" in data.coords else data.coords["longitude"]
    return lon, lat

def calculate_temperature(potential_temperature, pressure):

    kappa = 0.286  # Rd/Cp
    pressure_hPa = pressure / 100  # convert Pa to hPa
    pressure_hPa = xr.broadcast(potential_temperature, pressure_hPa)[1]
    temperature = potential_temperature * (pressure_hPa / 1000.0) ** kappa
    return temperature

def calculate_lwc_column(clmr, pot_temp, pressure, height):
    R = 287.05  # J/(kg·K)
    temperature = calculate_temperature(pot_temp, pressure)
    density = pressure / (R * temperature)  # kg/m³

    if height.ndim == 1:
        delta_z = np.gradient(height)  # m
        delta_z = xr.DataArray(delta_z, dims=["model_level_number"])
    elif height.ndim == 2:
        delta_z = np.gradient(height, axis=1)
        delta_z = xr.DataArray(delta_z, dims=["time", "model_level_number"])
    else:
        raise ValueError("Unexpected height dimension")

    # Column-integrated LWC (kg/m²)
    lwc = (clmr * density * delta_z).sum(dim="model_level_number")
    return lwc  # Keep in kg/m²


var_name_map = {
    "RH": "relative_humidity",
    "SPFH": "specific_humidity",
    "TMP": "air_temperature",  # only used for consistency — TMP is computed from POT + PRES
    "POT": "air_potential_temperature",
    "UGRD": "x_wind",
    "VGRD": "y_wind",
    "VVEL": "upward_air_velocity",
    "PRES": "air_pressure",
    "HGT": "geopotential_height",
    "LWC": "mass_fraction_of_cloud_liquid_water_in_air",  # used in LWC column calc
    "TCDC": "cloud_volume_fraction_in_atmosphere_layer",
    "APCP": "precipitation_amount",
    "HPBL": "m01s03i073"
}

base_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/um/u-dq502/0716"

def load_main_variable(var, level):
    if var == "TMP":
        pot = xr.open_dataset(os.path.join(base_dir, file_map["POT"]))["air_potential_temperature"]
        pres = xr.open_dataset(os.path.join(base_dir, file_map["PRES"]))["air_pressure"]
        tmp = calculate_temperature(pot, pres)
        tmp.attrs = pot.attrs
        return tmp.to_dataset(name="TMP")

    # === Special case: Column-integrated LWC
    elif var == "LWC" and level == "column":
        clmr_ds = xr.open_dataset(os.path.join(base_dir, file_map["LWC"]), decode_timedelta=True)
        clmr = clmr_ds["mass_fraction_of_cloud_liquid_water_in_air"]
        pot = xr.open_dataset(os.path.join(base_dir, file_map["POT"]), decode_timedelta=True)["air_potential_temperature"]
        pres = xr.open_dataset(os.path.join(base_dir, file_map["PRES"]), decode_timedelta=True)["air_pressure"]
        height = clmr_ds["level_height"]
        lwc = calculate_lwc_column(clmr, pot, pres, height)
        lwc.attrs["units"] = "kg/m²"
        lwc.attrs["long_name"] = "Column Liquid Water Content"
        return lwc.to_dataset(name="LWC")


    # === Special case: HPBL_surface fallback
    elif var == "HPBL" and level == "surface":
        fpath = os.path.join(base_dir, file_map["HPBL"])
        ds = xr.open_dataset(fpath)
        if "m01s03i073" in ds:
            return ds[["m01s03i073"]]
        else:
            varname = list(ds.data_vars)[0]
            return ds[[varname]].rename({varname: "HPBL"})

    # === Standard case
    else:
        fpath = os.path.join(base_dir, file_map[var])
        ds = xr.open_dataset(fpath, decode_timedelta=True)
        var_name = var_name_map.get(var, var)

        if var_name not in ds.data_vars:
            raise KeyError(f"Expected variable '{var_name}' not found in {fpath}. Available: {list(ds.data_vars)}")

        return ds[[var_name]].rename({var_name: var})

