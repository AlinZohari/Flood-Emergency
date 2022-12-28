import numpy
import geopandas as gpd
import pandas as pd
import rasterio
import rasterio.mask
import rasterio.windows
from rasterio import features
from rasterio import plot
from shapely.geometry import Point, LineString, Polygon, box
import matplotlib.pyplot as plt
import os
import json
import networkx as nx
import scipy as sp


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
    rasterio.plot.show(main_map, extent=study_buffer)
    print(study_buffer)

    # Task 2: Returns the point of highest elevation
    highest_elev = get_highest_point(study_buffer)
    print(highest_elev)

    # Task 3: Working with ITN
    # itn_network = pd.read_json('D:/UCL/Geospatial Programming/Material/itn/solent_itn.json')
    # print(itn_network.head())
    itn_json_path = os.path.join('D:/UCL/Geospatial Programming/Material/itn/solent_itn.json')
    with open(itn_json_path, 'r') as f:
        itn_json = json.load(f)

    itn_nodes = nx.Graph()
    road_links = itn_json['roadlinks']
    road_nodes = itn_json['roadnodes']
    road_links_inside_buffer = {}
    road_nodes_inside_buffer = {}
    all_new_line_strings = []
    all_new_points = []

    for links in road_links:
        new_line_string = LineString(road_links[links]['coords'])
        if study_buffer.contains(new_line_string):
            road_links_inside_buffer[links] = road_links[links]
            all_new_line_strings.append(new_line_string)

    for nodes in road_nodes:
        new_node_point = Point(road_nodes[nodes]['coords'])
        if study_buffer.contains(new_node_point):
            road_nodes_inside_buffer[nodes] = road_nodes[nodes]
            all_new_points.append(new_node_point)

    closest_distance_user_point_dist = 100000
    closest_distance_highest_elev_dist = 100000
    closest_distance_user_point = Point()
    closest_distance_highest_elev = Point()

    for x in all_new_points:
        if user_point.distance(x) < closest_distance_user_point_dist:
            closest_distance_user_point = x
            closest_distance_user_point_dist = user_point.distance(x)
        else:
            pass

    for x in all_new_points:
        if highest_elev.distance(x) < closest_distance_highest_elev_dist:
            closest_distance_highest_elev = x
            closest_distance_highest_elev_dist = highest_elev.distance(x)

    print(closest_distance_user_point)
    print(closest_distance_highest_elev)         # check the for loop for error

    closest_node_id_user = ''
    closest_node_id_high_elev = ''

    for nodes in road_nodes_inside_buffer:
        if [closest_distance_user_point.x, closest_distance_user_point.y] == road_nodes_inside_buffer[nodes]['coords']:
            closest_node_id_user = nodes

    for nodes in road_nodes_inside_buffer:
        if [closest_distance_highest_elev.x, closest_distance_highest_elev.y] == road_nodes_inside_buffer[nodes]['coords']:
            closest_node_id_high_elev = nodes

    print(closest_node_id_user)
    print(closest_node_id_high_elev)



    # print(road_links_inside_buffer)
    for link in road_links_inside_buffer:
        itn_nodes.add_edge(road_links_inside_buffer[link]['start'], road_links_inside_buffer[link]['end'], fid = link, weight = road_links_inside_buffer[link]['length'])

    path = nx.dijkstra_path(itn_nodes, source=closest_node_id_user, target=closest_node_id_high_elev, weight='weight')
    print(path)
    print(len(road_links_inside_buffer))
    print(len(road_links))

    # fig, ax = plt.subplots()
    # for line in all_new_line_strings:
    #     x, y = line.xy
    #     ax.plot(x, y)
    # print(len(all_new_line_strings))
    #
    # for point in all_new_points:
    #     x, y = point.xy
    #     ax.plot(x, y, 'ro')

    # nx.draw(itn_nodes, node_size=1)


    plt.show()
