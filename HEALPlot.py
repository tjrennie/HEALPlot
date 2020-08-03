from tools.plotter import HPlot
import matplotlib.pyplot as plt
import sys

map1 = HPlot(sys.argv[1])
comap_map = map1.plot_map(sys.argv[2])
map1.overplot()
map1.plot_cbar(comap_map)
map1.plot_catalogue()
map1.show()
