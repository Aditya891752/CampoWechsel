"""
Plot 10-Year NDVI Climatology & Bare-Field Window for Thomas County, KS.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from fieldshift.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, DEFAULT_BARE_FIELD_NDVI

# Output path
img_path = PROCESSED_DATA_DIR / "thomas_ndvi_climatology.png"

# Load 16-day NDVI
ndvi_df = pd.read_csv(RAW_DATA_DIR / "ndvi_thomas.csv")
ndvi_df["date"] = pd.to_datetime(ndvi_df["date"])
ndvi_df["month"] = ndvi_df["date"].dt.month

# Climatology by month
climatology = ndvi_df.groupby("month")["ndvi"].agg(["mean", "std", "min", "max"]).reset_index()
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
climatology["month_name"] = months

# Identify bare-field months
bare_months = climatology[climatology["mean"] < DEFAULT_BARE_FIELD_NDVI]

# High-contrast plot styling (Rules: No gradients, no dark low-contrast, crisp sunlight readability)
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FFFFFF")

# Plot standard deviation band
ax.fill_between(
    climatology["month"],
    climatology["mean"] - climatology["std"],
    climatology["mean"] + climatology["std"],
    color="#2D6A4F",
    alpha=0.18,
    label="±1 Std Dev (10-Yr Climatology)",
)

# Plot Mean NDVI line
ax.plot(
    climatology["month"],
    climatology["mean"],
    color="#1B5E20",
    linewidth=2.5,
    marker="o",
    markersize=6,
    label="10-Year Mean Monthly NDVI",
)

# Bare-field threshold line
ax.axhline(
    y=DEFAULT_BARE_FIELD_NDVI,
    color="#B91C1C",
    linestyle="--",
    linewidth=1.8,
    label=f"Bare-Field Threshold (NDVI < {DEFAULT_BARE_FIELD_NDVI:.2f})",
)

# Shading for bare-field months (July - October)
ax.axvspan(6.5, 10.5, color="#B91C1C", alpha=0.10, label="Bare-Field Window (July–Oct)")

# Annotate peak and bare periods
peak_row = climatology.loc[climatology["mean"].idxmax()]
ax.annotate(
    f"Wheat Heading Peak\nNDVI: {peak_row['mean']:.2f}",
    xy=(peak_row["month"], peak_row["mean"]),
    xytext=(peak_row["month"] - 1.5, peak_row["mean"] + 0.08),
    arrowprops=dict(facecolor="#1B5E20", shrink=0.05, width=1.2, headwidth=6),
    fontsize=9,
    fontweight="bold",
    color="#1B5E20",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#E8F5E9", edgecolor="#81C784"),
)

ax.annotate(
    "Post-Harvest Summer Fallow\nBare soil exposed to high wind & heat\n(NDVI < 0.20)",
    xy=(8, 0.16),
    xytext=(7.5, 0.35),
    arrowprops=dict(facecolor="#B91C1C", shrink=0.05, width=1.2, headwidth=6),
    fontsize=9,
    fontweight="bold",
    color="#B91C1C",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFEBEE", edgecolor="#EF9A9A"),
)

ax.set_xticks(range(1, 13))
ax.set_xticklabels(months, fontsize=10, fontweight="bold", color="#0F172A")
ax.set_ylabel("NDVI (Normalized Difference Vegetation Index)", fontsize=11, fontweight="bold", color="#0F172A")
ax.set_xlabel("Calendar Month", fontsize=11, fontweight="bold", color="#0F172A")
ax.set_title("Thomas County (Colby, KS) — 10-Year MODIS NDVI Climatology (2015–2024)", fontsize=13, fontweight="bold", pad=12, color="#0F172A")
ax.set_ylim(0.05, 0.75)
ax.grid(True, linestyle=":", alpha=0.6, color="#CBD5E1")
ax.legend(loc="upper right", frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=9)

# Note on source and proxy honesty rule
fig.text(
    0.10, 0.02,
    "Source: MODIS MOD13Q1 (250m) via AppEEARS reference proxy modulated by NASA POWER daily observations. [is_proxy=True]",
    fontsize=8, color="#64748B", style="italic"
)

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig(img_path)
plt.close()
print(f"Plot saved successfully to {img_path}")

# Print tabular climatology summary
print("\n--- Thomas County 10-Year Monthly NDVI Climatology ---")
print(climatology[["month", "month_name", "mean", "std", "min", "max"]].to_string(index=False))
