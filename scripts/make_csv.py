import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os

# === CONFIGURATION ===
output_path = "/ocean/projects/atm200005p/esohn1/gfsum_master/data/csv/interpolated_path_800.csv"  # 🔁 <-- Change this to your desired path

# === Original flight path points: lat, lon, pressure_hPa ===
points = [
    (-43.5, 172.5, 1000),
    (-53.7, 163.1, 300),
    (-54.3, 163.4, 300),
    (-55.7, 161.7, 1000),
    (-53.4, 165.7, 1000),
    (-57.4, 172.5, 900),
    (-54.6, 179.8, 300),
    (-54.9, 178.5, 900),
    (-49.7, 177.0, 150),
    (-44.3, 173.1, 1000),
]

# === Convert to DataFrame ===
df = pd.DataFrame(points, columns=["lat", "lon", "pressure_hPa"])

# === Distance-based interpolation support ===
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

dist = [0]
for i in range(1, len(df)):
    d = haversine(df.lat[i-1], df.lon[i-1], df.lat[i], df.lon[i])
    dist.append(dist[-1] + d)
dist = np.array(dist)

# === Interpolation ===
n_points = 800
interp_dist = np.linspace(0, dist[-1], n_points)

lat_interp = interp1d(dist, df["lat"])(interp_dist)
lon_interp = interp1d(dist, df["lon"])(interp_dist)
p_interp   = interp1d(dist, df["pressure_hPa"])(interp_dist)

interp_df = pd.DataFrame({
    "lat": lat_interp,
    "lon": lon_interp,
    "pressure_hPa": p_interp,
})

# === Save to CSV ===
os.makedirs(os.path.dirname(output_path), exist_ok=True)
interp_df.to_csv(output_path, index=False)
print(f"✅ Saved interpolated path with {n_points} points to: {output_path}")
