# gfs_pipeline/plotting/color_config.py

import numpy as np
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt

COLOR_CONFIG = {
    "TMP": {
        "cmap": ListedColormap([
            "#660ace", "#1c0fcd", "#008cff", "#0c9c9c", "#1fb97b",
            "#0eb331", "#80ff00", "#fff12d", "#ff9900", "#ff2a00", "#b30000"
        ]),
        "bounds": np.linspace(200, 350, 12),
        "label": "Temperature (K)"
    },
    "POT": {
        "cmap": ListedColormap([
            "#D0156F", "#FF00F3", "#DA09FF", "#8308FF", "#3700FF",
            "#2260D3", "#00FFF5", "#00FFFC", "#04DF53", "#00FD42",
            "#80FF00", "#BEFF6E", "#FFF873", "#EE8891", "#ED345F", "#FF374E"
        ]),
        "bounds": np.linspace(273, 341, 17),
        "label": "Potential Temperature (K)"
    },
    "RH": {
        "cmap": ListedColormap(["#36de76", "#19949d", "#3b66f1", "#0a35c4", "#130963"]),
        "bounds": [50, 65, 80, 95, 110],
        "label": "Relative Humidity (%)"
    },
    "SPFH": {
        "cmap": "YlGnBu",
        "bounds": np.linspace(0, 0.01, 11),
        "label": "Specific Humidity (kg/kg)"
    },
    "LWC": {
        "cmap": "Blues",
        "bounds": np.linspace(0, 0.5, 11),
        "label": "Liquid Water Content (g/m³)"
    },
    "HGT": {
        "cmap": ListedColormap(plt.get_cmap("cividis")(np.linspace(0, 1, 256))),
        "bounds": np.linspace(0, 6000, 13),
        "label": "Geopotential Height (m)"
    },
    "TCDC": {
        "cmap": "Blues",
        "bounds": np.linspace(0, 1),
        "label": "Total Cloud Cover (0–1)"
    },
    "HPBL": {
        "cmap": "viridis",
        "bounds": np.linspace(0, 2250, 10),
        "label": "Planetary Boundary Layer Height (m)"
    },
    "UGRD": {
        "cmap": "plasma_r",
        "bounds": np.arange(10, 90, 5),
        "label": "Horizontal Wind Speed (m/s)"
    }
}

CONTOUR_CONFIG = {
    ("TMP", "HGT"): {"colors": "tan", "linewidths": 1.0, "linestyles": "solid"},
    ("POT", "HGT"): {"colors": "white", "linewidths": 1.0, "linestyles": "solid"},
    ("RH", "HGT"):  {"colors": "black", "linewidths": 1.0, "linestyles": "solid"},
    ("WIND", "HGT"): {"colors": "black", "linewidths": 1.0, "linestyles": "dashed"},
}
