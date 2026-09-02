import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns

# Set style for academic plots
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("muted")

out_dir = "outputs/figures"
os.makedirs(out_dir, exist_ok=True)

# 1. Plot Membership Functions for pH
pH_UoD = np.linspace(0, 14, 1000)
def trapmf(x, a, b, c, d):
    return np.maximum(0, np.minimum(np.minimum((x-a)/(b-a + 1e-9), 1), (d-x)/(d-c + 1e-9)))
def trimf(x, a, b, c):
    return np.maximum(0, np.minimum((x-a)/(b-a + 1e-9), (c-x)/(c-b + 1e-9)))

ph_mfs = {
    "ACIDIC": trapmf(pH_UoD, 0, 0, 5.0, 6.5),
    "SLIGHTLY_ACIDIC": trimf(pH_UoD, 5.5, 6.5, 7.2),
    "NEUTRAL": trimf(pH_UoD, 6.5, 7.0, 7.8),
    "SLIGHTLY_ALKALINE": trimf(pH_UoD, 7.2, 8.0, 8.8),
    "ALKALINE": trapmf(pH_UoD, 8.2, 9.0, 14, 14)
}

plt.figure(figsize=(10, 5))
for name, y in ph_mfs.items():
    plt.plot(pH_UoD, y, label=name, linewidth=2)
plt.title("Membership Functions for pH Input", fontsize=14, fontweight='bold')
plt.xlabel("pH Value", fontsize=12)
plt.ylabel("Degree of Membership (\u03bc)", fontsize=12)
plt.axvspan(6.5, 8.5, color='green', alpha=0.1, label='WHO Safe Zone')
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f"{out_dir}/mf_ph.png", dpi=300)
plt.close()

# 2. Plot Benchmark Results (Synthetic vs Kaggle)
labels = ['Mamdani FIS', 'Random Forest', 'KNN', 'SVM']
# From terminal output
synthetic_acc = [75.30, 99.50, 92.30, 95.70]
kaggle_acc = [60.43, 59.61, 54.40, 61.22]

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width/2, synthetic_acc, width, label='Synthetic Dataset (WHO Oracle)')
rects2 = ax.bar(x + width/2, kaggle_acc, width, label='Kaggle Dataset (Real-World)')

ax.set_ylabel('Accuracy (%)', fontsize=12)
ax.set_title('Classifier Performance Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11)
ax.legend(loc='lower right')
ax.set_ylim(0, 110)

# Add values on bars
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

autolabel(rects1)
autolabel(rects2)

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f"{out_dir}/benchmark_comparison.png", dpi=300)
plt.close()

print("[*] Generated figures in outputs/figures/")
