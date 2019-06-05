# Experiment
The primary module to capture provenance of scientific experiments. The module is implemented as a plugin in webclient. It provides a Metadata Editor to document the metadata of the computational and non-computational steps of an scientific experiment.

**Requirements**

* OMERO server. Check the guideliness to install OMERO [here](https://github.com/CaesarReceptorLight/openmicroscopy) 
* Install the third party libraries used in the Experiment code.  
  * pip install django-form-utils  
  * pip install reportlab  
  * pip install httplib2  
  * pip install sparqlwrapper  

**Installation**

1.	Copy the folder 'Experiment' to:

    /home/omero/OMERO.server/lib/python/omeroweb/

2.	Add Experiment to the known web apps

    /home/omero/OMERO.server/bin/omero config append omero.web.apps '"Experiment"'

3.	Add the Experiment plugin to the list of right plugins

   /home/omero/OMERO.server/bin/omero config append omero.web.ui.right_plugins '["Experiment", "Experiment/
webclient_plugins/right_plugin.experiment.js.html","receptor_experiment_tab"]'

4.  Restart the web server

    /home/omero/OMERO.server/bin/omero web restart

Publication
-----------
* [Towards reproducibility of microscopy experiments](https://doi.org/10.1045/january2017-samuel), Sheeba Samuel, Frank Taubert, Daniel Walther, Birgitta König-Ries, H Martin Bücker, D-Lib Magazine, 2017.
* [The Story of an Experiment: A Provenance-based Semantic Approach towards Research Reproducibility](http://ceur-ws.org/Vol-2275/paper2.pdf), Sheeba Samuel, Kathrin Groeneveld, Frank Taubert, Daniel Walther, Tom Kache, Teresa Langenstück, Birgitta König-Ries, H Martin Bücker, and Christoph Biskup, SWAT4LS 2018.
