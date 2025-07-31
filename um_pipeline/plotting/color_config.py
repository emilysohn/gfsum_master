
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
        "label": "Temperature (K)",
        "convert": lambda x: x
    },
    "POT": {
        "cmap": ListedColormap([
            "#ECEAE6", "#FF00F3", "#DA09FF", "#8308FF", "#3700FF",
            "#005D71", "#00FFF5", "#00FFFC", "#04DF53", "#00FD42",
            "#80FF00", "#51FF00", "#FF6F9A", "#EE8891", "#ED345F", "#FF374E"
        ]),
        "bounds": np.linspace(273, 341, 17),
        "label": "Potential Temperature (K)",
        "convert": lambda x: x
    },
    "RH": {
        "cmap": ListedColormap(["#36de76", "#19949d", "#3b66f1", "#0a35c4", "#130963"]),
        "bounds": [70, 85, 100, 115, 130],
        "label": "Relative Humidity (%)",
        "convert": lambda x: x * 100 if x.max() < 1.5 else x
    },
    "SPFH": {
        "cmap": "YlGnBu",
        "bounds": np.linspace(0, 0.01, 11),
        "label": "Specific Humidity (kg/kg)",
        "convert": lambda x: x
    },
    "LWC": {
        "cmap": "Blues",
        "bounds": np.linspace(0, 0.5, 11),
        "label": "Liquid Water Content (g/m³)",
        "convert": lambda x: x * 1000
    },
    "HGT": {
        "cmap": ListedColormap(plt.get_cmap("cividis")(np.linspace(0, 1, 256))),
        "bounds": np.linspace(0, 6000, 13),
        "label": "Geopotential Height (m)",
        "convert": lambda x: x
    },
    "TCDC": {
        "cmap": "Blues",
        "bounds": np.linspace(0, 1),
        "label": "Total Cloud Cover (0–1)",
        "convert": lambda x: x
    },
    "HPBL": {
        "cmap": "viridis",
        "bounds": np.linspace(0, 2250, 10),
        "label": "Planetary Boundary Layer Height (m)",
        "convert": lambda x: x
    },
    "UGRD": {
        "cmap": "plasma_r",
        "bounds": np.arange(10, 90, 5),
        "label": "Horizontal Wind Speed (m/s)",
        "convert": lambda x: x
    }
}

CONTOUR_CONFIG = {
    ("TMP", "HGT"): {"colors": "tan", "linewidths": 1.0, "linestyles": "solid"},
    ("POT", "HGT"): {"colors": "white", "linewidths": 1.0, "linestyles": "solid"},
    ("RH", "HGT"):  {"colors": "black", "linewidths": 1.0, "linestyles": "solid"},
    ("WIND", "HGT"): {"colors": "black", "linewidths": 1.0, "linestyles": "dashed"},
}
