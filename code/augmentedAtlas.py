import base64
import traceback
import math
import geopandas
import pandas as pd
import numpy as np
import folium
import sys
import os
import fnmatch
import branca
import vincent
import json
from typing import List
import mapBinder
import config
from folium import GeoJsonPopup

FLAGS_FOLDER = config.FLAGS_FOLDER
RESULT_FOLDER = config.RESULT_FOLDER
countries_csv = config.COUNTRIES_CSV
economics_csv = config.ECONOMICS_CSV
couuntries_geojson_csv = config.GEOJSON_NOW_COUNTRIES_CSV

countries_df = pd.read_csv(countries_csv)
economics_df = pd.read_csv(economics_csv)
# print(economics_df.describe())
# print(economics_df.dtypes)
geojson_currentWorld = geopandas.read_file(config.GEOJSON_NOW)
geojson_currentWorld_head = geojson_currentWorld.head(10)
geojson_currentWorld_countries_df = pd.read_csv(couuntries_geojson_csv)

city_icon = r'../data/city-marker.png'

MACROECONOMIC_INDEXES = ['GDP per capita (current US$)', 'GDP: Gross domestic product (million current US$)',
                         'Economy: Agriculture (% of GVA)', 'Economy: Industry (% of GVA)', 'Economy: Services and other activity (% of GVA)',
                         'International trade: Imports (million US$)', 'International trade: Exports (million US$)',
                         'International trade: Balance (million US$)',
                         'Education: Government expenditure (% of GDP)',
                         'Threatened species (number)', 'CO2 emission estimates (million tons/tons per capita)',
                         'Pop. using improved drinking water (urban/rural, %)', 'Pop. using improved sanitation facilities (urban/rural, %)']

MACROECONOMIC_LAYER_DICT = {
    'SimpleLayer': [
        dict(layer_name='Economy: GDP per capita (US$)',
             df_column_name='GDP per capita (current US$)',
             choropleth_color='YlOrRd',
             legend_color=['white', '#FBFCBF', 'yellow', 'orange', 'red']),
        dict(layer_name='Economy: International trade balance (million US$)',
             df_column_name='International trade: Balance (million US$)',
             choropleth_color='PuRd',
             legend_color=['white', '#e7e1ef', '#c994c7', '#dd1c77', 'purple']),
        dict(layer_name='Environment: C02 emissions (tons)',
             df_column_name='CO2 emission estimates (million tons/tons per capita)',
             choropleth_color='YlGnBu',
             legend_color=['white', '#edf8b1', '#7fcdbb', 'green', 'blue']),
        dict(layer_name='Environment: Threatened Species',
             df_column_name='Threatened species (number)',
             choropleth_color='RdPu',
             legend_color=['white', '#fde0dd', '#fa9fb5', 'purple']),
        dict(layer_name='Education: Government expenditure (% of GDP)',
             df_column_name='Education: Government expenditure (% of GDP)',
             choropleth_color='PuBuGn',
             legend_color=['white', '#ece2f0', '#a6bddb', '#1c9099'])
    ],
    'ComplexLayer': [

    ]
}


def clean_economics_dataframe(dataframe=economics_df):
    """
    Clean the dataframe from non-numeric values in the columns specified which are the ones later analyzed.
    :param dataframe:
    :return:
    """
    # clean string columns
    # dataframe['Forested area (% of land area)'] = dataframe['Forested area (% of land area)'].str.split('/').str[1]

    for column in MACROECONOMIC_INDEXES:
        dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
        dataframe[column].replace(-99, np.nan, inplace=True)

    return dataframe


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
    """
    Extract the value from the dataframe row
    :param df_row:
    :return:
    """
    value = 'N/A'
    if df_row.size > 0:
        value = df_row.values[0]
        if type(value) is not str:
            if math.isnan(value):
                value = 'N/A'
    return value


def create_countries_dict(countries_dataframe):
    """
    Create a dict of dict. Primary Key = CountryName. Inner Keys are the macroeconomic indicator extracted from the df with the corresponding values
    :param countries_dataframe:
    :return:
    """
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
            country_info['population (million)'] = country_population / 1000
        else:
            country_info['population (million)'] = country_population
        country_info['population_density'] = country_density
        country_info['GDP (million $)'] = country_gdp
        country_info['GDP_capita ($)'] = country_gdp_capita
        country_info['flag_image_path'] = flag_image

        data[country_name] = country_info

    return data


def encode_img_for_html(image_path, resolution=75, width=50, height=25):
    """
    Encode the image located at @image_path for html embedding
    :param image_path:
    :param resolution:
    :param width:
    :param height:
    :return:
    """
    encode_img = base64.b64encode(open(image_path, 'rb').read())
    html_img_string = '<img src="data:image/png;base64,{}" resolution="' + str(resolution) + '" width="' + str(width) + '" height="' + str(height) + '">'
    html_img = html_img_string.format
    # html_img = '<img src="data:image/png;base64,{}" resolution="75" width="50" height="25">'.format
    img = html_img(encode_img.decode('UTF-8'))
    return img


def popup_string_creator(country, capital, population, population_density, gdp, gdp_capita, flag_path):
    """
    Encode the information as html string
    :param country:
    :param capital:
    :param population:
    :param population_density:
    :param gdp:
    :param gdp_capita:
    :param flag_path:
    :return:
    """
    if flag_path != '':
        flag_html = encode_img_for_html(flag_path)
    else:
        flag_html = 'N/A'
    popup_string = """
                   <b>COUNTRY:</b> {str1}<br>
                   <b>CAPITAL:</b> {str2}<br>
                   <b>POPULATION (million):</b> {str3}<br>
                   <b>POPULATION DENSITY:</b> {str4}<br>
                   <b>GDP (million $):</b> {str5}<br>
                   <b>GDP PER CAPITA ($):</b> {str6}<br>
                   {str7}
                   """.format(str1=country, str2=capital, str3=str(population),
                              str4=str(population_density), str5=str(gdp), str6=str(gdp_capita), str7=flag_html)

    return popup_string


def delete_folium_choropleth_legend(choropleth: folium.Choropleth):
    """
    A hack to remove choropleth legends. The choropleth color-scaled legend sometimes looks too crowded. Until there is an
    option to disable the legend, use this routine to remove any color map children from the choropleth.

    :param choropleth: Choropleth objected created by `folium.Choropleth()`
    :return: The same object `choropleth` with any child whose name starts with
      'color_map' removed.
    """
    del_list = []
    for child in choropleth._children:
        if child.startswith('color_map'):
            del_list.append(child)
    for del_item in del_list:
        choropleth._children.pop(del_item)
    return choropleth


def create_choropleth_data_layer(layer_name, layer_color, dataframe, dataframe_column_key,
                                 dataframe_column, legend_color, map):
    """
    Create data layer for macroeconomic indexes visualizations
    :param layer_name:
    :param dataframe:
    :param dataframe_column:
    :return:
    """
    data_layer = folium.features.Choropleth(geo_data=geojson_currentWorld, data=dataframe,
                                            columns=dataframe_column_key, key_on='feature.properties.name',
                                            legend_name=layer_name, fill_color=layer_color,
                                            bins=9, nan_fill_color='lightgrey',
                                            fill_opacity=0.7, line_opacity=0.2,
                                            name=layer_name, overlay=True,
                                            highlight=True, show=False)
    # add data to geojson property
    for f in data_layer.geojson.data['features']:
        country = f['properties']['name']
        country_value_df_row = dataframe.loc[dataframe['country'] == country][dataframe_column]
        country_value = extract_df_row_value(country_value_df_row)
        f['properties'][layer_name] = country_value
    # create tooltip
    tooltip_layer_desc = layer_name
    if ':' not in tooltip_layer_desc:
        tooltip_layer_desc = ':' + tooltip_layer_desc
    tooltip_layer_desc = tooltip_layer_desc.split(':')[1]
    folium.GeoJsonTooltip(fields=['name', layer_name], aliases=['COUNTRY', tooltip_layer_desc]).add_to(data_layer.geojson)
    delete_folium_choropleth_legend(data_layer.add_to(m))
    # create colormap
    vmin = min(economics_df[dataframe_column])
    vmax = max(economics_df[dataframe_column])
    layer_legend = branca.colormap.LinearColormap(legend_color, vmin=vmin, vmax=vmax, caption=layer_name)
    # bind colormap with chorpleth_layer
    m.add_child(data_layer)
    m.add_child(layer_legend)
    m.add_child(mapBinder.BindColormap(data_layer, layer_legend))

    return data_layer


def create_industryPie_layer(dataframe):
    layer = folium.GeoJson(geojson_currentWorld, name='Economic Sectors', show=False,
                           style_function=lambda x: {'fillColor': 'yellow', 'color': 'yellow', 'weight': 1},
                           tooltip=folium.features.GeoJsonTooltip(fields=['name'], aliases=['COUNTRY']))

    for country in COUNTRIES_DICT:
        v = None
        lat = COUNTRIES_DICT[country]['capital_latitude']
        long = COUNTRIES_DICT[country]['capital_longitude']
        agriculture_row = dataframe.loc[dataframe['country'] == country]['Economy: Agriculture (% of GVA)']
        agriculture = extract_df_row_value(agriculture_row)
        industry_row = dataframe.loc[dataframe['country'] == country]['Economy: Industry (% of GVA)']
        industry = extract_df_row_value(industry_row)
        services_row = dataframe.loc[dataframe['country'] == country]['Economy: Services and other activity (% of GVA)']
        services = extract_df_row_value(services_row)
        pie_data = {'Agriculture: ' + str(agriculture) + '%': agriculture, 'Industry: ' + str(industry) + '%': industry, 'Services: ' + str(services) + '%': services}
        pie = vincent.Pie(pie_data, outer_radius=50)
        pie.width = 50
        pie.height = 50
        pie.legend('Economic Sectors')
        pie_json_data = json.loads(pie.to_json())
        if lat != 'N/A' and long != 'N/A':
            p = folium.Popup('', max_width=1200)
            v = folium.features.Vega(pie_json_data, width='100%', height='100%')
            p.add_child(v)
            icon = folium.features.CustomIcon(icon_image=city_icon, icon_size=(10, 10))
            folium.Marker(location=(lat, long), tooltip=country, popup=p, icon=icon).add_to(layer)

    return layer


if __name__ == "__main__":
    try:
        # rename_flags()
        economics_df = clean_economics_dataframe()
        m = folium.Map([41, 12], tiles=None, zoom_start=3)
        folium.TileLayer('cartodbpositron', name='World').add_to(m)
        m.get_root().title = "SIC MUNDUS EST"
        # HTML title
        html_element = """<head>
                      <h3 align="center" style="font-size:14px; background-color: #F9B985">
                      <b>SIC MUNDUS EST</b></br>
                      Click on a layer to see macroeconomic data related to countries.<br>
                      Click on markers to see details related to that visualization.<br>
                      <b>NOTE:</b> this project is still work in progress, some refinements are still needed. At the moment it is a draft of the final outcome.<br>
                      <br>
                      <p align="center" style="font-size:10px; background-color: #F7F052"; color: white>Developed by Carlo Leone Fanton - <a href="mailto:carlo.fanton92@gmail.com">Click Here To Email Me</a>
                      </h3>
                      </head>"""
        m.get_root().html.add_child(folium.Element(html_element))

        COUNTRIES_DICT = create_countries_dict(geojson_currentWorld_countries_df)

        atlas_layer = folium.GeoJson(geojson_currentWorld, name='Atlas', show=False,
                                     style_function=lambda x: {'fillColor': '#C60909', 'color': '#C60909', 'weight': 1},
                                     tooltip=folium.features.GeoJsonTooltip(fields=['name'], aliases=['COUNTRY']))

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
                icon = folium.features.CustomIcon(icon_image=city_icon, icon_size=(10, 10))
                folium.Marker(location=(lat, long), tooltip=country, popup=popup, icon=icon).add_to(atlas_layer)
                # folium.CircleMarker(location=(lat, long), tooltip=country, radius=5, weight=3, color='red', fillcolor='red').add_to(m)
        # atlas_layer.add_to(m)

        for layer in MACROECONOMIC_LAYER_DICT['SimpleLayer']:
            layer_name = layer['layer_name']
            column_name = layer['df_column_name']
            column_values = economics_df[column_name]
            choropleth_colors = layer['choropleth_color']
            legend_colors = layer['legend_color']
            choropleth_layer = create_choropleth_data_layer(layer_name, choropleth_colors, economics_df, ['country', column_name],
                                                 column_name,legend_colors, m)

        industryPie_layer = create_industryPie_layer(economics_df)
        industryPie_layer.add_to(m)

        # LAYER CONTROL
        folium.LayerControl(collapsed=False).add_to(m)

        output_path = RESULT_FOLDER + '/sicMundus.html'
        m.save(output_path)
        print("Done")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        traceback.print_exc()
