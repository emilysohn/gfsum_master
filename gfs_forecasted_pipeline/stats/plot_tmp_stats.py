# plot_tmp_summary_gfs.py
import pandas as pd
import matplotlib.pyplot as plt
import os

csv_path = "/ocean/projects/atm200005p/esohn1/gfsum_master/stats/gfs_forecasted/tmp_5day_summary.csv"
output_dir = "/ocean/projects/atm200005p/esohn1/gfsum_master/stats/gfs_forecasted/figures"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(csv_path)

plt.figure(figsize=(8, 5))
levels = df['Level']
x = range(len(levels))
plt.plot(x, df['TMP_min'], label='Min TMP', marker='o')
plt.plot(x, df['TMP_max'], label='Max TMP', marker='o')
plt.plot(x, df['TMP_mean'], label='Mean TMP', marker='o')

plt.xticks(x, levels)
plt.xlabel("Pressure Level")
plt.ylabel("Temperature (K)")
plt.title("5-Day Summary of Temperature (GFS)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "tmp_5day_summary_plot.png"))
plt.close()
