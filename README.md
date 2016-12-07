# Map Visualization of Large Data in Python :alien:

##### CIS5930 - Python Programming at Florida State University.
##### Adam Stallard and Eric Serbousek
##### Fall 2016


## Requirements
* python 3
* [flask](http://flask.pocoo.org/)
* [numpy](http://www.numpy.org/)
* [scipy](https://www.scipy.org/install.html)
* ~~[shapely](https://pypi.python.org/pypi/Shapely/)~~
* all-in-one: ```pip install -r requirements.txt```
  * Scipy depends on numpy. This command fails if attempting to install both simultaneously.
  * You might be ok by running it twice. Otherwise `pip install` them individually.
  * If you are on Windows, please consider using Anaconda. Installing dependencies will be much easier!
  * Libraries must correspond to the correct version of python you use!

* ~~If you have trouble installing shapely, here is what I have done on my CentOS7 machine:~~

Leaving this below for reference. Shapely was removed as a dependency because it was only used to parse WKT.
Since our data source has only one WKT formatted string, we just used regex.

```shell
sudo su -  
cd /path/to/downloads  
wget http://download.osgeo.org/geos/geos-3.5.0.tar.bz2  
tar xvf geos-3.5.0.tar.bz2  
cd geos-3.5.0  
./configure --prefix=/usr/local  
make && make install -j2  
export LD_LIBRARY_PATH=/path/to/configure/prefix/lib:$LD_LIBRARY_PATH  
```
* `/path/to/configure/prefix` is the path used by `configure` to install geos ^^^  
* Setting this variable is considered bad practice and it will not persist across shells.  
* For a better solution see [this stack post](http://stackoverflow.com/questions/1099981/why-cant-python-find-shared-objects-that-are-in-directories-in-sys-path/1100297#1100297)


## Running
* Initialize the enviornment (note for windows, use `set` instead of `export`):

NOTE: This was how we originally ran the app. Now we explicitly launch in main. See the second code block below.
```shell
export FLASK_APP=main.py  
cd /path/to/python_web_app/samos_map  
flask run &
```
```shell
cd /path/to/python_web_app/samos_map  
[nohup] python main.py [-h] [-p 5000] [-l 1000000] [&]
```


* ~~The default port for flask is 5000. Change this by passing `-p {port}` when calling `flask run`~~
* ~~Open your browser and go to `http://localhost:5000/`~~
* ~~Any additional proxy will route to a 404 page. Ex: `http://localhost:5000/kshdfkhasd`~~

Previously we tested on local host but the server uses an Apache proxy to reroute /map to port 5000.
Because of this, we have hard coded various url resources in the index.html file so that they go through the proxy.

## About
### OSM - [OpenStreetMap](https://www.openstreetmap.org/)
### DOMS - [Distributed Oceanographic Matchup Service](https://doms.jpl.nasa.gov/)
### EDGE - [The Extensible Data Gateway Environment](https://github.com/dataplumber/edge)
### Solr - [Apache - Lucene - Solr](https://doms.jpl.nasa.gov/)
### SAMOS - [Shipboard Automated Meteorological and Oceanographic System](http://samos.coaps.fsu.edu/html/)
### ICOADS - [International Comprehensive Ocean-Atmosphere Data Set](http://icoads.noaa.gov/)
### SPURS - [Salinity Processes in the Upper Ocean Regional Study](http://spurs.jpl.nasa.gov/)

Open Street Maps is a crowd sourced free map of the world. While they have their own webpage with large map data, it provides mainly land based data withg the exception of coast lines. We would like to map out mainly ocean based data, with the eventual addition of satelitte data (both land + ocean). In order to do this, we plan on using the OSM API which will provide us with a base layer of our map. There are certainly other tools to do this, but using OSM provides an extensible set of features that are simple to work with, and will allow us to overlay our own datasets onto this map in conjuction with what OSM provides.

DOMS is a separate project that aims to provide a central interface to request matched data from a distribution of sources. The match happens on time AND space. This project is currently in development between FSU (tallahassee, FL), JPL (Pasadena, California), and NCAR (Boulder, Colorado). Each of these endpoints have an instance of Apache Solr loaded with very large oceanographic-atmoshperic data sets. EDGE acts as a proxy or communication tool between the central node at JPL, and all distributed nodes. The endpoints are public access and provide a means of extracting data via RESTful URL query strings that are relayed to Solr on the local host. The response from Solr is then relayed back to the user in a simplified JSON format.

For this project, we are taking advantage of these access points for our map visualization. The current implementation only supports extraction from SAMOS, as we have full control over this endpoint. Once this project becomes stable, we will consider adding the other sources as optional layers / feature maps to our tool. Since the protocol on all endpoints is the same (EDGE), this should be a relatively simple update, however it will require much more processing power as these datasets are very large.


## TO-DO
- [x] Add requirements to README
- [x] Add setup / run to README
- [x] Add information about datasets to README
- [x] Add info about openstreetmaps to README
- [x] Add info about EDGE / DOMS / SAMOS to README
- [x] ~~Relay client zoom state (bounding box) to server~~ # zoom events handled on client
- [x] Cluster data extracted from the KDTree # handled via javascript on client
- [ ] Compress clustered data for smaller server->client packet sizes
- [ ] Decompress data on client side (via JS?)
- [ ] ~~Distinguish clusters on client side (JS?)~~
- [x] Populate map on client side (JS?)
- [x] Have a drink


## Future Work
Once everything is stable and working, we would like to incorporate the ability to provide a moving map based on time. Since the data set provided are all spatial-temporal, the actual data points on a static page will represent tracks of data. If we pass time values with our data points, the renderer should be able to show moving objects in the ocean as a function of time. For our protoype (and for the purposes of this as a class project) this will not be incorporated.

Another excellent feature would be to overlay pre computed base tile layers with full ship tracks to be loaded in place of that which is provided by OSM. This would allow the user to see the general tracks of the ship without being confused by the clusters. This would require heavy processing, but only a single pass. Then the client could load tile layers directly from the server instead.

It seems that some of the clustering features provided by leaflet are a little funky on the front end, such as when zooming out some of the markers get pasted to the map and never go away. This doesn't seem to affect the workflow too bad for now, so it is not a huge issue.

As for compression, we never got a chance to toy with the idea, but it may improve the speed of transfer to the client when a point set is large (> ~5000 ?).

Finally, there may some advantage to reworking client server interaction after a user has been on the page for some time. This may be some form of caching or something else entirely, but it may be worth looking into.


## References for AJAX <-> Flask communication
* http://code.runnable.com/UiPhLHanceFYAAAP/how-to-perform-ajax-in-flask-for-python
* http://www.giantflyingsaucer.com/blog/?p=4310
