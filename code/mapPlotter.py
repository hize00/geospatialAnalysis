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
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri — Esri, HERE, Garmin, &copy; OpenStreetMap contributors, and the GIS user community',
            max_zoom=16,
            name='Modern World').add_to(m)
        m.get_root().title = "MorphoWorld"
        # HTML title: glass-panel header injected into <head> (styles) and <body> (markup)
        head_element = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    :root{ --glow-bg: rgba(17,24,39,.72); --glow-border: rgba(255,255,255,.14); --glow-accent: #d4d700; --glow-text: #f4f6fb; --glow-muted: #b7c0d8; }
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
    .glow-slider-bar{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:1000;display:flex;align-items:center;gap:10px;background:var(--glow-bg);border:1px solid var(--glow-border);border-radius:12px;padding:8px 14px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 8px 24px rgba(0,0,0,.3);font-family:'Inter',-apple-system,sans-serif;font-size:12.5px;color:var(--glow-text);}
    .glow-slider-btn{background:none;border:1px solid var(--glow-border);border-radius:6px;width:24px;height:24px;cursor:pointer;font-size:13px;color:var(--glow-text);display:flex;align-items:center;justify-content:center;line-height:1;}
    .glow-slider-btn:hover{background:rgba(255,255,255,.08);}
    #glowYearSlider{width:200px;accent-color:var(--glow-accent);}
    .glow-slider-year{font-weight:700;min-width:56px;text-align:center;}
    @media (max-width:560px){.glow-slider-bar{left:8px;right:8px;transform:none;}#glowYearSlider{flex:1;width:auto;}}
</style>"""
        m.get_root().header.add_child(folium.Element(head_element))

        body_element = """
<div class="glow-panel" id="glowPanel">
    <a class="glow-hub-link" href="index.html">&larr; All visualizations</a>
    <div class="glow-panel-head" onclick="var p=this.parentElement;p.classList.toggle('collapsed');this.querySelector('.glow-toggle').textContent=p.classList.contains('collapsed')?'+':'−';">
        <p class="glow-title">Morpho<span class="glow-accent">World</span></p>
        <button class="glow-toggle" aria-label="toggle">&minus;</button>
    </div>
    <div class="glow-body">
        Click a year in the layers panel to reveal that era's <b>world borders</b>. Palettes group ages: <b>Blue</b> (through 1000), <b>Red</b> (through 1880), <b>Green</b> (20th century).
        <br><br>
        <span style="opacity:.8">Border data hand-digitized by ThinkQuest students &mdash; expect ~40mi of error. <a href="http://web.archive.org/web/20080328104539/http://library.thinkquest.org:80/C006628/download.html/">Source</a></span>
    </div>
</div>

<div class="glow-slider-bar" id="glowSliderBar" hidden>
    <button class="glow-slider-btn" id="glowPrev" aria-label="previous era">&larr;</button>
    <input type="range" id="glowYearSlider" min="0" max="0" step="1" value="0">
    <button class="glow-slider-btn" id="glowNext" aria-label="next era">&rarr;</button>
    <span class="glow-slider-year" id="glowYearLabel"></span>
</div>"""
        m.get_root().html.add_child(folium.Element(body_element))

        slider_script = """
(function(){
    function findByPrefix(prefix){
        for (var k in window) {
            if (Object.prototype.hasOwnProperty.call(window, k) && k.indexOf(prefix) === 0) return window[k];
        }
        return null;
    }
    function init(){
        var layerControl = findByPrefix('layer_control_');
        var map = findByPrefix('map_');
        if (!layerControl || !layerControl.overlays || !map || typeof map.addLayer !== 'function') return;

        var years = Object.keys(layerControl.overlays);
        if (!years.length) return;
        years.sort(function(a, b){
            function val(y){ return y.indexOf('BC') !== -1 ? -parseInt(y.replace('BC', ''), 10) : parseInt(y, 10); }
            return val(a) - val(b);
        });

        var bar = document.getElementById('glowSliderBar');
        var slider = document.getElementById('glowYearSlider');
        var label = document.getElementById('glowYearLabel');
        var prevBtn = document.getElementById('glowPrev');
        var nextBtn = document.getElementById('glowNext');

        slider.max = years.length - 1;

        function show(idx){
            idx = Math.max(0, Math.min(years.length - 1, idx));
            years.forEach(function(year, i){
                var layer = layerControl.overlays[year];
                if (i === idx) {
                    if (!map.hasLayer(layer)) map.addLayer(layer);
                } else if (map.hasLayer(layer)) {
                    map.removeLayer(layer);
                }
            });
            slider.value = idx;
            label.textContent = years[idx];
        }

        slider.addEventListener('input', function(e){ show(parseInt(e.target.value, 10)); });
        prevBtn.addEventListener('click', function(){ show(parseInt(slider.value, 10) - 1); });
        nextBtn.addEventListener('click', function(){ show(parseInt(slider.value, 10) + 1); });

        bar.hidden = false;
        show(0);
    }
    if (document.readyState === 'complete') { setTimeout(init, 0); }
    else { window.addEventListener('load', init); }
})();
"""
        m.get_root().script.add_child(folium.Element(slider_script))

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


