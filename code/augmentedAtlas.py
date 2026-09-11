import traceback
import math
import re
import shutil
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

CITY_ICON_SIZE = 10
CITY_ICON_ACCENT = '#444440'
city_icon = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' "
    "viewBox='0 0 {s} {s}'%3E%3Ccircle cx='{c}' cy='{c}' r='3.5' fill='%23{color}' "
    "stroke='%23ffffff' stroke-width='1.2'/%3E%3C/svg%3E"
).format(s=CITY_ICON_SIZE, c=CITY_ICON_SIZE / 2, color=CITY_ICON_ACCENT.lstrip('#'))

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


def safe_flag_filename(country_name):
    name = re.sub(r'[^A-Za-z0-9_\- ]+', '', country_name).strip()
    return re.sub(r'\s+', '_', name) + '.png'


def flag_relative_path(flag_image_abs_path, country_name):
    """
    Copy the flag image into RESULT_FOLDER/flags so popups can reference it by URL
    instead of embedding it as base64 (keeps the generated HTML small and lets the
    browser cache one flag file across every popup that needs it).
    :param flag_image_abs_path:
    :param country_name:
    :return: path relative to the generated HTML file, or '' if no flag was found
    """
    if not flag_image_abs_path:
        return ''
    flags_out_dir = os.path.join(RESULT_FOLDER, 'flags')
    os.makedirs(flags_out_dir, exist_ok=True)
    fname = safe_flag_filename(country_name)
    dest = os.path.join(flags_out_dir, fname)
    if not os.path.exists(dest):
        shutil.copyfile(flag_image_abs_path, dest)
    return 'flags/' + fname


def format_number(value, decimals=0):
    """
    Format a numeric value with thousands separators, or None if it's missing/non-numeric.
    """
    if value is None or value == 'N/A':
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)
    return '{:,.{}f}'.format(value, decimals)


def format_population(value_millions):
    """
    Format a population expressed in millions:
    - under 1M: show in thousands, e.g. 850K
    - 1M-10M: 2 decimals, e.g. 2.25M (1 decimal would round too coarsely at this scale)
    - 10M and up: 1 decimal, e.g. 59.4M
    """
    if value_millions is None or value_millions == 'N/A':
        return None
    try:
        value_millions = float(value_millions)
    except (TypeError, ValueError):
        return str(value_millions)
    if value_millions < 1:
        return '{:,.0f}K'.format(value_millions * 1000)
    if value_millions < 10:
        return '{:,.2f}M'.format(value_millions)
    return '{:,.1f}M'.format(value_millions)


def popup_string_creator(country, capital, population, population_density, gdp, gdp_capita, flag_path):
    """
    Build a compact popup card (flag, capital, stat grid) matching the site's dark theme,
    instead of a flat key/value list with a base64-embedded flag.
    :param country:
    :param capital:
    :param population:
    :param population_density:
    :param gdp:
    :param gdp_capita:
    :param flag_path:
    :return:
    """
    flag_rel = flag_relative_path(flag_path, country)
    if flag_rel:
        flag_html = '<img class="mundus-flag" src="{}" alt="{} flag" loading="lazy">'.format(flag_rel, country)
    else:
        flag_html = '<div class="mundus-flag mundus-flag-empty"></div>'

    capital_line = capital if capital and capital != 'N/A' else 'Capital unknown'

    stats = [
        ('Population', format_population(population), ''),
        ('Density', format_number(population_density, 1), '/km&sup2;'),
        ('GDP', format_number(gdp, 0), 'M$'),
        ('GDP / capita', format_number(gdp_capita, 0), '$'),
    ]
    stats_html = ''.join(
        '<div class="mundus-stat"><span class="mundus-stat-label">{}</span>'
        '<span class="mundus-stat-value">{}{}</span></div>'.format(label, value, unit)
        for label, value, unit in stats if value is not None
    )

    popup_string = (
        '<div class="mundus-popup">'
        '<div class="mundus-popup-head">{flag}'
        '<div class="mundus-popup-heading"><div class="mundus-country">{country}</div>'
        '<div class="mundus-capital">{capital}</div></div></div>'
        '<div class="mundus-stats">{stats}</div>'
        '</div>'
    ).format(flag=flag_html, country=country, capital=capital_line, stats=stats_html)

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
                           style_function=lambda x: {'color': '#8a8a86', 'fillColor': '#000000',
                                                      'weight': 0.6, 'opacity': 0.25, 'fillOpacity': 0.03},
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
            icon = folium.features.CustomIcon(icon_image=city_icon, icon_size=(CITY_ICON_SIZE, CITY_ICON_SIZE),
                                              icon_anchor=(CITY_ICON_SIZE // 2, CITY_ICON_SIZE // 2))
            folium.Marker(location=(lat, long), tooltip=country, popup=p, icon=icon).add_to(layer)

    return layer


if __name__ == "__main__":
    try:
        # rename_flags()
        economics_df = clean_economics_dataframe()
        m = folium.Map([41, 12], tiles=None, zoom_start=3)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri — Esri, HERE, Garmin, &copy; OpenStreetMap contributors, and the GIS user community',
            max_zoom=16,
            name='World').add_to(m)
        m.get_root().title = "SIC MUNDUS EST"
        # HTML title: glass-panel header injected into <head> (styles) and <body> (markup)
        head_element = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    :root{ --glow-bg: rgba(17,24,39,.72); --glow-border: rgba(255,255,255,.14); --glow-accent: #c60909; --glow-text: #f4f6fb; --glow-muted: #b7c0d8; }
    .glow-panel{position:fixed;top:16px;left:16px;z-index:1000;max-width:380px;background:var(--glow-bg);border:1px solid var(--glow-border);border-radius:14px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 12px 32px rgba(0,0,0,.35);color:var(--glow-text);font-family:'Inter',-apple-system,sans-serif;transition:all .25s ease;overflow:hidden;}
    .glow-panel.collapsed .glow-body{display:none;}
    .glow-panel-head{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:12px 14px;cursor:pointer;border-bottom:1px solid transparent;}
    .glow-panel:not(.collapsed) .glow-panel-head{border-bottom-color:var(--glow-border);}
    .glow-title{font-size:15px;font-weight:700;letter-spacing:.2px;margin:0;}
    .glow-accent{color:var(--glow-accent);}
    .glow-toggle{background:none;border:none;color:var(--glow-muted);font-size:16px;cursor:pointer;line-height:1;padding:2px 4px;}
    .glow-body{padding:4px 14px 12px;font-size:12.5px;line-height:1.5;color:var(--glow-muted);}
    .glow-body b{color:var(--glow-text);}
    .glow-body a{color:var(--glow-accent);}
    .glow-hub-link{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:var(--glow-muted);text-decoration:none;padding:10px 14px 0;}
    .glow-hub-link:hover{color:var(--glow-text);}
    .glow-footer{margin-top:10px;padding-top:8px;border-top:1px solid var(--glow-border);font-size:10.5px;color:var(--glow-muted);}
    .glow-footer a{color:var(--glow-accent);text-decoration:none;}
    .glow-footer a:hover{text-decoration:underline;}
    @media (max-width:520px){.glow-panel{left:8px;right:8px;top:8px;max-width:none;}}
    .legend{background:var(--glow-bg) !important;border:1px solid var(--glow-border) !important;border-radius:10px !important;padding:8px 14px 4px !important;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 8px 24px rgba(0,0,0,.3) !important;}
    .legend .caption{fill:var(--glow-text) !important;font-family:'Inter',-apple-system,sans-serif !important;font-size:11px !important;}
    .legend .tick text{fill:var(--glow-muted) !important;font-family:'Inter',-apple-system,sans-serif !important;font-size:10px !important;}
    .legend .tick line{stroke:var(--glow-border) !important;}
    .legend path.domain{stroke:var(--glow-border) !important;}
    .leaflet-popup-content-wrapper{background:var(--glow-bg);color:var(--glow-text);border:1px solid var(--glow-border);border-radius:12px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 12px 32px rgba(0,0,0,.35);}
    .leaflet-popup-tip{background:rgba(17,24,39,.85);}
    .leaflet-popup-content{margin:0;}
    .leaflet-popup-close-button{color:var(--glow-muted) !important;}
    .mundus-popup{font-family:'Inter',-apple-system,sans-serif;padding:12px 14px;min-width:200px;}
    .mundus-popup-head{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
    .mundus-flag{width:36px;height:24px;object-fit:cover;border-radius:3px;border:1px solid var(--glow-border);flex-shrink:0;}
    .mundus-flag-empty{width:36px;height:24px;border-radius:3px;border:1px dashed var(--glow-border);flex-shrink:0;}
    .mundus-country{font-size:14px;font-weight:700;color:var(--glow-text);line-height:1.25;}
    .mundus-capital{font-size:11.5px;color:var(--glow-muted);}
    .mundus-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;}
    .mundus-stat{display:flex;flex-direction:column;gap:1px;}
    .mundus-stat-label{font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:var(--glow-muted);}
    .mundus-stat-value{font-size:13px;font-weight:600;color:var(--glow-text);}
</style>"""
        m.get_root().header.add_child(folium.Element(head_element))

        body_element = """
<div class="glow-panel" id="glowPanel">
    <a class="glow-hub-link" href="index.html">&larr; All visualizations</a>
    <div class="glow-panel-head" onclick="var p=this.parentElement;p.classList.toggle('collapsed');this.querySelector('.glow-toggle').textContent=p.classList.contains('collapsed')?'+':'−';">
        <p class="glow-title">Sic <span class="glow-accent">Mundus</span> Est</p>
        <button class="glow-toggle" aria-label="toggle">&minus;</button>
    </div>
    <div class="glow-body">
        Toggle a macroeconomic <b>layer</b> to color the world by that metric, then click a marker for the full country breakdown.
        <br><br>
        <span style="opacity:.8">Work in progress &mdash; some layers are still rough drafts.</span>
    </div>
</div>"""
        m.get_root().html.add_child(folium.Element(body_element))

        # Move the zoom control out from under the glass header panel (top-left) to bottom-left.
        zoom_position_script = """
(function(){
    function init(){
        for (var k in window) {
            if (/^map_/.test(k) && window[k] && window[k].zoomControl) {
                window[k].zoomControl.setPosition('bottomleft');
            }
        }
    }
    if (document.readyState === 'complete') { setTimeout(init, 0); }
    else { window.addEventListener('load', init); }
})();
"""
        m.get_root().script.add_child(folium.Element(zoom_position_script))

        COUNTRIES_DICT = create_countries_dict(geojson_currentWorld_countries_df)

        atlas_layer = folium.GeoJson(geojson_currentWorld, name='Atlas', show=False,
                                     style_function=lambda x: {'color': '#8a8a86', 'fillColor': '#000000',
                                                                'weight': 0.6, 'opacity': 0.25, 'fillOpacity': 0.03},
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
                icon = folium.features.CustomIcon(icon_image=city_icon, icon_size=(CITY_ICON_SIZE, CITY_ICON_SIZE),
                                              icon_anchor=(CITY_ICON_SIZE // 2, CITY_ICON_SIZE // 2))
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
