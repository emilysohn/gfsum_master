# plot_cdc_stats.py (UM)
import os
import pandas as pd
import matplotlib.pyplot as plt

source = "um"
csv_path = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/cdc_summary.csv"
output_dir = f"/ocean/projects/atm200005p/esohn1/gfsum_master/stats/{source}/figures"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["LCDC_mean"], label="Low Cloud", color="blue")
plt.plot(df["date"], df["MCDC_mean"], label="Mid Cloud", color="green")
plt.plot(df["date"], df["HCDC_mean"], label="High Cloud", color="red")

plt.xlabel("Date")
plt.ylabel("Cloud Fraction (0–1)")
plt.title("Daily Mean Cloud Cover by Type (UM)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "cdc_summary_plot.png"))
plt.close()
