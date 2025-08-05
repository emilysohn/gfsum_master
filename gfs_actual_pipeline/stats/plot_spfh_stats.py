# plot_spfh_summary_gfs.py

import os
import pandas as pd
import matplotlib.pyplot as plt

# === Configuration ===
csv_path = "/ocean/projects/atm200005p/esohn1/gfsum_master/stats/gfs_actual/spfh_5day_summary.csv"
output_path = "/ocean/projects/atm200005p/esohn1/gfsum_master/stats/gfs_actual/figures/spfh_5day_summary_plot.png"

# === Load and Plot ===
df = pd.read_csv(csv_path)

levels = df["level"]
mins = df["SPFH_min"]
maxs = df["SPFH_max"]
means = df["SPFH_mean"]

plt.figure(figsize=(8, 5))
plt.bar(levels, maxs, label="Max SPFH", color="skyblue")
plt.bar(levels, mins, label="Min SPFH", color="lightcoral")
plt.plot(levels, means, label="Mean SPFH", color="black", marker="o", linestyle="--")

plt.xlabel("Pressure Level")
plt.ylabel("Specific Humidity (kg/kg)")
plt.title("GFS: 5-Day Summary of Specific Humidity (SPFH)")
plt.legend()
plt.tight_layout()
plt.savefig(output_path)
plt.close()

print(f"✅ GFS SPFH summary plot saved to {output_path}")
