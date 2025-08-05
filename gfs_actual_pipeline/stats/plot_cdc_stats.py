# plot_cdc_stats.py
import os
import pandas as pd
import matplotlib.pyplot as plt

source = "gfs_actual"
csv_path = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/cdc_summary.csv"
output_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/figures"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(csv_path)
dates = pd.to_datetime(df["date"])

plt.figure(figsize=(8, 5))
plt.plot(dates, df["LCDC_mean"], label="Low Cloud", marker="o")
plt.plot(dates, df["MCDC_mean"], label="Mid Cloud", marker="o")
plt.plot(dates, df["HCDC_mean"], label="High Cloud", marker="o")
plt.ylabel("Cloud Cover Fraction (0–1)")
plt.xlabel("Date")
plt.title("Daily Mean Cloud Type Coverage (GFS Actual)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "cdc_summary_plot.png"))
plt.close()
