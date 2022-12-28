import numpy
import geopandas as gpd
import pandas as pd
import rasterio
import rasterio.mask
import rasterio.windows
from rasterio import features
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
    """
    Takes a point as an input and returns a 5km bufferzone around it
    :param point: a Point Class object from Shapely Package
    :return: buffer_zone (Polygon) and plots it
    """
    buffer_zone = point.buffer(5000)  # Make a new function for this buffer task
    xp, yp = buffer_zone.exterior.xy
    plt.fill(xp, yp, facecolor='blue', alpha=0.5)
    return buffer_zone


def get_highest_point(buffer_study_area):
    """
    Gets the buffer area around the user's point and plots and returns the highest elevation point in that area.
    :param buffer_study_area: a buffer raster
    :return: Point of highest elevation
    """
    study_area = rasterio.mask.mask(dem, [buffer_study_area], crop=True, filled=True)  # Main Study Area

    indices_x_y = numpy.where(study_area[0] == study_area[0].max())          # returns 3 arrays with 1 element each
    # x = indices_x_y[2][0] i.e. x position in the array
    # y = indices_x_y[1][0] i.e y position in the array
    x_max_elev = buffer_study_area.bounds[0] + indices_x_y[2][0] * 5
    y_max_elev = buffer_study_area.bounds[3] - indices_x_y[1][0] * 5
    print(numpy.max(study_area[0]))
    plt.plot(x_max_elev, y_max_elev, 'ro')
    rasterio.plot.show(study_area[0], transform=study_area[1])
    return Point([x_max_elev, y_max_elev])


if __name__ == "__main__":
    main_map = rasterio.open('D:/UCL/Geospatial Programming/Material/background/raster-50k_2724246.tif')
    dem = rasterio.open('D:/UCL/Geospatial Programming/Material/elevation/sz.asc')
    print(dem.bounds)

    user_point = user_input()
    study_buffer = get_buffer(user_point)

    # Task 2: Returns the point of highest elevation
    highest_elev = get_highest_point(study_buffer)
    print(highest_elev)

    # study_image = rasterio.mask.mask(dem, [study_buffer], crop=True, filled=True)    #Main Study Area
    # print(study_image)
    # print(study_buffer.bounds[0], study_buffer.bounds[3])
    #
    # indices = numpy.where(study_image[0] == study_image[0].max())
    # print(indices)
    # print(indices[2][0])
    # print(indices[1][0])
    # print(study_image[1].bounds)
    #
    # x = study_buffer.bounds[0] + indices[2][0] * 5
    # y = study_buffer.bounds[3] - indices[1][0] * 5
    #
    # print(x, y)
    #
    # max_elev = numpy.max(study_image[0])
    # print(max_elev)
    # plt.plot(x,y, 'ro')
    #
    # rasterio.plot.show(study_image[0], transform=study_image[1])
    rasterio.plot.show(main_map, extent=study_buffer)              # overlap the buffer and the map together
                                                                   # It's not working now but it's intentional
    plt.show()
