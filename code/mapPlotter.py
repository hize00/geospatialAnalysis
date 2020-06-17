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

geojsonData_1880 = geopandas.read_file(config.GEOJSON_1880)
geojsonData_1914 = geopandas.read_file(config.GEOJSON_1914)
geojsonData_1920 = geopandas.read_file(config.GEOJSON_1920)
geojsonData_1938 = geopandas.read_file(config.GEOJSON_1938)
geojsonData_1945 = geopandas.read_file(config.GEOJSON_1945)

years = {'Date': ['01-01-1880', '01-01-1914', '01-01-1920', '01-01-1938', '01-01-1945']}
df = pd.DataFrame(years)
df['Date'] = pd.to_datetime(df['Date'])
# print(df)
datetime_index = pd.DatetimeIndex(df['Date'])
dt_index_epochs = datetime_index.astype(int) // 10**9
dt_index = dt_index_epochs.astype('U10')
# print(dt_index)


def create_rgb_colors(color_number):
    HSV_tuples = [(x * 1.0 / color_number, 0.5, 0.5) for x in range(color_number)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    return list(RGB_tuples)


if __name__ == "__main__":
    # 'NAME', 'geometry'
    a = geojsonData_1945.head(10)
    colors = create_rgb_colors(5)

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

    now = datetime.datetime.now()
    m = folium.Map([41, 12], tiles='cartodbpositron', zoom_start=3)

    # folium.LatLngPopup().add_to(m)

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

    folium.LayerControl(collapsed=False).add_to(m)

    output_path = RESULT_FOLDER + '/morphoWorld.html'
    m.save(output_path)

