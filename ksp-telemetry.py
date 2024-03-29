#!/usr/bin/env python3

"""ksp-telemetry.py

This script graphs the telemetry data generated by Mechjeb, a Kerbal Space Program mod.
"""

# Copyright(C) 2019 Al2Me6
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__version__ = "1.2.1"

import argparse
import csv
import os
import sys
from typing import Dict, Tuple

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description=f"KSP Telemetry Grapher v{__version__}",
                                 allow_abbrev=False)
parser.add_argument("telemetry",
                    metavar="TELEMETRY_FILE",
                    type=argparse.FileType('r'),
                    help="path to Mechjeb telemetry CSV")
parser.add_argument("--title",
                    metavar="TITLE",
                    type=str,
                    help="add TITLE to graph")
parser.add_argument("--verbose",
                    action="store_true",
                    help="graph additional data")
parser.add_argument("--out",
                    metavar="OUTPUT",
                    type=argparse.FileType('wb'),
                    help="save graph to OUTPUT, allowable filetypes: eps, jpeg, \
                          jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff")
parser.add_argument("--no-view",
                    action="store_true",
                    help="do not view graph after generation (requires --out)")
args = parser.parse_args()

# "dependent" argument parsing
if args.no_view and not args.out:  # argument should be of type None if not passed
    parser.print_usage(sys.stderr)
    print(f"{os.path.basename(__file__)}: error: argument --no-view: requires argument --out",
          file=sys.stderr)
    sys.exit(2)

print(f"KSP Telemetry Grapher v{__version__}")

print(f"Loading Mechjeb telemetry file \"{args.telemetry.name}\"")
# convert column of rows to row of columns
reader = csv.reader(args.telemetry)
headers = next(reader)
raw_data = tuple(tuple(float(val) for val in line) for line in reader)
telemetry_data: Dict[str, Tuple[float, ...]] = {col: tuple(row[idx] for row in raw_data)
                                                for idx, col in enumerate(headers)}
args.telemetry.close()


def arrange_subplots() -> Tuple[int, int]:
    """Return correct arrangement of plots according to verbosity"""
    return (2, 3) if args.verbose else (2, 2)


fig = plt.figure(figsize=(14, 6) if args.verbose else (10, 6))

if args.title:
    fig.suptitle(args.title, fontsize=14)

try:
    plt.subplot(*arrange_subplots(), 1)  # asterisk expands tuple
    plt.plot([dist / 1000 for dist in telemetry_data["DownRange"]],  # convert to km
             [alt_asl / 1000 for alt_asl in telemetry_data["AltitudeASL"]])
    plt.title("Launch Profile")
    plt.xlabel("Distance downrange (km)")
    plt.ylabel("Altitude ASL (km)")
    plt.grid()

    plt.subplot(*arrange_subplots(), 2)
    plt.plot(telemetry_data["TimeSinceMark"], telemetry_data["Acceleration"])
    plt.title("Acceleration")
    plt.xlabel("MET (s)")
    plt.ylabel("Acceleration (g)")
    plt.grid()

    plt.subplot(*arrange_subplots(), 3)
    plt.plot(telemetry_data["TimeSinceMark"], telemetry_data["SpeedOrbital"])
    plt.title("Orbital Velocity")
    plt.xlabel("MET (s)")
    plt.ylabel("Orbital velocity (m/s)")
    plt.grid()

    plt.subplot(*arrange_subplots(), 4)
    plt.plot([alt_asl / 1000 for alt_asl in telemetry_data["AltitudeASL"]],
             telemetry_data["Q"])
    plt.title("Dynamic Pressure")
    plt.xlabel("Altitude ASL (km)")
    plt.ylabel("Q (Pa)")
    plt.grid()

    if args.verbose:
        plt.subplot(*arrange_subplots(), 5)
        plt.plot(telemetry_data["TimeSinceMark"][3:],  # remove erroneous measurements
                 telemetry_data["AoA"][3:])
        plt.title("Angle of Attack")
        plt.xlabel("MET (s)")
        plt.ylabel("AoA (deg)")
        plt.grid()

        plt.subplot(*arrange_subplots(), 6)
        plt.plot(telemetry_data["TimeSinceMark"],
                 telemetry_data["DeltaVExpended"], label="Δv Expended")
        tan_vel = telemetry_data["SpeedOrbital"][0]
        dv_lost = [dv_exp - telemetry_data["SpeedOrbital"][i] +
                   tan_vel for i, dv_exp in enumerate(telemetry_data["DeltaVExpended"])]
        plt.plot(telemetry_data["TimeSinceMark"], dv_lost, label="Δv Lost")
        plt.title("Delta-v Expenditure")
        plt.xlabel("MET (s)")
        plt.ylabel("Δv (m/s)")
        plt.legend(loc="upper left")
        plt.grid()
except KeyError:
    print("Error: could not find correct data entries in the file passed!")
    sys.exit(1)

plt.subplots_adjust(hspace=0.5, wspace=0.3)  # prevent overlap

if args.out:
    print(f"Saving graph to \"{args.out.name}\"")
    plt.savefig(args.out)
    args.out.close()

if not args.no_view:
    print("Opening preview")
    plt.show()

print("Done")
sys.exit(0)
