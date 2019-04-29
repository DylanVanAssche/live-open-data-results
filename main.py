#!/bin/python
import argparse
import glob
import sys
from parser import TopParser
from plot import Plotter

class Main():
    def __init__(self, path, process):
        self._path = path
        self._process = process
        self._data = {}
        print("Benchmarking process: {}".format(process))

    def run(self):
        # Recursive discover all files
        files = glob.glob(self._path, recursive=True)
        benchmark="polling30s"
        self._data[benchmark] = {}

        # Build the self._data tree by parsing each file correctly
        number_of_files = len(files)
        for i, path in enumerate(files):
            self.print_progress(i, number_of_files)
            print(path)
            _, mode, interval, filename = path.split("/")
            print(mode)
            print(interval)

            # Top file
            top = TopParser(path, self._process)
            top.parse()
            self._data[benchmark]["top"] = {
                                                            "cpu": top.cpu,
                                                            "mem": top.mem,
                                                            "timeline": top.timeline
                                                       }
        # Parsing complete
        print("\nFinished parsing, processing plots...")

        # Plot all the data using the Plotter class
        p = Plotter(self._data)

        # CPU and RAM usage
        p.plot_top("liveboard", "cpu")

    def print_progress(self, file_index, number_of_files):
        # Calculate percentage and generate progress bar
        percentage = ((file_index + 1) / number_of_files) * 100
        sys.stdout.write('\r')
        sys.stdout.write("[%-100s] %d%%" % ('=' * int(percentage), percentage))
        sys.stdout.flush()

    def create_data_tree(self, benchmark, part, device):
        # Benchmark: original, rt-poll or rt-sse
        if not benchmark in self._data:
            self._data[benchmark] = {}

        # Part of benchmark: liveboard or planner
        if not part in self._data[benchmark]:
            self._data[benchmark][part] = {}

        # Device: jolla-1 or xperia-x
        if not device in self._data[benchmark][part]:
            self._data[benchmark][part][device] = {}

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="LCRail benchmark.")
    parser.add_argument('-p',
                        '--processes',
                        metavar='processes',
                        action='append',
                        help='<Required> List of processes to benchmark, for example: \"node nginx\"',
                        required=True)
    args = parser.parse_args()
    processes = args.processes
    m = Main("results/**/**/*.txt", processes)
    m.run()

