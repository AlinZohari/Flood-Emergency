# Flood Emergency Planning

**Table of Content**
1. [Abstract](https://github.com/AlinZohari/Flood-Emergency?tab=readme-ov-file#abstract)
2. [Dependencies](https://github.com/AlinZohari/Flood-Emergency?tab=readme-ov-file#dependencies)
3. [Limitations](https://github.com/AlinZohari/Flood-Emergency?tab=readme-ov-file#limitations)

## Abstract
The software is built as a flood emergency plan that assist user on the Isle of Wight.
When the user enter their coordinate on the island, it will return to the user the position of the highest point within a 5 kilometer of radius from them.
It shows which route to take that are the shortest and would give the time it would take for the user to walk from their position to the highest point. <br>
<br>
![image](https://github.com/AlinZohari/Flood-Emergency/assets/89179323/c886d5b0-df65-4af0-bf72-ed173728ee40)

## Dependencies

- [NumPy](https://numpy.org/)
- [GeoPandas](https://geopandas.org/)
- [Pandas](https://pandas.pydata.org/)
- [Rasterio](https://rasterio.readthedocs.io/)
- [Shapely](https://shapely.readthedocs.io/)
- [Matplotlib](https://matplotlib.org/)
- [NetworkX](https://networkx.github.io/)
- [SciPy](https://www.scipy.org/)
- [Pyproj](https://pyproj4.github.io/pyproj/stable/)
- [Cartopy](https://scitools.org.uk/cartopy/docs/latest/)
- [matplotlib_scalebar](https://github.com/ppinard/matplotlib-scalebar)

## Limitations
The development of the software only consider the nearest node within the 5km buffer zone. For example, if a node exist which are more near to the highest point but are outside of the 5km buffer zone it will not classify it as the nearest node. Instead the software uses only the nearest node to the highest point which are inside the buffer. This may result on creation of different shortest pathway.
