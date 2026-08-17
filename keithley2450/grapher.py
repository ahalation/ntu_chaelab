import os
import matplotlib.pyplot as plt
import pandas as pd

INPUTDIR: str = ".\\in"
OUTPUTDIR: str = ".\\out"

def main() -> None:
    for f in os.listdir(INPUTDIR):
        fd = rf".\in\{f}"
        rt, ext = os.path.splitext(fd)
        if ext == ".csv":
            df = pd.read_csv(fd)
            v, i = df.to_numpy().T
            # fig, (ax1, ax2) = plt.subplots(1, 2)
            fig, ax1 = plt.subplots()
            df.plot(x="Voltage (V)", y="Current (A)", ax=ax1)
            ax1.set(title=rt.rsplit("\\", 1)[1])
            ax1.tick_params(direction="in", which="both")
            ax1.grid()
            plt.show()

if __name__ == "__main__":
    main()