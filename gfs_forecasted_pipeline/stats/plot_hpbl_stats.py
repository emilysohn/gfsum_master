# plot_hpbl_stats.py
import os
import pandas as pd
import matplotlib.pyplot as plt

source = "gfs_forecasted"
csv_path = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/hpbl_summary.csv"
output_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/figures"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(csv_path)
dates = pd.to_datetime(df["date"])

plt.figure(figsize=(8, 5))
plt.plot(dates, df["mean_HPBL_m"], label="Mean", marker="o")
plt.plot(dates, df["min_HPBL_m"], label="Min", linestyle="--")
plt.plot(dates, df["max_HPBL_m"], label="Max", linestyle="--")
plt.ylabel("Boundary Layer Height (m)")
plt.xlabel("Date")
plt.title("Daily HPBL Statistics (GFS Actual)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "hpbl_summary_plot.png"))
plt.close()
