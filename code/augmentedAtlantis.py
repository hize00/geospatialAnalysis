import base64
import traceback
import math
import geopandas
import pandas as pd
import numpy as np
import folium
import sys
import os, fnmatch
import config

FLAGS_FOLDER = config.FLAGS_FOLDER
RESULT_FOLDER = config.RESULT_FOLDER
countries_csv = config.COUNTRIES_CSV
economics_csv = config.ECONOMICS_CSV
couuntries_geojson_csv = config.GEOJSON_NOW_COUNTRIES_CSV

countries_df = pd.read_csv(countries_csv)
economics_df = pd.read_csv(economics_csv)

geojson_currentWorld = geopandas.read_file(config.GEOJSON_NOW)
geojson_currentWorld_countries_df = pd.read_csv(couuntries_geojson_csv)

city_icon = '../data/city-icon.png'


def rename_flags():
    """
    Filename of downloaded flags had country code in it. Rename it with Country Name
    """
    for file in os.listdir(FLAGS_FOLDER):
        file_name = os.path.splitext(file)[0]
        file_extension = os.path.splitext(file)[1]
        flag_row_df = countries_df.loc[countries_df['CountryCode'] == file_name.upper()]['CountryName']
        if flag_row_df.size == 1:
            flag_country = flag_row_df.values[0]
            if flag_country:
                os.rename(os.path.join(FLAGS_FOLDER, file), os.path.join(FLAGS_FOLDER, flag_country + file_extension))


def find_flag_file(pattern, root_path):
    result = ''
    for root, dirs, files in os.walk(root_path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result = os.path.join(root, name)
                # print('File with pattern ' + pattern + ' found')
                break
    return result


def extract_df_row_value(df_row):
    value = 'N/A'
    if df_row.size > 0:
        value = df_row.values[0]
        if type(value) is not str:
            if math.isnan(value):
                value = 'N/A'
    return value


def create_countries_dict(countries_dataframe):
    data = {}
    for country in countries_dataframe.itertuples():
        country_info = {}
        country_name = country.CountryName
        alias = country.Alias
        # print('processing country ' + country_name)
        flag_image = find_flag_file(country_name + '.png', FLAGS_FOLDER)
        if flag_image == '':
            if type(alias) is str:
                # print('Look for flag with country Alias: ' + alias)
                flag_image = find_flag_file(alias + '.png', FLAGS_FOLDER)
        capital_row = countries_df.loc[countries_df['CountryName'] == (country_name or alias)]['CapitalName']
        capital = extract_df_row_value(capital_row)
        capital_lat_row = countries_df.loc[countries_df['CountryName'] == (country_name or alias)]['CapitalLatitude']
        capital_lat = extract_df_row_value(capital_lat_row)
        capital_long_row = countries_df.loc[countries_df['CountryName'] == (country_name or alias)]['CapitalLongitude']
        capital_long = extract_df_row_value(capital_long_row)
        country_population_row = economics_df.loc[economics_df['country'] == (country_name or alias)]['Population in thousands (2017)']
        country_population = extract_df_row_value(country_population_row)
        country_density_row = economics_df.loc[economics_df['country'] == (country_name or alias)]['Population density (per km2, 2017)']
        country_density = extract_df_row_value(country_density_row)
        country_gdp_row = economics_df.loc[economics_df['country'] == (country_name or alias)]['GDP: Gross domestic product (million current US$)']
        country_gdp = extract_df_row_value(country_gdp_row)
        country_gdp_capita_row = economics_df.loc[economics_df['country'] == (country_name or alias)]['GDP per capita (current US$)']
        country_gdp_capita = extract_df_row_value(country_gdp_capita_row)

        country_info['capital'] = capital
        country_info['capital_latitude'] = capital_lat
        country_info['capital_longitude'] = capital_long
        if country_population != 'N/A':
            country_info['population (million)'] = country_population/1000
        else:
            country_info['population (million)'] = country_population
        country_info['population_density'] = country_density
        country_info['GDP (million $)'] = country_gdp
        country_info['GDP_capita ($)'] = country_gdp_capita
        country_info['flag_image_path'] = flag_image

        data[country_name] = country_info

    return data


def encode_img_for_html(image_path, resolution=75, width=50, height=25):
    encode_img = base64.b64encode(open(image_path, 'rb').read())
    html_img_string = '<img src="data:image/png;base64,{}" resolution="' + str(resolution)+'" width="' + str(width) + '" height="' + str(height) + '">'
    html_img = html_img_string.format
    # html_img = '<img src="data:image/png;base64,{}" resolution="75" width="50" height="25">'.format
    img = html_img(encode_img.decode('UTF-8'))
    return img


def popup_string_creator(country, capital, population, population_density, gdp, gdp_capita, flag_path):
    if flag_path != '':
        flag_html = encode_img_for_html(flag_path)
    else:
        flag_html = 'N/A'
    popup_string = """
                   <b>COUNTRY:</b> {str1}<br>
                   <b>CAPITAL:</b> {str2}<br>
                   <b>POPULATION (million):</b> {str3}<br>
                   <b>POPULATION DENSITY:</b> {str4}<br>
                   <b>GDP (million$):</b> {str5}<br>
                   <b>GDP PER CAPITA ($):</b> {str6}<br>
                   {str7}
                   """.format(str1=country, str2=capital, str3=str(population),
                              str4=str(population_density), str5=str(gdp), str6=str(gdp_capita), str7=flag_html)

    return popup_string


if __name__ == "__main__":
    try:
        # rename_flags()
        m = folium.Map([41, 12], tiles=None, zoom_start=3)
        folium.TileLayer('cartodbpositron', name='Atlantis').add_to(m)
        m.get_root().title = "Atlantis"
        # HTML title
        html_element = """<head>
                      <h3 align="center" style="font-size:14px; background-color: #d4d700">
                      <b>Atlantis - WORK IN PROGRESS</b></br>
                      Developer: Carlo Leone Fanton
                      </h3>
                      </head>"""
        m.get_root().html.add_child(folium.Element(html_element))

        COUNTRIES_DICT = create_countries_dict(geojson_currentWorld_countries_df)

        layer = folium.GeoJson(geojson_currentWorld, name='Atlantis', show=False,
                               style_function=lambda x: {'fillColor': '#43aa8b', 'color': '#43aa8b', 'weight': 2},
                               tooltip=folium.features.GeoJsonTooltip(fields=['name'], aliases=['COUNTRY']))

        icon = folium.features.CustomIcon(icon_image=city_icon, icon_size=(14, 14))
        # lat, long, name
        for country in COUNTRIES_DICT:
            capital = COUNTRIES_DICT[country]['capital']
            lat = COUNTRIES_DICT[country]['capital_latitude']
            long = COUNTRIES_DICT[country]['capital_longitude']
            population = COUNTRIES_DICT[country]['population (million)']
            population_density = COUNTRIES_DICT[country]['population_density']
            gdp = COUNTRIES_DICT[country]['GDP (million $)']
            gdp_capita = COUNTRIES_DICT[country]['GDP_capita ($)']
            flag_path = COUNTRIES_DICT[country]['flag_image_path']
            if lat != 'N/A' and long != 'N/A':
                popup_string = popup_string_creator(country, capital, population, population_density, gdp, gdp_capita, flag_path)
                popup = folium.Popup(html=popup_string, max_width=1200)
                folium.Marker(location=(lat, long), tooltip=country, popup=popup).add_to(m)
                #folium.CircleMarker(location=(lat, long), tooltip=country, popup=popup, radius=5, weight=3, color='red', fillcolor='red').add_to(m)

        layer.add_to(m)

        output_path = RESULT_FOLDER + '/atlantis.html'
        m.save(output_path)
        print("Done")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        traceback.print_exc()
