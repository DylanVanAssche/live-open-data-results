#!/bin/python
import argparse
import glob
import sys
from parser import TopParser
from plot import Plotter

class Main():
    def __init__(self, path, processes):
        self._path = path
        self._processes = processes
        self._data = {}
        print("Benchmarking processes: {}".format(processes))

    def run(self):
        # Recursive discover all files
        files = glob.glob(self._path, recursive=True)

        # Build the self._data tree by parsing each file correctly
        number_of_files = len(files)
        for i, path in enumerate(files):
            self.print_progress(i, number_of_files)

            # Extract data tree
            _, mode, interval, filename = path.split("/")
            self.create_data_tree(mode, interval)

            # Top file parsing
            top = TopParser(path, self._processes)
            top.parse()
            self._data[mode][interval] = {
                                                    "cpu": top.cpu,
                                                    "mem": top.mem,
                                                    "timeline": top.timeline
                                                }
        # Parsing complete
        print("\nFinished parsing, processing plots...")

        # Plot all the data using the Plotter class
        p = Plotter(self._data)

        # CPU and RAM usage
        p.plot("polling", 1)
        p.plot("polling", 30)
        #p.plot("pushing", 1)
        p.plot("pushing", 30)

    def print_progress(self, file_index, number_of_files):
        # Calculate percentage and generate progress bar
        percentage = ((file_index + 1) / number_of_files) * 100
        sys.stdout.write('\r')
        sys.stdout.write("[%-100s] %d%%" % ('=' * int(percentage), percentage))
        sys.stdout.flush()

    def create_data_tree(self, mode, interval):
        if not mode in self._data:
            self._data[mode] = {}

        if not interval in self._data[mode]:
            self._data[mode][interval] = {}

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Pushing vs Polling benchmark.")
    parser.add_argument('-p',
                        '--processes',
                        metavar='processes',
                        action='append',
                        help='<Required> List of processes to benchmark, for example: \" -p node -p nginx\"',
                        required=True)
    args = parser.parse_args()
    processes = args.processes

    # Run plotter
    m = Main("results/**/**/*.txt", processes)
    m.run()
