import numpy
import geopandas as gpd
import numpy as np
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
import pyproj
from cartopy import crs


def user_input(island_bounds):
    """
    Takes user input and makes sure it's in the MBR
    :param island_bounds: a shapefile polygon to check if the user point is on the island.
    :return: returns a Point if it is inside the MBR
    """
    x = float(input('Insert x coordinate:'))
    y = float(input('Insert y coordinate:'))
    input_point = Point([x, y])
    if island_bounds.contains(input_point):
        if 425000 <= x <= 470000 and 75000 <= y <= 100000:
            # plt.plot(x, y, 'ro')
            return input_point
        else:
            print("The co-ordinates are out of bounds")
            exit()
    else:
        print("You are already drowning in water.")
        exit()


def user_wd():
    """
        Get user's Material's file path
        :return: returns a String
        """
    wd = input('Input your Material file path:')
    wd = wd.replace('\\', '/')
    return wd


def get_buffer(point):
    """
    Takes a point as an input and returns a 5km bufferzone around it
    :param point: a Point Class object from Shapely Package
    :return: buffer_zone (Polygon) and plots it
    """
    if 430000 <= point.x <= 465000 and 80000 <= point.y <= 95000:
        buffer_zone = point.buffer(5000)  # Make a new function for this buffer task
        # xp, yp = buffer_zone.exterior.xy
        # plt.fill(xp, yp, facecolor='blue', alpha=0.5)
        return buffer_zone
    else:
        buffer_zone = point.buffer(5000)
        map_bounds = Polygon([(428825.0, 74465.0), (466875.0, 74465.0), (466875.0, 97470.0), (428825.0, 97470.0)])
        t6_buffer_zone = buffer_zone.intersection(map_bounds)
        # xp, yp = t6_buffer_zone.exterior.xy
        # plt.fill(xp, yp, facecolor='blue', alpha=0.5)
        return t6_buffer_zone


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
    # plt.plot(x_max_elev, y_max_elev, 'ro')
    # rasterio.plot.show(study_area[0], transform=study_area[1])
    return Point([x_max_elev, y_max_elev])


def find_elevation_by_point(point, buffer_study_area):
    """
    Find elevation at any given point
    :param point: Point Object
    :param buffer_study_area: buffer area around the user point
    :return: elevation value as a float
    """
    study_area = rasterio.mask.mask(dem, [buffer_study_area], crop=True, filled=True)
    x_index = int((point.x - buffer_study_area.bounds[0]) / 5)
    y_index = int((buffer_study_area.bounds[3] - point.y) / 5)
    return study_area[0][0][y_index][x_index]


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


def get_time_for_roadlink(roadlink, buffer):
    """
    Returns time in minutes to travel a roadlink between 2 nodes by taking into account the elevation using
    Naismith's rule
    :param roadlink: Roadlink Id
    :param buffer: Study Buffer
    :return: Minutes needed to travel as an int
    """
    start_node_elevation = find_elevation_by_point(Point(roadlink['coords'][0]), buffer)
    end_node_elevation = find_elevation_by_point(Point(roadlink['coords'][-1]), buffer)
    elevation_change = end_node_elevation - start_node_elevation
    if elevation_change > 0:
        added_time = elevation_change // 10
        time_taken = (roadlink['length'] / 5000) * 60 + added_time
    else:
        time_taken = (roadlink['length'] / 5000) * 60
    return time_taken


if __name__ == "__main__":
    working_d = user_wd()
    if working_d.endswith('/Material') == False:
        print("Please enter the file path ending with 'Material':")
        working_d = user_wd()

    main_map = rasterio.open(working_d + '/background/raster-50k_2724246.tif')
    dem = rasterio.open(working_d + '/elevation/sz.asc')
    island_shape_df = gpd.read_file(working_d + '/shape/isle_of_wight.shp')
    island_shape = island_shape_df['geometry'][0]

    # print(main_map.bounds)
    # print(dem.bounds)
    # print(dem)

    user_point = user_input(island_shape)
    study_buffer = get_buffer(user_point)
    # rasterio.plot.show(main_map, extent=study_buffer)
    # print(study_buffer)

    # Task 2: Returns the point of highest elevation
    highest_elev = get_highest_point(study_buffer)
    study_area = rasterio.mask.mask(dem, [study_buffer], crop=True, filled=True)
    study_area[0][study_area[0] == 0] = None

    # print(highest_elev)
    # print(find_elevation_by_point(highest_elev, study_buffer))

    # Task 3: Working with ITN and getting closest node to both points
    itn_json_path = os.path.join(working_d + '/itn/solent_itn.json')
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

    # Add a new value to the road_links_inside_buffer dictionary for time take to be used as weight
    for i in road_links_inside_buffer:
        road_links_inside_buffer[i]['time taken'] = get_time_for_roadlink(road_links_inside_buffer[i], study_buffer)

    print(closest_distance_user_point)
    print(closest_distance_highest_elev)         # check the for loop for error

    # Getting the id of the closest node to user and highest point using the get_id_of_closest_node() function
    closest_node_id_user = get_id_of_closest_node(closest_distance_user_point, road_nodes_inside_buffer)
    closest_node_id_high_elev = get_id_of_closest_node(closest_distance_highest_elev, road_nodes_inside_buffer)

    print(closest_node_id_user)
    print(closest_node_id_high_elev)

    # print(road_links_inside_buffer)
    for link in road_links_inside_buffer:
        itn_nodes.add_edge(road_links_inside_buffer[link]['start'], road_links_inside_buffer[link]['end'], fid=link, weight=road_links_inside_buffer[link]['time taken'])
        # compute all the road links between the nearest point to the user input coordinate
        # and the nearest point to the highest elevation point

    path = nx.dijkstra_path(itn_nodes, source=closest_node_id_user, target=closest_node_id_high_elev, weight='weight')
    # find the shortest road nodes
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

    # fig, ax = plt.subplots

    # Following Code block was taken from Practical Section of Week 8 from Jupyter Notebook
    back_array_main_map = main_map.read(1)
    pallete_main_map = np.array(([value for key, value in main_map.colormap(1).items()]))
    background_image = pallete_main_map[back_array_main_map]
    bounds = main_map.bounds
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    display_extent = [user_point.x - 10000, user_point.x + 10000, user_point.y - 10000, user_point.y + 10000]
    fig = plt.figure(figsize=(3, 3), dpi=300)
    ax = fig.add_subplot(1, 1, 1, projection=crs.OSGB())
    # fig, ax = plt.subplots()

    # plotting all objects
    ax.imshow(background_image, origin='upper', extent=extent, zorder=0)
    rasterio.plot.show(study_area[0], transform=study_area[1], ax=ax, zorder=1, alpha=0.5)
    ax.plot(user_point.x, user_point.y, 'ro',zorder=2, markersize=1)
    ax.plot(highest_elev.x, highest_elev.y, 'go', zorder=3, markersize=1)
    shortest_path_gpd.plot(ax=ax, edgecolor='blue', linewidth=0.5, zorder=4)
    ax.set_extent(display_extent, crs=crs.OSGB())

    # adding map elements


    plt.show()
