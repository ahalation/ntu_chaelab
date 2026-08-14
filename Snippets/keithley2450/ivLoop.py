
#TODO - fix compliance current 
#TODO - add pund
#TODO - convert instructions to smu

#SECTION - Decompiled Lalit Script
# import matplotlib
# matplotlib.use('TkAgg')
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
#         self.title('Keithley 2450 SMU Control')
#         self.button_initialize = tk.Button(self, text='Initialize', command=self.initialize_smu)
#         self.button_initialize.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
#         self.label_gpib = tk.Label(self, text='GPIB Address:')
#         self.label_gpib.grid(row=1, column=0, padx=10, pady=5)
#         self.entry_gpib = tk.Entry(self)
#         self.entry_gpib.grid(row=1, column=1, padx=10, pady=5)
#         self.entry_gpib.insert(0, 'GPIB::18')
#         self.label_start_volt = tk.Label(self, text='Start Voltage (V):')
#         self.label_start_volt.grid(row=2, column=0, padx=10, pady=5)
#         self.entry_start_volt = tk.Entry(self)
#         self.entry_start_volt.grid(row=2, column=1, padx=10, pady=5)
#         self.entry_start_volt.insert(0, '0')
#         self.label_max_volt = tk.Label(self, text='Max Voltage (V):')
#         self.label_max_volt.grid(row=3, column=0, padx=10, pady=5)
#         self.entry_max_volt = tk.Entry(self)
#         self.entry_max_volt.grid(row=3, column=1, padx=10, pady=5)
#         self.entry_max_volt.insert(0, '5')
#         self.label_min_volt = tk.Label(self, text='Min Voltage (V):')
#         self.label_min_volt.grid(row=4, column=0, padx=10, pady=5)
#         self.entry_min_volt = tk.Entry(self)
#         self.entry_min_volt.grid(row=4, column=1, padx=10, pady=5)
#         self.entry_min_volt.insert(0, '-5')
#         self.label_stop_volt = tk.Label(self, text='Stop Voltage (V):')
#         self.label_stop_volt.grid(row=5, column=0, padx=10, pady=5)
#         self.entry_stop_volt = tk.Entry(self)
#         self.entry_stop_volt.grid(row=5, column=1, padx=10, pady=5)
#         self.entry_stop_volt.insert(0, '0')
#         self.label_step_value = tk.Label(self, text='Step Value (V):')
#         self.label_step_value.grid(row=6, column=0, padx=10, pady=5)
#         self.entry_step_value = tk.Entry(self)
#         self.entry_step_value.grid(row=6, column=1, padx=10, pady=5)
#         self.entry_step_value.insert(0, '0.5')
#         self.label_num_cycles = tk.Label(self, text='Number of Cycles:')
#         self.label_num_cycles.grid(row=7, column=0, padx=10, pady=5)
#         self.entry_num_cycles = tk.Entry(self)
#         self.entry_num_cycles.grid(row=7, column=1, padx=10, pady=5)
#         self.entry_num_cycles.insert(0, '1')
#         self.label_comp_current = tk.Label(self, text='Compliance Current (A):')
#         self.label_comp_current.grid(row=8, column=0, padx=10, pady=5)
#         self.entry_comp_current = tk.Entry(self)
#         self.entry_comp_current.grid(row=8, column=1, padx=10, pady=5)
#         self.entry_comp_current.insert(0, '0.00001')
#         self.label_port = tk.Label(self, text='Select Port:')
#         self.label_port.grid(row=9, column=0, padx=10, pady=5)
#         self.port_var = tk.StringVar(self)
#         self.port_menu = ttk.Combobox(self, textvariable=self.port_var)
#         self.port_menu['values'] = ('Front', 'Rear')
#         self.port_menu.current(0)
#         self.port_menu.grid(row=9, column=1, padx=10, pady=5)
#         self.button_start = tk.Button(self, text='Start Measurement', command=self.start_measurement)
#         self.button_start.grid(row=10, column=0, columnspan=2, padx=10, pady=20)
#     def initialize_smu(self):
#         gpib_address = self.entry_gpib.get()
#         try:
#             self.smu = Keithley2450(gpib_address)
#             messagebox.showinfo('Initialization', 'Keithley 2450 SMU initialized successfully.')
#         except Exception as e:
#             messagebox.showerror('Error', str(e))
#     def start_measurement(self):
#         start_voltage = float(self.entry_start_volt.get())
#         max_voltage = float(self.entry_max_volt.get())
#         min_voltage = float(self.entry_min_volt.get())
#         stop_voltage = float(self.entry_stop_volt.get())
#         step_value = float(self.entry_step_value.get())
#         num_cycles = int(self.entry_num_cycles.get())
#         compliance_current = float(self.entry_comp_current.get())
#         selected_port = self.port_var.get()
#         try:
#             if selected_port == 'Front':
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
#                     print(f'Cycle: {cycle + 1}, Voltage: {voltage} V, Current: {current} A')
#             self.smu.shutdown()
#             with open('vi_loop_measurement_results.csv', 'w', newline='') as file:
#                 writer = csv.writer(file)
#                 writer.writerow(['Voltage (V)', 'Current (A)'])
#                 writer.writerows(data)
#             voltages, currents = zip(*data)
#             plt.figure()
#             plt.plot(voltages, currents, marker='o')
#             plt.xlabel('Voltage (V)')
#             plt.ylabel('Current (A)')
#             plt.title('VI Loop Characteristic')
#             plt.grid(True)
#             plt.show()
#             messagebox.showinfo('Success', 'VI Loop Measurement completed successfully and results saved to \'vi_loop_measurement_results.csv\'.')
#         except Exception as e:
#             messagebox.showerror('Error', str(e))
# if __name__ == '__main__':
#     app = KeithleyControlApp()
#     app.mainloop()
#END_SECTION