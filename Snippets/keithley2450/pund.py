# Authored 2026 Miguel Ong (@ahalation)
# Derived from 2024 Lalit Singh
#
# NOTE
# purely experimental - minimum pulse and measure times estimated at approx ~20ms which may be too large for most micro+nano ferroelectrics

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from src.keithley2450 import Keithley2450TSP

plt.switch_backend("TkAgg")

class Keithley2450PUND(tk.Tk):
    """
    #TODO - replace placeholder description
    PUND Control Application using custom pymeasure Instrument library rewritten to use TSP instead of SCIP
    """
    pass

