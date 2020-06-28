# geospatialAnalysis
After reading some Geospatial Analysis tech articles, I discovered how interactive maps can be built in Python thanks to two amazing libraries: *Geopandas* and *Folium*.<br>
Being a "geography geek" the topic has immediatly caught my interest, so I've started creating my own geospatial visualizations which I collect in this repository<br>

## 1. Topologic-Morphing World: how borders evolved through ages
**GITHUB PAGE:** [topoMorphingWorld](https://hize00.github.io/geospatialAnalysis/topoMorphingWorld.html)<br>
In this visualization we can see how countries borders evolved over time among different ages. Data related to borders were collected from [here](http://web.archive.org/web/20080328104539/http://library.thinkquest.org:80/C006628/download.html) and converted into geojson files with [this tool](https://ogre.adc4gis.com/). As the [disclaimer page](http://web.archive.org/web/20080328161758/http://library.thinkquest.org:80/C006628/disclaimer.html) warns, some of the data are incorrect but anyway I would like to send a big "thank you" to all the students involved in that project.<br>
The cool idea behind this visualization is that we can understand better and easier how borders changed through time and this could be appealing in different areas of study such as history, geography and geo-politics overall.
<br>

## 2. Sic Mundus Est: digital atlas augmented with UN macroeconomic information
I love geography, since I was little I was fascinated by the shapes of countries and the history behind them and their borders. I know by heart the majority of capitals and flags (but I can't remember what I ate last night...) so the creation of a digital Atlas is a project which I found entertaining (Python + Geography: perfect match!)<br>
In order to create a digital Atlas I've downloaded a list of countries capitals with their latitude and longitude and a list of flags. Then I've downloaded the annual sociopolitical report of the United Nations with a list of macroeconomic indexes such as GDP, GDP per capita, International Trade Balance, Education Spendings and many more.<br>
I've preprocessed the data in order to make the countries' names coherent with the countries present in the geojson file. At this point we have 4 datasets:<br>
1. Geojson file of the world
2. Flags files
3. Dataset with countries capitals with latitude and longitude
4. Dataset with macroeconomic indexes
The 4 datasets are connected by the same key, the country name (which the preprocessing phase assured to be equal accross all 4 of them)<br>
The next step is to build visualizations aggregating the data and exploiting *folium* library potentials.<br>

**DIGITAL ATLAS GITHUB PAGE:** [digitalAtlas](https://hize00.github.io/geospatialAnalysis/digitalAtlas.html)<br>
**AUGMENTED ATLAS GITHUB PAGE:** [augmentedAtlas](https://hize00.github.io/geospatialAnalysis/sicMundus.html)<br>

**Data sources**<br>
- Capitals with latitude and longitude: [Kaggle](https://www.kaggle.com/nikitagrec/world-capitals-gps)<br>
- Countries macroeconomic indexes: [Kaggle](https://www.kaggle.com/sudalairajkumar/undata-country-profiles)
- Flags: [Flagpedia](https://flagpedia.net/download) <br>


