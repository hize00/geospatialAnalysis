import geopandas
import folium
import sys
import os
import config

RESULT_FOLDER = config.RESULT_FOLDER

geojsonData_2000bc = geopandas.read_file(config.GEOJSON_2000BC)
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

GEOJSONS = {'2000BC': geojsonData_2000bc,
            '323BC': geojsonData_323bc,
            '200BC': geojsonData_200bc,
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

GEOJSONS_SORTED = sorted(GEOJSONS, key=lambda x: int(x) if 'BC' not in x else int(x.replace('BC', ''))*-1)
# GEOJSONS_SORTED = sorted(GEOJSONS, key=lambda x: int(x))


def simple_rounding(x):
    i, f = divmod(x, 1)
    return int(i + ((f >= 0.5) if (x > 0) else (f > 0.5)))


if __name__ == "__main__":
    try:
        # Palettes: blue - red - green
        colors = ['#80ffdb', '#72efdd', '#64dfdf', '#56cfe1', '#48bfe3', '#4ea8de', '#5390d9', '#5e60ce', '#6930c3', '#7400b8',
                  '#ffff3f', '#eeef20', '#ffba08', '#faa307', '#f48c06', '#e85d04', '#dc2f02', '#d00000', '#9d0208', '#6a040f',
                  '#dddf00', '#d4d700', '#bfd200', '#aacc00', '#80b918', '#55a630', '#2b9348', '#007f5f']
        styles = []
        for c in colors:
            style = {'fillColor': c, 'color': c}
            styles.append(style)

        delta_idx_color = 1
        if len(GEOJSONS) < len(colors):
            delta_idx_color = len(colors) / len(GEOJSONS)
        else:
            print("WARNING: you are trying to plot a higher number of maps with respect to the number of colors provided. Some colors will be repeated")

        m = folium.Map([41, 12], tiles=None, zoom_start=3)
        folium.TileLayer('cartodbpositron', name='Modern World').add_to(m)
        m.get_root().title = "MorphoWorld"
        # HTML title
        html_element = """<head>
                          <h3 align="center" style="font-size:12px; background-color: #d4d700">
                          <b>Interactive world map among various ages, click on one year to see the related world boundaries.<br>
                          Ages have been divided in 3 color palettes: Blue [up to year 1000], Red [up to year 1880] and Green [XXth century]</b><br>
                          DISCLAIMER: The GIS data presented in this site was hand-created by students and as such is not guaranteed to be accurate. It is estimated that political boundaries have an average error of 40 miles<br>
                          Maps DataSource: <a href="http://web.archive.org/web/20080328104539/http://library.thinkquest.org:80/C006628/download.html/"> Link </a>
                          <p align="center" style="font-size:10px; background-color: #aacc00"; color: white>Developed by Carlo Leone Fanton - <a href="mailto:carlo.fanton92@gmail.com">Click Here To Email Me</a>
                          </h3>
                          </head>"""
        m.get_root().html.add_child(folium.Element(html_element))

        for idx, key in enumerate(GEOJSONS_SORTED):
            color_idx = simple_rounding(delta_idx_color * idx)
            if color_idx >= len(colors):
                color_idx = idx
            styleColor = styles[color_idx]
            # careful about late binding
            layer = folium.GeoJson(GEOJSONS[key], name=key, style_function=lambda x, styleColor=styleColor: styleColor, show=False,
                                   tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], aliases=['COUNTRY']))
            layer.add_to(m)
            print('Added layer ' + key + ' with color ' + colors[color_idx])

        folium.LayerControl(collapsed=False).add_to(m)

        output_path = RESULT_FOLDER + '/morphoWorld.html'
        m.save(output_path)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)


