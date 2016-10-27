# Map Visualization of Large Data in Python :alien:

##### CIS5930 - Python Programming at Florida State University.
##### Adam Stallard and Eric Serbousek
##### Fall 2016


## Requirements
* python 2 | 3
* [flask](http://flask.pocoo.org/)
* [numpy](http://www.numpy.org/)
* [scipy](https://www.scipy.org/install.html)
* [shapely](https://pypi.python.org/pypi/Shapely/)
* all-in-one: ```pip install -r requirements.txt```
  * Scipy depends on numpy. This command fails if attempting to install both simultaneously.
  * You might be ok by running it twice. Otherwise `pip install` them individually.
* NOTE: If you are on Windows, please consider using Anaconda. Installing dependencies will be much easier!
* NOTE: libraries must correspond to the correct version of python you use!
* NOTE: if you have trouble installing shapely, here is what I have done on my CentOS7 machine:

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
* NOTE: `/path/to/configure/prefix` is the path used by `configure` to install geos ^^^  
* NOTE: Setting this variable is considered bad practice and it will not persist across shells.  
* NOTE: For a better solution see [this stack post](http://stackoverflow.com/questions/1099981/why-cant-python-find-shared-objects-that-are-in-directories-in-sys-path/1100297#1100297)


## Running
* Initialize the enviornment (note for windows, use `set` instead of `export`):

```shell
export FLASK_APP=main.py  
cd /path/to/python_web_app/samos_map  
flask run &
```

* The default port for flask is 5000. Change this by passing `-p {port}` when calling `flask run` 
* Open your browser and go to `http://localhost:5000/`
* Any additional proxy will route to a 404 page. Ex: `http://localhost:5000/kshdfkhasd`

## About
### DOMS
See [Distributed Oceanographic Matchup Service](https://doms.jpl.nasa.gov/)
### EDGE
See [The Extensible Data Gateway Environment](https://github.com/dataplumber/edge)
### Solr
See [Apache - Lucene - Solr](https://doms.jpl.nasa.gov/)
### SAMOS
See [Shipboard Automated Meteorological and Oceanographic System](http://samos.coaps.fsu.edu/html/)
### ICOADS
See [Internation Comprehensive Ocean-Atmosphere Data Set](http://icoads.noaa.gov/)
### SPURS
See [Salinity Processes in the Upper Ocean Regional Study](http://spurs.jpl.nasa.gov/)

DOMS is a separate project that aims to provide a central interface to request matched data from a distribution of sources. The match happens on time AND space. This project is currently in development between FSU (tallahassee, FL), JPL (Pasadena, California), and NCAR (Boulder, Colorado). Each of these endpoints have an instance of Apache Solr loaded with very large oceanographic-atmoshperic data sets. EDGE acts as a proxy or communication tool between the central node at JPL, and all distributed nodes. The endpoints are public access and provide a means of extracting data via RESTful URL query strings that are relayed to Solr on the local host. The response from Solr is then relayed back to the user in a simplified JSON format.

For this project, we are taking advantage of these access points for our map visualization. The current implementation only supports extraction from SAMOS, as we have full control over this endpoint. Once this project becomes stable, we will consider adding the other sources as optional layers / feature maps to our tool. Since the protocol on all endpoints is the same (EDGE), this should be a relatively simple update, however it will require much more processing power as these datasets are very large.


## TO-DO
- [x] Add requirements to README
- [x] Add setup / run to README
- [ ] Add information about datasets to README
- [ ] Add info about openstreetmaps to README
- [ ] Add info about EDGE / DOMS / SAMOS to README
- [ ] Relay client zoom state (bounding box) to server
- [ ] Cluster data extracted from the KDTree
- [ ] Compress clustered data for smaller server->client packet sizes
- [ ] Decompress data on client side (via JS?)
- [ ] Distinguish clusters on client side (JS?)
- [ ] Populate map on client side (JS?)
- [ ] Add diagrams so people know what the hell we are talking about :joy:
- [ ] Have a drink


##References for AJAX<->Flask
http://code.runnable.com/UiPhLHanceFYAAAP/how-to-perform-ajax-in-flask-for-python

http://www.giantflyingsaucer.com/blog/?p=4310
