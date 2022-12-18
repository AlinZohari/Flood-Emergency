import numpy
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio import plot
from shapely.geometry import Point, Polygon

if __name__ == "__main__":
    map = rasterio.open('D:/UCL/Geospatial Programming/Material/background/raster-50k_2724246.tif')
    dem = rasterio.open('D:/UCL/Geospatial Programming/Material/elevation/sz.asc')
    # rasterio.plot.show(map)

