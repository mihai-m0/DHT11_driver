"""Plot a CSV file produced by dht11_logger.py.

Usage:
    python plot_log.py dht11_log.csv
    python plot_log.py dht11_log.csv --save plot.png
"""

import argparse
import csv
from datetime import datetime

import matplotlib.pyplot as plt


def load_csv(path):
    """Return three lists: timestamps, temperatures, humidities."""
    times, temps, hums = [], [], []
    with open(path, newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            times.append(datetime.fromisoformat(row["timestamp"]))
            temps.append(int(row["temperature_c"]))
            hums.append(int(row["humidity_pct"]))
    return times, temps, hums


def main():
    parser = argparse.ArgumentParser(description="Plot a DHT11 log file.")
    parser.add_argument("csv_file", help="CSV file written by dht11_logger.py")
    parser.add_argument("--save", help="save the figure to this file instead of showing it")
    args = parser.parse_args()

    times, temps, hums = load_csv(args.csv_file)
    if not times:
        raise SystemExit("The CSV file contains no readings yet.")

    fig, (ax_temp, ax_hum) = plt.subplots(2, 1, sharex=True, figsize=(9, 6))

    ax_temp.plot(times, temps, marker="o", markersize=3)
    ax_temp.set_ylabel("Temperature (C)")
    ax_temp.grid(True)

    ax_hum.plot(times, hums, marker="o", markersize=3)
    ax_hum.set_ylabel("Humidity (%)")
    ax_hum.set_xlabel("Time")
    ax_hum.grid(True)

    fig.suptitle("DHT11 readings")
    fig.autofmt_xdate()

    if args.save:
        fig.savefig(args.save, dpi=150, bbox_inches="tight")
        print(f"Saved {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
