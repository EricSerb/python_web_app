# Map Visualization of Large Data in Python :alien:

> CIS5930 - Python Programming at Florida State University.
> Adam Stallard and Eric Serbousek
> Fall 2016


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
export `LD_LIBRARY_PATH=/path/to/configure/prefix/lib:$LD_LIBRARY_PATH`  
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


## TO-DO
* [x] Add requirements to README
* [x] Add setup / run to README
* [] Add information about datasets to README
* [] Add info about openstreetmaps to README
* [] Add info about EDGE / DOMS / SAMOS to README
* [] Relay client zoom state (bounding box) to server
* [] Cluster data extracted from the KDTree
* [] Compress clustered data for smaller server->client packet sizes
* [] Decompress data on client side (via JS?)
* [] Distinguish clusters on client side (JS?)
* [] Populate map on client side (JS?)
* [] Add diagrams so people know what the hell we are talking about :joy:
* [] Have a drink

