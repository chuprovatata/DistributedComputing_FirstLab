
import os
import pandas as pd
import matplotlib.pyplot as plt

# Каталог для сохранения графиков
OUTPUT_DIR = "graphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Общие настройки графиков
plt.rcParams["figure.figsize"] = (9, 5.5)
plt.rcParams["font.size"] = 11
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

# ==========================================
# 1. Сравнение времени выполнения
# ==========================================

threads = [1, 2, 4, 8, 12]

static_times = [
    0.713287,
    0.346175,
    0.223956,
    0.179192,
    0.152094
]

dynamic_times = [
    0.683428,
    0.321270,
    0.175289,
    0.147634,
    0.136320
]

df = pd.DataFrame({
    "threads": threads,
    "static_time_s": static_times,
    "dynamic_time_s": dynamic_times
})

# Сохраняем исходные данные в CSV
df.to_csv(
    os.path.join(OUTPUT_DIR, "benchmark_summary.csv"),
    index=False
)

plt.figure()
plt.plot(
    threads, static_times,
    marker="o", linewidth=2,
    label="Static"
)
plt.plot(
    threads, dynamic_times,
    marker="s", linewidth=2,
    label="Dynamic"
)

plt.xlabel("Number of threads")
plt.ylabel("Execution time (s)")
plt.title("N-body: execution time vs. thread count")
plt.xticks(threads)
plt.legend()
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "01_execution_time.png"),
    dpi=300, bbox_inches="tight"
)
plt.close()


# ==========================================
# 2. Ускорение динамической реализации
# ==========================================

df["speedup"] = (
    df["static_time_s"] / df["dynamic_time_s"]
)

plt.figure()
bars = plt.bar(
    [str(t) for t in threads],
    df["speedup"]
)

plt.axhline(
    y=1.0, linestyle="--",
    label="No speedup (1.0x)"
)

plt.bar_label(
    bars,
    labels=[f"{x:.2f}x" for x in df["speedup"]],
    padding=3
)

plt.xlabel("Number of threads")
plt.ylabel("Speedup (static / dynamic)")
plt.title("Dynamic implementation speedup")
plt.legend()
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "02_speedup.png"),
    dpi=300, bbox_inches="tight"
)
plt.close()


# ==========================================
# 3. Процент сокращения времени
# ==========================================

df["faster_percent"] = (
    (df["static_time_s"] - df["dynamic_time_s"])
    / df["static_time_s"] * 100
)

plt.figure()
bars = plt.bar(
    [str(t) for t in threads],
    df["faster_percent"]
)

plt.bar_label(
    bars,
    labels=[f"{x:.1f}%" for x in df["faster_percent"]],
    padding=3
)

plt.xlabel("Number of threads")
plt.ylabel("Execution time reduction (%)")
plt.title("Dynamic vs. static implementation")
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "03_time_reduction.png"),
    dpi=300, bbox_inches="tight"
)
plt.close()


# ==========================================
# 4. Влияние размера chunk
# ==========================================

chunks = [1, 10, 50, 100]

chunk_times = [
    0.088557,
    0.091127,
    0.094139,
    0.100810
]

chunk_df = pd.DataFrame({
    "chunk": chunks,
    "mean_time_s": chunk_times
})

chunk_df.to_csv(
    os.path.join(OUTPUT_DIR, "chunk_experiment.csv"),
    index=False
)

plt.figure()
plt.plot(
    chunks, chunk_times,
    marker="o", linewidth=2
)

for x, y in zip(chunks, chunk_times):
    plt.annotate(
        f"{y:.4f} s",
        (x, y),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center"
    )

plt.xlabel("Chunk size")
plt.ylabel("Mean execution time (s)")
plt.title("Effect of chunk size (12 threads)")
plt.xticks(chunks)
plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "04_chunk_comparison.png"),
    dpi=300, bbox_inches="tight"
)
plt.close()

print("Graphs created successfully:")
for filename in sorted(os.listdir(OUTPUT_DIR)):
    print(os.path.join(OUTPUT_DIR, filename))

