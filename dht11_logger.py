"""Log DHT11 readings sent by the Arduino over USB serial into a CSV file.

The Arduino sketch prints one line per successful reading

Any other line (for example "No response" or "Sum is wrong!") is treated as a
diagnostic message from the driver and is only echoed to the console.

Usage:
    python dht11_logger.py COM3
    python dht11_logger.py /dev/ttyACM0 --output my_log.csv
"""

import argparse
import csv
import os
import re
import sys
import time
from datetime import datetime

import serial  # provided by the "pyserial" package

# A valid reading is two unsigned integers separated by a comma.
READING_RE = re.compile(r"^Temp is (\d+)\s*C,\s*Humidity is (\d+)\s*%$")

CSV_HEADER = ["timestamp", "temperature_c", "humidity_pct"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Log DHT11 readings from an Arduino serial port to CSV."
    )
    parser.add_argument("port", help="serial port, e.g. COM3 or /dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=9600,
                        help="baud rate; must match Serial.begin() (default: 9600)")
    parser.add_argument("--output", default="dht11_log.csv",
                        help="CSV file to append to (default: dht11_log.csv)")
    return parser.parse_args()


def parse_reading(line):
    """Return (temperature, humidity) as ints, or None if the line is not a reading."""
    match = READING_RE.match(line)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def csv_needs_header(path):
    """True if the file does not exist yet or is empty."""
    return not os.path.exists(path) or os.path.getsize(path) == 0


def main():
    args = parse_args()
    write_header = csv_needs_header(args.output)

    try:
        ser = serial.Serial(args.port, args.baud, timeout=3)
    except serial.SerialException as err:
        sys.exit(f"Could not open {args.port}: {err}\n"
                 "Is the Arduino Serial Monitor still open?")

    with ser, open(args.output, "a", newline="") as csv_file:
        # Opening the port usually resets the Arduino;give it time to boot.
        time.sleep(2)
        ser.reset_input_buffer()

        writer = csv.writer(csv_file)
        if write_header:
            writer.writerow(CSV_HEADER)

        print(f"Logging from {args.port} to {args.output}. Press Ctrl+C to stop.")
        try:
            while True:
                raw = ser.readline()          # blocks for at most `timeout` seconds
                if not raw:
                    continue                  # timeout: nothing arrived, try again

                line = raw.decode("utf-8", errors="replace").strip()
                reading = parse_reading(line)

                if reading is None:
                    print(f"[arduino] {line}")
                    continue

                temperature, humidity = reading
                timestamp = datetime.now().isoformat(timespec="seconds")

                writer.writerow([timestamp, temperature, humidity])
                csv_file.flush()              # keep the file valid if the script is killed
                print(f"{timestamp}  {temperature} C  {humidity} %")
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
