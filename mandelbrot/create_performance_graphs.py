import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def generate_plots(filename):
    if not os.path.exists(filename):
        print(f"Ошибка: файл '{filename}' не найден.")
        return

    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")
        return

    required_columns = {'threads', 'points', 'average_time'}

    if not required_columns.issubset(df.columns):
        print(f"Ошибка: в CSV должны быть колонки: {required_columns}")
        return

    df = df.sort_values(by=['points', 'threads'])

    # Время выполнения на одном потоке для каждого количества точек
    t_serial_map = (
        df[df['threads'] == 1]
        .set_index('points')['average_time']
        .to_dict()
    )

    if not t_serial_map:
        print("Ошибка: отсутствуют данные для одного потока.")
        return

    df['t_serial'] = df['points'].map(t_serial_map)

    # Ускорение
    df['speedup'] = df['t_serial'] / df['average_time']

    # Эффективность
    df['efficiency'] = df['speedup'] / df['threads']

    unique_points = sorted(df['points'].unique())

    os.makedirs('plots', exist_ok=True)

    # ---------------------------------------------------------
    # График 1. Время выполнения
    # ---------------------------------------------------------

    plt.figure(figsize=(9, 6))

    for points in unique_points:
        subset = df[df['points'] == points]

        plt.plot(
            subset['threads'],
            subset['average_time'],
            marker='o',
            label=f'{points:,} точек'
        )

    plt.title('Время выполнения программы')
    plt.xlabel('Количество потоков')
    plt.ylabel('Среднее время выполнения (с)')
    plt.yscale('log')
    plt.xticks(sorted(df['threads'].unique()))
    plt.grid(True, alpha=0.5)
    plt.legend()
    plt.tight_layout()

    plt.savefig('plots/execution_time.png', dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # График 2. Ускорение
    # ---------------------------------------------------------

    plt.figure(figsize=(9, 6))

    for points in unique_points:
        subset = df[df['points'] == points]

        plt.plot(
            subset['threads'],
            subset['speedup'],
            marker='o',
            label=f'{points:,} точек'
        )

    max_threads = df['threads'].max()

    plt.plot(
        [1, max_threads],
        [1, max_threads],
        'k--',
        label='Идеальное ускорение',
        alpha=0.5
    )

    plt.title('Ускорение параллельной программы')
    plt.xlabel('Количество потоков')
    plt.ylabel('Ускорение S = T1 / Tp')
    plt.xticks(sorted(df['threads'].unique()))
    plt.grid(True, alpha=0.5)
    plt.legend()
    plt.tight_layout()

    plt.savefig('plots/speedup.png', dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # График 3. Эффективность
    # ---------------------------------------------------------

    plt.figure(figsize=(9, 6))

    for points in unique_points:
        subset = df[df['points'] == points]

        plt.plot(
            subset['threads'],
            subset['efficiency'],
            marker='o',
            label=f'{points:,} точек'
        )

    plt.axhline(
        y=1.0,
        color='black',
        linestyle='--',
        label='Идеальная эффективность',
        alpha=0.5
    )

    plt.title('Эффективность распараллеливания')
    plt.xlabel('Количество потоков')
    plt.ylabel('Эффективность E = S / p')
    plt.xticks(sorted(df['threads'].unique()))
    plt.ylim(bottom=0)
    plt.grid(True, alpha=0.5)
    plt.legend()
    plt.tight_layout()

    plt.savefig('plots/efficiency.png', dpi=300)
    plt.close()

    print("Графики успешно сохранены:")
    print("plots/execution_time.png")
    print("plots/speedup.png")
    print("plots/efficiency.png")


if __name__ == "__main__":
    csv_file = "performance_results.csv"

    if len(sys.argv) > 1:
        csv_file = sys.argv[1]

    generate_plots(csv_file)