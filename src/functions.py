import geopandas as gpd
from shapely.geometry import Point
import geoplot as gplt
import matplotlib
provinces_gdf = gpd.read_file("../data/provinces_gdf.geojson", driver='geojson')


def geographic_centroid_gdf(geographic_unit: str, provinces_gdf=provinces_gdf) -> gpd.geodataframe.GeoDataFrame:
    """
    Transforms the original geodataframe into one that has geographic centroids for the given geographic unit.
    The geographic unit will be larger than province.
    -
    Input: 
    geographic_unit: A string specifying the geographic unit, as specified in provinces_gdf
    -
    Output:
    geographic_unit_centroid_gdf: A geodataframe that has a geometry column with geographic centroids.
    """
    # checking that the region is specified correctly
    assert geographic_unit[0].isupper()
    # finding the centroids
    geographic_unit_centroid_gdf = provinces_gdf.dissolve(by=geographic_unit)
    geographic_unit_centroid_gdf['geometry'] = geographic_unit_centroid_gdf['geometry'].centroid
    return geographic_unit_centroid_gdf

def find_weighted_centroids(geographic_unit: str, provinces_gdf=provinces_gdf) -> gpd.geodataframe.GeoDataFrame:
    """
    Transforms the original geodataframe into one that has weighted mean population centroids for the given geographic unit.
    The geographic unit will be larger than province.
    -
    Input: 
    geographic_unit: A string specifying the geographic unit, as specified in provinces_gdf
    -
    Output:
    pop_weighted_centroid_gdf: A geodataframe that has a geometry column with weighted mean population centroids.
    """
    # checking that the region is specified correctly
    assert geographic_unit[0].isupper()
    # finding the geographic unit's population
    geographic_unit_pop_sum = provinces_gdf.groupby(geographic_unit).Population.sum()
    # finding weighted lat and lon for each geographic unit
    provinces_gdf['Weighted_region_centroid_lat'] = [provinces_gdf['Pop_weighted_lat'][x] / \
                                                     geographic_unit_pop_sum[provinces_gdf[geographic_unit][x]] 
                                                    for x in range(len(provinces_gdf))]
    provinces_gdf['Weighted_region_centroid_lon'] = [provinces_gdf['Pop_weighted_lon'][x] / \
                                                     geographic_unit_pop_sum[provinces_gdf[geographic_unit][x]] 
                                                    for x in range(len(provinces_gdf))]
    # sum up all of the weighted coords and recombine
    geographic_unit_coord_sum = provinces_gdf.groupby(geographic_unit) \
                        ['Weighted_region_centroid_lat','Weighted_region_centroid_lon'].sum()
    geographic_unit_coord_sum['Weighted_centroid_coords'] = list(zip(geographic_unit_coord_sum['Weighted_region_centroid_lat'], 
                                                       geographic_unit_coord_sum['Weighted_region_centroid_lon']))
    geographic_unit_coord_sum['geometry'] = [Point(x) for x in geographic_unit_coord_sum['Weighted_centroid_coords']]
    # making it into a geodataframe
    geographic_unit_pop_weighted_gdf = gpd.GeoDataFrame(geographic_unit_coord_sum)
    return geographic_unit_pop_weighted_gdf

def plot_both_centroids(geometries: gpd.geodataframe.GeoDataFrame,
                       geographic_centroids: gpd.geodataframe.GeoDataFrame,
                       population_weighted_centroids: gpd.geodataframe.GeoDataFrame):
# -> matplotlib.axes._subplots.AxesSubplot:
    print("""The green dot(s) represent(s) the weighted mean population centroid 
    while the black dots represent the geographic centroid.""")
    ax = geographic_centroids.plot(color='black', figsize=(5,5))
    population_weighted_centroids.plot(figsize=(5,5), ax=ax, color='green')
    gplt.polyplot(geometries, facecolor='white', edgecolor='grey', ax=ax, figsize=(5,5))
    return ax

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
   