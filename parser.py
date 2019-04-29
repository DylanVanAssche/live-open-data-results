#!/bin/python
import statistics
import sys
from datetime import datetime
from collections import OrderedDict


class BaseParser:
    def __init__(self, input_file, process=None):
        self._input_file = input_file
        self._lines = []
        self._timestamps = []
        self._timeline = [] # Start at 0s
        self._process = process
        self.read_file()

    def read_file(self):
        with open(self._input_file, "r") as f:
           self._lines = f.readlines()

    def parse(self):
        raise NotImplementedError("Parsing method is absent")

    def convert_timestamps(self):
        # Convert timestamps to timeline
        if not self._timestamps:
            return

        begin_timestamp = self._timestamps[0]
        for t in self._timestamps:
            self._timeline.append(t - begin_timestamp)

        # Remove duplicates
        self._timeline = list(OrderedDict.fromkeys(self._timeline))

    @property
    def timeline(self):
        return self._timeline

class TopParser(BaseParser):
    def __init__(self, input_file, process):
        super().__init__(input_file, process)
        self._cpu = {}
        self._mem = {}

    def parse(self):
        for line in self._lines:
            try:
                valid = False
                for p in self._process:
                    if p in line:
                        valid = True
                        break

                if valid:
                    day, month, date, time, timezone, year, pid, user, priority, nice, virtual_mem, res, shr, state, cpu, mem, cputime, *command = line.split()
                    self._timestamps.append(datetime.strptime(time, "%H:%M:%S").timestamp())
                    if time not in self._cpu:
                        self._cpu[time] = []

                    if time not in self._mem:
                        self._mem[time] = []

                    self._cpu[time].append(float(cpu))
                    self._mem[time].append(float(mem))
            except Exception as e:
                print("\nERROR: {} for parsing line: {} in file {}".format(e, line, self._input_file), file=sys.stderr)
                raise e
        cpu_list = []
        mem_list = []
        for k in self._cpu.keys():
            self._cpu[k] = sum(self._cpu[k])
            cpu_list.append(self._cpu[k])

        for k in self._mem.keys():
            self._mem[k] = sum(self._mem[k])
            mem_list.append(self._mem[k])
        self.convert_timestamps()
        self._cpu = cpu_list
        self._mem = mem_list

    @property
    def cpu(self):
        return self._cpu

    @property
    def mem(self):
        return self._mem

class UserInformedTimeParser(BaseParser):
    def __init__(self, input_file):
        super().__init__(input_file)
        self._liveboard_timestamps = []
        self._planner_timestamps = []
        self._liveboard = []
        self._planner = []

    def parse(self):
        for line in self._lines:
            try:
                if "$" in line:
                    _, name, timestamp = line.split(",")
                    if "liveboard" in name:
                        self._liveboard.append(abs(int(timestamp)))
                    elif "router" in name:
                        self._planner.append(abs(int(timestamp)))
                    else:
                        raise NotImplementedError("Unknown benchmark name")
            except ValueError as e:
                pass # Ignore unused log 
            except Exception as e:
                print("\nERROR: {} for parsing line: {} in file {}".format(e, line, self._input_file), file=sys.stderr)

    @property
    def liveboard(self):
        return self._liveboard

    @property
    def planner(self):
        return self._planner
