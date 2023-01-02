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
    # print(numpy.max(study_area[0]))
    plt.plot(x_max_elev, y_max_elev, 'ro')
    rasterio.plot.show(study_area[0], transform=study_area[1])
    return Point([x_max_elev, y_max_elev])


def get_closest_node_point(point, all_nodes_inside_buffer):
    """
    Takes a point and a list of all node points inside the buffer around the point. Returns the closest
    node(Point Object) to the given point
    :param point: A Point Object (user_input and the user point)
    :param all_nodes_inside_buffer: list of all the node points inside the buffer around user point
    :return: returns a node (Point Object) closest to the point
    """
    total_distance_from_point = 100000
    closest_node_to_point = Point()

    for i in all_nodes_inside_buffer:
        if point.distance(i) < total_distance_from_point:
            closest_node_to_point = i
            total_distance_from_point = point.distance(i)
        else:
            pass
    return closest_node_to_point


def get_id_of_closest_node(closest_node, node_points_inside_buffer):
    """
    Get id of the closest node
    :param closest_node: closest node (Point)
    :param node_points_inside_buffer: list of node_points inside the buffer
    :return: returns a string of node id
    """
    closest_node_id = ''
    for nodes in node_points_inside_buffer:
        if [closest_node.x, closest_node.y] == node_points_inside_buffer[nodes]['coords']:
            closest_node_id = nodes
    return closest_node_id


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
    # print(highest_elev)

    # Task 3: Working with ITN and getting closest node to both points
    itn_json_path = os.path.join('D:/UCL/Geospatial Programming/Material/itn/solent_itn.json')
    with open(itn_json_path, 'r') as f:
        itn_json = json.load(f)        # read json file

    itn_nodes = nx.Graph()
    road_links = itn_json['roadlinks']
    road_nodes = itn_json['roadnodes']
    road_links_inside_buffer = {}
    road_nodes_inside_buffer = {}
    all_new_line_strings = []
    all_node_points_inside_buffer = []

    for links in road_links:
        new_line_string = LineString(road_links[links]['coords'])   # convert the road links from json into linestrings
        if study_buffer.contains(new_line_string):
            road_links_inside_buffer[links] = road_links[links]
            all_new_line_strings.append(new_line_string)         # create road links within the buffer zone

    for nodes in road_nodes:
        new_node_point = Point(road_nodes[nodes]['coords'])       # convert node points from json into point coordinates
        if study_buffer.contains(new_node_point):
            road_nodes_inside_buffer[nodes] = road_nodes[nodes]
            all_node_points_inside_buffer.append(new_node_point)  # create node points within the buffer zone

    # Getting the closest node to user and highest point using the get_closest_node_point() function
    closest_distance_user_point = get_closest_node_point(user_point, all_node_points_inside_buffer)
    closest_distance_highest_elev = get_closest_node_point(highest_elev, all_node_points_inside_buffer)

    print(closest_distance_user_point)
    print(closest_distance_highest_elev)         # check the for loop for error

    # Getting the id of the closest node to user and highest point using the get_id_of_closest_node() function
    closest_node_id_user = get_id_of_closest_node(closest_distance_user_point, road_nodes_inside_buffer)
    closest_node_id_high_elev = get_id_of_closest_node(closest_distance_highest_elev, road_nodes_inside_buffer)

    print(closest_node_id_user)
    print(closest_node_id_high_elev)

    # print(road_links_inside_buffer)
    for link in road_links_inside_buffer:
        itn_nodes.add_edge(road_links_inside_buffer[link]['start'], road_links_inside_buffer[link]['end'], fid = link, weight = road_links_inside_buffer[link]['length'])
        # compute all the road links between the nearest point to the user input coordinate
        # and the nearest point to the highest elevation point

    path = nx.dijkstra_path(itn_nodes, source=closest_node_id_user, target=closest_node_id_high_elev, weight='weight')
    # find the shortest road links
    print(path)

    # Following Code Block was taken from Practical Section of Week 8 from Jupyter Notebook
    links = []
    geom = []
    first_node = path[0]
    for node in path[1:]:
        link_fid = itn_nodes.edges[first_node, node]['fid']
        links.append(link_fid)
        geom.append(LineString(road_links[link_fid]['coords']))
        first_node = node
    shortest_path_gpd = gpd.GeoDataFrame({'fid': links, 'geometry': geom})
    shortest_path_gpd.plot()

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
