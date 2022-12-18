import numpy
import geopandas as gpd
import pandas as pd
import rasterio
import rasterio.mask
import rasterio.windows
from rasterio import plot
from shapely.geometry import Point, LineString, Polygon
import matplotlib.pyplot as plt


def user_input():
    """
    Takes user input and makes sure it's in the MBR
    :return: returns a Point if it is inside the MBR
    """
    x = float(input('Insert x coordinate:'))
    y = float(input('Insert y coordinate:'))
    input_point = Point([x, y])

    if 430000 <= x <= 465000 and 80000 <= y <= 95000:
        plt.plot(x, y, 'ro')
        return input_point
    else:
        print("The co-ordinates are out of bounds")
        exit()


def get_buffer(point):
    buffer_zone = point.buffer(5000)  # Make a new function for this buffer task
    xp, yp = buffer_zone.exterior.xy
    plt.fill(xp, yp, 'bo')
    return buffer_zone


if __name__ == "__main__":
    map = rasterio.open('D:/UCL/Geospatial Programming/Material/background/raster-50k_2724246.tif')
    dem = rasterio.open('D:/UCL/Geospatial Programming/Material/elevation/sz.asc')

    user_point = user_input()
    study_buffer = get_buffer(user_point)
    print(study_buffer)
    # study_buffer = study_buffer.to_crs({'init': 'epsg:27700'})
    study_image, study_transform = rasterio.mask.mask(dem, [study_buffer], crop=True, filled=True)
    print(rasterio.mask.mask(dem, [study_buffer], crop=True, filled=True))
    """
        Masked Method: Not Successful
    study_meta = dem.meta
    study_meta.update({"driver": "GTiff",
                      "height": study_image.shape[1],
                       "width:": study_image.shape[2],
                       "transform": study_transform})

    # rasterio.plot.show(dem)
    with open("D:/UCL/Geospatial Programming/RGB.byte.masked.tif", 'w', **study_meta) as dest:
        dest.write(study_image)
    """
    rasterio.plot.show(study_image, transform=study_transform)
    rasterio.plot.show(map)

    plt.show()

