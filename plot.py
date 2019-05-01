#!/bin/python
import argparse
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import glob
import sys
import statistics
from datetime import datetime
BAR_WIDTH = 0.8
COLOR_CPU = "#3465a4"
COLOR_MEM = "#c9211e"

class Plotter():
    def __init__(self, data, bar_width=BAR_WIDTH):
        self._data = data
        self._bar_width = bar_width

        # Set figure size
        plt.rcParams["figure.figsize"] = [12, 8]

    def legend_plot(self):
        custom_lines = [Line2D([0], [0], color=COLOR_CPU, lw=4),
                        Line2D([0], [0], color=COLOR_MEM, lw=4)]
        plt.legend(custom_lines, ["CPU", "Memory"])

    def axis_labels_plot(self, y_max, y_label, unit):
        # X labels
        plt.xlabel("Time (s)")

        # Y labels
        plt.ylabel("{} ({})".format(y_label, unit))
        plt.ylim(0, min(1.25 * y_max, 100))

    def bar_values(self, bar_graph, unit, rounding):
        # Draw values on top of each bar
        for bar in bar_graph:
            y = bar.get_height()
            y_value = round(y, rounding)
            if rounding == 0:
                y_value = int(y_value)
            plt.text(bar.get_x() + self._bar_width/2,
                     1.05 * y,
                     "{} {}".format(y_value, unit),
                     va="bottom",
                     ha="center",
                     fontweight="bold",
                     fontsize=10)

    def plot(self, mode, interval):
        # Check if implemented
        assert(mode == "polling" or mode == "pushing")
        assert(interval == 1 or interval == 30)

        # Generate beautiful title
        if mode == "polling" and interval == 1:
            plt.title("HTTP polling\n1 second interval")
        elif mode == "polling" and interval == 30:
            plt.title("HTTP polling\n30 seconds interval")
        elif mode == "pushing" and interval == 1:
            plt.title("SSE pushing\n1 second interval")
        elif mode == "pushing" and interval == 30:
            plt.title("SSE pushing\n30 seconds interval")
        else:
            raise NotImplementedError("Unknown benchmark mode ({}) and/or interval ({})".format(name, interval))

        # Set figure size
        plt.rcParams["figure.figsize"] = [12, 8]

        # Paths are strings, not numbers
        interval = str(interval)

        # X-axis data
        y_max = 0
        unit = "%"

        # Find the mean and max values
        mean_cpu = statistics.mean(self._data[mode][interval]["cpu"])
        mean_mem = statistics.mean(self._data[mode][interval]["mem"])
        max_cpu = max(self._data[mode][interval]["cpu"])
        max_mem = max(self._data[mode][interval]["mem"])
        y_max = max(max_cpu, max_mem)

        # Plot CPU and memory usage
        plt.plot(self._data[mode][interval]["timeline"],
                             self._data[mode][interval]["cpu"],
                             color=COLOR_CPU)
        plt.plot(self._data[mode][interval]["timeline"],
                             self._data[mode][interval]["mem"],
                             color=COLOR_MEM)

        # Plot the mean CPU and memory usage as text
        props = dict(boxstyle='round', facecolor='white', alpha=0.15)
        plt.text(-60.0,
                 min(1.25 * y_max, 100) * 0.95,
                 "Mean CPU usage: {} %\nMean memory usage: {} %".format(round(mean_cpu, 1), round(mean_mem, 1)),
                 verticalalignment="center",
                 fontsize=10,
                 linespacing=1.75,
                 bbox=props)

        # Labels and legend
        self.axis_labels_plot(y_max, "Usage", unit)
        self.legend_plot()
        plt.show()

