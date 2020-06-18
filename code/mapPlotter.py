import pandas as pd
import numpy as np
import geopandas
import folium
from folium.plugins import TimeSliderChoropleth, HeatMapWithTime
import matplotlib
import datetime
import colorsys
import config

RESULT_FOLDER = config.RESULT_FOLDER

geojsonData_323bc = geopandas.read_file(config.GEOJSON_323BC)
geojsonData_200bc = geopandas.read_file(config.GEOJSON_200BC)
geojsonData_1bc = geopandas.read_file(config.GEOJSON_1BC)
geojsonData_400 = geopandas.read_file(config.GEOJSON_400)
geojsonData_800 = geopandas.read_file(config.GEOJSON_800)
geojsonData_1000 = geopandas.read_file(config.GEOJSON_1000)
geojsonData_1279 = geopandas.read_file(config.GEOJSON_1279)
geojsonData_1492 = geopandas.read_file(config.GEOJSON_1492)
geojsonData_1530 = geopandas.read_file(config.GEOJSON_1530)
geojsonData_1650 = geopandas.read_file(config.GEOJSON_1650)
geojsonData_1715 = geopandas.read_file(config.GEOJSON_1715)
geojsonData_1783 = geopandas.read_file(config.GEOJSON_1783)
geojsonData_1880 = geopandas.read_file(config.GEOJSON_1880)
geojsonData_1914 = geopandas.read_file(config.GEOJSON_1914)
geojsonData_1920 = geopandas.read_file(config.GEOJSON_1920)
geojsonData_1938 = geopandas.read_file(config.GEOJSON_1938)
geojsonData_1945 = geopandas.read_file(config.GEOJSON_1945)
geojsonData_1994 = geopandas.read_file(config.GEOJSON_1994)

GEOJSONS = {'-323': geojsonData_323bc,
            '-200': geojsonData_200bc,
            '0': geojsonData_1bc,
            '400': geojsonData_400,
            '800': geojsonData_800,
            '1000': geojsonData_1000,
            '1279': geojsonData_1279,
            '1492': geojsonData_1492,
            '1650': geojsonData_1650,
            '1715': geojsonData_1715,
            '1783': geojsonData_1783,
            '1880': geojsonData_1880,
            '1914': geojsonData_1914,
            '1920': geojsonData_1920,
            '1938': geojsonData_1938,
            '1945': geojsonData_1945,
            '1994': geojsonData_1994}

GEOJSONS_SORTED = sorted(GEOJSONS, key=lambda x: int(x))


if __name__ == "__main__":
    try:
        # 'NAME', 'geometry'
        a = geojsonData_1945.head(10)
        # Palettes: blue - red - green
        colors = ['#80ffdb', '#72efdd', '#64dfdf', '#56cfe1', '#48bfe3', '#4ea8de', '#5390d9', '#5e60ce', '#6930c3', '#7400b8',
                  #'#ffba08', '#faa307', '#f48c06', '#e85d04', '#dc2f02', '#d00000', '#9d0208', '#6a040f',
                  '#ffba08', '#faa307', '#f48c06', '#e85d04', '#dc2f02', '#d00000', 'pink', '#6a040f',
                  '#ffff3f', '#eeef20', '#dddf00', '#d4d700', '#bfd200', '#aacc00', '#80b918', '#55a630', '#2b9348', '#007f5f']
        styles = []
        for c in colors:
            style = {'fillColor': c, 'color': c}
            styles.append(style)

        m = folium.Map([41, 12], tiles='cartodbpositron', zoom_start=3)

        for idx, key in enumerate(GEOJSONS_SORTED):
            folium.GeoJson(GEOJSONS[key], name=key, style_function=lambda x: styles[idx], show=False,
                           tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], aliases=['COUNTRY'])).add_to(m)
            print('Added map ' + key + ' with color ' + colors[idx])

        folium.LayerControl(collapsed=False).add_to(m)

        output_path = RESULT_FOLDER + '/morphoWorld.html'
        m.save(output_path)

        """   
        styles = [{'fillColor': '#FFBA08', 'color': '#FFBA08'},
                  {'fillColor': '#FAA307', 'color': '#FAA307'},
                  {'fillColor': '#F48C06', 'color': '#F48C06'},
                  {'fillColor': '#E85D04', 'color': '#E85D04'},
                  {'fillColor': '#DC2F02', 'color': '#DC2F02'},
                  {'fillColor': '#D00000', 'color': '#D00000'},
                  {'fillColor': '#9D0208', 'color': '#9D0208'},
                  {'fillColor': '#6A040F', 'color': '#6A040F'},
                  {'fillColor': '#370617', 'color': '#370617'},
                  {'fillColor': '#03071E', 'color': '#03071E'}
                  ]
    
        folium.GeoJson(geojsonData_1880, name='1880', style_function=lambda x: styles[0], show=False,
                       tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], aliases=['COUNTRY'])).add_to(m)
        folium.GeoJson(geojsonData_1914, name='1914', style_function=lambda x: styles[1], show=False,
                       tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], aliases=['COUNTRY'])).add_to(m)
        folium.GeoJson(geojsonData_1920, name='1920', style_function=lambda x: styles[2], show=False,
                       tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], aliases=['COUNTRY'])).add_to(m)
        folium.GeoJson(geojsonData_1938, name='1938', style_function=lambda x: styles[3], show=False,
                       tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], aliases=['COUNTRY'])).add_to(m)
        folium.GeoJson(geojsonData_1945, name='1945', style_function=lambda x: styles[4], show=False,
                       tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], aliases=['COUNTRY'])).add_to(m)
        """
    except Exception as e:
        print("\n---Exception occurred---\n")
        print(e)


