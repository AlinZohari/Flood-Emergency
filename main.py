import numpy
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio import plot
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt


def user_input():
    """
    Takes user input and makes sure it's in the MBR
    :return: returns a Point if it is inside the MBR
    """
    x = float(input('Insert x coordinate:'))
    y = float(input('Insert y coordinate:'))
    input_point = Point([x, y])
    buffer_zone = input_point.buffer(5000)          # Make a new function for this buffer task
    xp, yp = buffer_zone.exterior.xy
    if 430000 <= x <= 465000 and 80000 <= y <= 95000:
        plt.fill(xp, yp, 'bo')
        plt.plot(x, y, 'ro')
        return input_point
    else:
        print("The co-ordinates are out of bounds")
        exit()


if __name__ == "__main__":
    map = rasterio.open('D:/UCL/Geospatial Programming/Material/background/raster-50k_2724246.tif')
    dem = rasterio.open('D:/UCL/Geospatial Programming/Material/elevation/sz.asc')
    user_input()
    rasterio.plot.show(map)
    plt.show()

