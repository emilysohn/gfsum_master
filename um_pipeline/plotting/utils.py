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

# === Wind quivers ===
def plot_quivers(ax, u, v, lat, lon, proj, stride=5):
    # Ensure same shape for u and v
    min_lat = min(u.shape[0], v.shape[0])
    min_lon = min(u.shape[1], v.shape[1])
    u = u[:min_lat, :min_lon]
    v = v[:min_lat, :min_lon]
    lat = lat[:min_lat]
    lon = lon[:min_lon]
    lon2d, lat2d = np.meshgrid(lon, lat)
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
    if potential_temperature.shape != pressure_hPa.shape:
        pressure_hPa = xr.broadcast(potential_temperature, pressure_hPa)[1]

    temperature = potential_temperature * (pressure_hPa / 1000.0) ** kappa
    return temperature

def calculate_lwc_column(clmr, pressure, height):
    R = 287.05  # specific gas constant for dry air, J/kg/K
    temperature = calculate_temperature(clmr, pressure)  # shape match assumed
    density = pressure / (R * temperature)  # [kg/m³]

    delta_z = np.gradient(height, axis=1)  # assumes height dims: (time, level)
    lwc = (density * clmr * delta_z).sum(dim="model_level_number")  # [kg/m²]
    lwc = lwc * 1000  # convert to g/m²
    return lwc

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

    elif var == "LWC":
        clmr_ds = xr.open_dataset(os.path.join(base_dir, file_map["LWC"]))
        clmr = clmr_ds["mass_fraction_of_cloud_liquid_water_in_air"]
    
        pres = xr.open_dataset(os.path.join(base_dir, file_map["PRES"]))["air_pressure"]
    
    # Get level height from the CLMR dataset — not from its own file
        height = clmr_ds["level_height"]  # this should be 1D: (model_level_number)
    
        lwc = calculate_lwc_column(clmr, pres, height)
        lwc.attrs = clmr.attrs
        return lwc.to_dataset(name="LWC")


    else:
        fpath = os.path.join(base_dir, file_map[var])
        ds = xr.open_dataset(fpath, decode_timedelta=True)
        var_name = var_name_map.get(var, var)

        if var_name not in ds.data_vars:
            raise KeyError(f"Expected variable '{var_name}' not found in {fpath}. Available: {list(ds.data_vars)}")

        return ds[[var_name]].rename({var_name: var})
