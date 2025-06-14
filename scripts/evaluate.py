import pandas as pd
import matplotlib.pyplot as plt
import os, sys

CSV = os.path.join("logs", "runs.csv")
OUT = "plots"

if not os.path.exists(CSV):
    sys.exit(f"❌ {CSV} not found")

os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(CSV)
if df.empty:
    sys.exit("CSV is empty – nothing to plot.")

# 1. Core metrics
μ  = df.linesCleared.mean()
σ  = df.linesCleared.std()
mx = df.linesCleared.max()
success = (df.linesCleared >= 35).mean() * 100          # adjust goal here

print(f"Runs           : {len(df)}")
print(f"Mean           : {μ:6.2f}")
print(f"Std-dev        : {σ:6.2f}")
print(f"Best           : {mx}")
print(f"Success ≥150   : {success:5.1f} %")

# 2. Scatter + moving average
plt.figure(figsize=(7,4))
df.plot.scatter(x="run", y="linesCleared", s=12, ax=plt.gca())
df["MA20"] = df.linesCleared.rolling(20).mean()
df.plot(x="run", y="MA20", ax=plt.gca(), color="orange", lw=2)
plt.title("Lines cleared per run (dots)  –  20-run moving avg (orange)")
plt.savefig(f"{OUT}/scatter_ma.png", dpi=160); plt.close()

# 3. Histogram
plt.figure(figsize=(6,4))
df.linesCleared.plot.hist(bins=20, alpha=0.7)
plt.axvline(μ, color="r", ls="--", label=f"mean {μ:.1f}")
plt.legend(); plt.title("Histogram of linesCleared")
plt.savefig(f"{OUT}/histogram.png", dpi=160); plt.close()

# 4. Boxplot
plt.figure(figsize=(4,4))
df.boxplot(column="linesCleared")
plt.title("Spread / outliers")
plt.savefig(f"{OUT}/boxplot.png", dpi=160); plt.close()

# 5. Level vs linesCleared
fig, ax1 = plt.subplots(figsize=(7,4))
df.plot.scatter(x="run", y="linesCleared", ax=ax1,
                color="tab:blue", label="Lines")
ax2 = ax1.twinx()
df.plot.scatter(x="run", y="level", ax=ax2,
                color="tab:orange", label="Level")
ax1.set_ylabel("Lines cleared"); ax2.set_ylabel("Level")
fig.suptitle("Performance (left) vs game speed (right)")
fig.savefig(f"{OUT}/level_vs_lines.png", dpi=160); plt.close()
