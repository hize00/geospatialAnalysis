import base64

import geopandas
import pandas as pd
import numpy as np
import folium
import sys
import os
import config
from branca.element import IFrame

FLAGS_FOLDER = config.FLAGS_FOLDER
RESULT_FOLDER = config.RESULT_FOLDER
countries_csv = config.COUNTRIES_CSV
economics_csv = config.ECONOMICS_CSV

countries_df = pd.read_csv(countries_csv)
economics_df = pd.read_csv(economics_csv)

geojson_currentWorld = geopandas.read_file(config.GEOJSON_NOW)

test_image = '../data/flags/Italy.png'


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


if __name__ == "__main__":
    try:
        # rename_flags()
        m = folium.Map([41, 12], tiles=None, zoom_start=3)
        folium.TileLayer('cartodbpositron', name='Atlantis').add_to(m)
        m.get_root().title = "Atlantis"
        # HTML title
        html_element = """<head>
                      <h3 align="center" style="font-size:14px; background-color: #d4d700">
                      <b>Atlantis - WORK IN PROGRESS</b>
                      </h3>
                      </head>"""
        m.get_root().html.add_child(folium.Element(html_element))

        # TODO get data from pandas df's

        # TODO for each country get data and plot them -
        encode_img = base64.b64encode(open(test_image, 'rb').read())
        html_img = '<img src="data:image/png;base64,{}" resolution="75" width="50" height="25">'.format
        geojson_currentWorld['custom'] = "gang"
        geojson_currentWorld['flag'] = html_img(encode_img.decode('UTF-8'))

        layer = folium.GeoJson(geojson_currentWorld, name='Atlantis', show=False,
                               tooltip=folium.features.GeoJsonTooltip(fields=['name', 'custom', 'flag'], aliases=['COUNTRY', 'yeye', 'FLAG']))
        layer.add_to(m)

        output_path = RESULT_FOLDER + '/atlantis.html'
        m.save(output_path)
        print("Done")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
