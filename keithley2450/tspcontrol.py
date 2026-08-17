# Authored 2024 Lalit Singh
# Modified 2026 Miguel Ong (@ahalation)
#

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from ttkwidgets.frames import Tooltip
from src.keithley2450 import Keithley2450TSP

plt.switch_backend("TkAgg")

class Keithley2450MSC(tk.Tk):
    """
    Measurement Source Control (MSC) Application for the Keithley 2450 using customised pymeasure Instrument class rewritten to use TSP instead of SCIP.
    Includes context manager to initiate mode switch to TSP and back after completion of measurement.
    Currently supported:
    Linear I-V Sweep
    Planned:
    PUND Sequence - purely experimental - minimum pulse and measure times estimated at approx ~0.2ms which may be too large for most micro+nano ferroelectrics
    Possible but not currently planned:
    Logarithmic Sweep
    List (Custom Level) Sweep
    """

    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.title("Keithley 2450 TSP Control")
        self.gpibLabel = tk.Label(self, text="GPIB Address:")
        self.gpibLabel.grid(row=0, column=0, padx=10, pady=5)
        self.gpibEntry = tk.Entry(self)
        self.gpibEntry.grid(row=0, column=1, padx=10, pady=5)
        self.gpibEntry.insert(0, "GPIB::19")
        self.initButton = tk.Button(self, text="Initialize", command=self.initialise)
        self.initButton.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.portLabel = tk.Label(self, text="Select Port:")
        self.portLabel.grid(row=2, column=0, padx=10, pady=5)
        self.portVar = tk.StringVar(self)
        self.portMenu = ttk.Combobox(self, textvariable=self.portVar)
        self.portMenu["values"] = ("Front", "Rear")
        self.portMenu.grid(row=2, column=1, padx=10, pady=5)
        self.portMenu.current(1)
        self.startVoltLabel = tk.Label(self, text="Start/Stop Voltage (V):")
        self.startVoltLabel.grid(row=3, column=0, padx=10, pady=5)
        self.startVoltEntry = tk.Entry(self)
        self.startVoltEntry.grid(row=3, column=1, padx=10, pady=5)
        self.startVoltEntry.insert(0, "0")
        self.maxVoltLabel = tk.Label(self, text="Max Voltage (V):")
        self.maxVoltLabel.grid(row=4, column=0, padx=10, pady=5)
        self.maxVoltEntry = tk.Entry(self)
        self.maxVoltEntry.grid(row=4, column=1, padx=10, pady=5)
        self.maxVoltEntry.insert(0, "5")
        self.minVoltLabel = tk.Label(self, text="Min Voltage (V):")
        self.minVoltLabel.grid(row=5, column=0, padx=10, pady=5)
        self.minVoltEntry = tk.Entry(self)
        self.minVoltEntry.grid(row=5, column=1, padx=10, pady=5)
        self.minVoltEntry.insert(0, "-5")
        self.infoMinVoltLabel = tk.Label(self, text=" \u2753 ")
        self.infoMinVoltLabel.grid(row=5, column=2, padx=2, pady=0)
        self.infoMinVoltTooltip = Tooltip(self.infoMinVoltLabel, headertext=None, text="""If set to Start/Stop Voltage, only forward loop will be executed
                                                                                          If Start/Stop, Max and Min Voltage are all equal, a static DC measurement will be taken instead""", timeout=0, showheader=0)
        self.stepLabel = tk.Label(self, text="Step Value (V):")
        self.stepLabel.grid(row=7, column=0, padx=10, pady=5)
        self.stepEntry = tk.Entry(self)
        self.stepEntry.grid(row=7, column=1, padx=10, pady=5)
        self.stepEntry.insert(0, "0.5")
        self.compCurrLabel = tk.Label(self, text="Compliance Current (mA):")
        self.compCurrLabel.grid(row=8, column=0, padx=10, pady=5)
        self.compCurrEntry = tk.Entry(self)
        self.compCurrEntry.grid(row=8, column=1, padx=10, pady=5)
        self.compCurrEntry.insert(0, "0.01")
        self.cyclesLabel = tk.Label(self, text="Number of Cycles:")
        self.cyclesLabel.grid(row=9, column=0, padx=10, pady=5)
        self.cyclesEntry = tk.Entry(self)
        self.cyclesEntry.grid(row=9, column=1, padx=10, pady=5)
        self.cyclesEntry.insert(0, "1")
        self.filenameLabel = tk.Label(self, text="Output filename (.csv):")
        self.filenameLabel.grid(row=10, column=0, padx=10, pady=5)
        self.filenameEntry = tk.Entry(self)
        self.filenameEntry.grid(row=10, column=1, padx=10, pady=5)
        self.filenameEntry.insert(0, "IV_measurement")
        self.infoFilenameLabel = tk.Label(self, text=" \u2753 ")
        self.infoFilenameLabel.grid(row=10, column=2, padx=2, pady=0)
        self.infoFilenameTooltip = Tooltip(self.infoFilenameLabel, headertext=None, text="Output file will be generated at the same directory as this script, in .csv format", timeout=0, showheader=0)
        self.advancedLabel = tk.Label(self, text="--- Advanced Settings ---")
        self.advancedLabel.grid(row=11, column=0, columnspan=2, padx=10, pady=5)
        self.sweepTypeLabel = tk.Label(self, text="Sweep Type")
        self.sweepTypeLabel.grid(row=12, column=0, padx=10, pady=5)
        self.sweepTypeVar = tk.StringVar(self)
        self.sweepTypeMenu = ttk.Combobox(self, textvariable=self.sweepTypeVar)
        self.sweepTypeMenu["values"] = ("Linear")
        self.sweepTypeMenu.grid(row=12, column=1, padx=10, pady=5)
        self.sweepTypeMenu.current(0)
        self.infoSweepTypeLabel = tk.Label(self, text=" \u2753 ")
        self.infoSweepTypeLabel.grid(row=12, column=2, padx=2, pady=0)
        self.infoSweepTypeTooltip = Tooltip(self.infoSweepTypeLabel, headertext=None, text="Logarithmic and List sweeps are also available but will only be implemented upon request", timeout=0, showheader=0)
        self.nplcLabel = tk.Label(self, text="Measurement Read Time (ms):")
        self.nplcLabel.grid(row=13, column=0, padx=10, pady=5)
        self.nplcVar = tk.StringVar(self)
        self.nplcMenu = ttk.Combobox(self, textvariable=self.nplcVar)
        # NOTE - Corresponding NPLC Values: 0.01, 0.05, 0.1, 0.5, 1, 5, 10
        self.nplcMenu["values"] = ("0.2ms", "1ms", "2ms", "10ms", "20ms", "100ms", "200ms")
        self.nplcMenu.grid(row=13, column=1, padx=10, pady=5)
        self.nplcMenu.current(4)
        self.infoNplcLabel = tk.Label(self, text=" \u2753 ")
        self.infoNplcLabel.grid(row=13, column=2, padx=2, pady=0)
        self.infoNplcTooltip = Tooltip(self.infoNplcLabel, headertext=None, text="""Read times are obtained via number of power line cycles(NPLC) divided by power line frequency
                                                                                    Keithley 2450 NPLC range: 0.01 to 10 (Default 1)
                                                                                    Singapore Mains Frequency: 50Hz""", timeout=0, showheader=0)
        self.delayLabel = tk.Label(self, text="Source Delay (ms):")
        self.delayLabel.grid(row=14, column=0, padx=10, pady=5)
        self.delayEntry = tk.Entry(self)
        self.delayEntry.grid(row=14, column=1, padx=10, pady=5)
        self.delayEntry.insert(0, "-1")
        self.infoDelayLabel = tk.Label(self, text=" \u2753 ")
        self.infoDelayLabel.grid(row=14, column=2, padx=2, pady=0)
        self.infoDelayTooltip = Tooltip(self.infoDelayLabel, headertext=None, text="If set to a negative value, will use autodelay", timeout=0, showheader=0)
        self.sourceRangeLabel = tk.Label(self, text="Source Signal Range:")
        self.sourceRangeLabel.grid(row=16, column=0, padx=10, pady=5)
        self.sourceRangeVar = tk.StringVar(self)
        self.sourceRangeMenu = ttk.Combobox(self, textvariable=self.sourceRangeVar)
        self.sourceRangeMenu["values"] = ("Auto", "20mV", "200mV", "2V", "20V", "200V")
        self.sourceRangeMenu.grid(row=16, column=1, padx=10, pady=5)
        self.sourceRangeMenu.current(0)
        self.measureRangeLabel = tk.Label(self, text="Measurement Signal Range (mA):")
        self.measureRangeLabel.grid(row=17, column=0, padx=10, pady=5)
        self.measureRangeEntry = tk.Entry(self)
        self.measureRangeEntry.grid(row=17, column=1, padx=10, pady=5)
        self.measureRangeEntry.insert(0, "-1")
        self.infoMeasureRangeLabel = tk.Label(self, text=" \u2753 ")
        self.infoMeasureRangeLabel.grid(row=17, column=2, padx=2, pady=0)
        self.infoMeasureRangeTooltip = Tooltip(self.infoMeasureRangeLabel, headertext=None, text="""Set to a value approximately 125% of your estimated maximum output reading.
                                                                                                    If set to a negative value, will use autorange""", timeout=0, showheader=0)
        self.button_start = tk.Button(self, text="Start Measurement", command=self.measure)
        self.button_start.grid(row=19, column=0, columnspan=2, padx=10, pady=20)

    def initialise(self) -> None:
        #TODO - test if reachable at supplied gpib address
        #TODO - test ctxmgr scpi-tsp switch
        try:
            # self.smu = Keithley2450TSP(gpib_address)
            messagebox.showinfo("Hi", "Test Message.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        # pass

    def measure(self) -> None:
        #TODO - setup scpi-tsp context switch
        #TODO - setup ports
        #TODO - setup nplc
        #TODO - check if only forward loop to execute
        #TODO - setup source ranging
        #TODO - setup measure ranging
        #TODO - setup source (as input) and sweep (0) delays
        #TODO - setup sweep params
        #TODO - generate sweeps
        #TODO - reset sources
        #TODO - read buffer
        #TODO - reset buffer
        #TODO - convert buffer into df
        #TODO - plot graph
        #TODO - output to csv with given filename
        pass

if __name__ == "__main__":
    app = Keithley2450MSC()
    app.mainloop()

#SECTION - Decompiled Lalit Script
# import matplotlib
# matplotlib.use("TkAgg")
# import tkinter as tk
# from tkinter import ttk, messagebox
# from pymeasure.instruments.keithley import Keithley2450
# import time
# import csv
# import matplotlib.pyplot as plt
# import numpy as np
# class KeithleyControlApp(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Keithley 2450 SMU Control")
#         self.initButton = tk.Button(self, text="Initialize", command=self.initialize_smu)
#         self.initButton.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
#         self.gpibLabel = tk.Label(self, text="GPIB Address:")
#         self.gpibLabel.grid(row=1, column=0, padx=10, pady=5)
#         self.gpibEntry = tk.Entry(self)
#         self.gpibEntry.grid(row=1, column=1, padx=10, pady=5)
#         self.gpibEntry.insert(0, "GPIB::18")
#         self.startVoltLabel = tk.Label(self, text="Start Voltage (V):")
#         self.startVoltLabel.grid(row=2, column=0, padx=10, pady=5)
#         self.startVoltEntry = tk.Entry(self)
#         self.startVoltEntry.grid(row=2, column=1, padx=10, pady=5)
#         self.startVoltEntry.insert(0, "0")
#         self.maxVoltLabel = tk.Label(self, text="Max Voltage (V):")
#         self.maxVoltLabel.grid(row=3, column=0, padx=10, pady=5)
#         self.maxVoltEntry = tk.Entry(self)
#         self.maxVoltEntry.grid(row=3, column=1, padx=10, pady=5)
#         self.maxVoltEntry.insert(0, "5")
#         self.minVoltLabel = tk.Label(self, text="Min Voltage (V):")
#         self.minVoltLabel.grid(row=4, column=0, padx=10, pady=5)
#         self.minVoltEntry = tk.Entry(self)
#         self.minVoltEntry.grid(row=4, column=1, padx=10, pady=5)
#         self.minVoltEntry.insert(0, "-5")
#         self.stopVoltLabel = tk.Label(self, text="Stop Voltage (V):")
#         self.stopVoltLabel.grid(row=5, column=0, padx=10, pady=5)
#         self.stopVoltEntry = tk.Entry(self)
#         self.stopVoltEntry.grid(row=5, column=1, padx=10, pady=5)
#         self.stopVoltEntry.insert(0, "0")
#         self.stepLabel = tk.Label(self, text="Step Value (V):")
#         self.stepLabel.grid(row=6, column=0, padx=10, pady=5)
#         self.stepEntry = tk.Entry(self)
#         self.stepEntry.grid(row=6, column=1, padx=10, pady=5)
#         self.stepEntry.insert(0, "0.5")
#         self.cyclesLabel = tk.Label(self, text="Number of Cycles:")
#         self.cyclesLabel.grid(row=7, column=0, padx=10, pady=5)
#         self.cyclesEntry = tk.Entry(self)
#         self.cyclesEntry.grid(row=7, column=1, padx=10, pady=5)
#         self.cyclesEntry.insert(0, "1")
#         self.compCurrLabel = tk.Label(self, text="Compliance Current (A):")
#         self.compCurrLabel.grid(row=8, column=0, padx=10, pady=5)
#         self.compCurrEntry = tk.Entry(self)
#         self.compCurrEntry.grid(row=8, column=1, padx=10, pady=5)
#         self.compCurrEntry.insert(0, "0.00001")
#         self.portLabel = tk.Label(self, text="Select Port:")
#         self.portLabel.grid(row=9, column=0, padx=10, pady=5)
#         self.portVar = tk.StringVar(self)
#         self.portMenu = ttk.Combobox(self, textvariable=self.portVar)
#         self.portMenu["values"] = ("Front", "Rear")
#         self.portMenu.current(0)
#         self.portMenu.grid(row=9, column=1, padx=10, pady=5)
#         self.button_start = tk.Button(self, text="Start Measurement", command=self.start_measurement)
#         self.button_start.grid(row=10, column=0, columnspan=2, padx=10, pady=20)
#     def initialize_smu(self):
#         gpib_address = self.gpibEntry.get()
#         try:
#             self.smu = Keithley2450(gpib_address)
#             messagebox.showinfo("Initialization", "Keithley 2450 SMU initialized successfully.")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))
#     def start_measurement(self):
#         start_voltage = float(self.startVoltEntry.get())
#         max_voltage = float(self.maxVoltEntry.get())
#         min_voltage = float(self.minVoltEntry.get())
#         stop_voltage = float(self.stopVoltEntry.get())
#         step_value = float(self.stepEntry.get())
#         num_cycles = int(self.cyclesEntry.get())
#         compliance_current = float(self.compCurrEntry.get())
#         selected_port = self.portVar.get()
#         try:
#             if selected_port == "Front":
#                 self.smu.use_front_terminals()
#             else:
#                 self.smu.use_rear_terminals()
#             self.smu.apply_voltage()
#             self.smu.source_current_limit = compliance_current
#             self.smu.enable_source()
#             data = []
#             for cycle in range(num_cycles):
#                 voltages_up = np.arange(start_voltage, max_voltage + step_value, step_value)
#                 voltages_down = np.arange(max_voltage, min_voltage - step_value, -step_value)
#                 voltages_final = np.arange(min_voltage, stop_voltage + step_value, step_value)
#                 voltages = np.concatenate((voltages_up, voltages_down, voltages_final))
#                 for voltage in voltages:
#                     self.smu.source_voltage = voltage
#                     time.sleep(0.1)
#                     current = self.smu.current
#                     data.append((voltage, current))
#                     print(f"Cycle: {cycle + 1}, Voltage: {voltage} V, Current: {current} A")
#             self.smu.shutdown()
#             with open("vi_loop_measurement_results.csv", "w", newline="") as file:
#                 writer = csv.writer(file)
#                 writer.writerow(["Voltage (V)", "Current (A)"])
#                 writer.writerows(data)
#             voltages, currents = zip(*data)
#             plt.figure()
#             plt.plot(voltages, currents, marker="o")
#             plt.xlabel("Voltage (V)")
#             plt.ylabel("Current (A)")
#             plt.title("VI Loop Characteristic")
#             plt.grid(True)
#             plt.show()
#             messagebox.showinfo("Success", "VI Loop Measurement completed successfully and results saved to \"vi_loop_measurement_results.csv\".")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))
# if __name__ == "__main__":
#     app = KeithleyControlApp()
#     app.mainloop()
#END_SECTION