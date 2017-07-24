# OWL-NETS

 OWL-NETS (NEtwork Transformation for Statistical Learning) is a novel computational method that reversibly abstracts OWL-encoded biomedical knowledge into a representation well-suited for inference. The OWL-NETS method can be used to leverage existing ontology-based knowledge representations and network inference methods to generate novel, significant biological hypotheses.

## Getting Started

To use OWL-NETS, download zipped file or fork and clone project repository. Additional instructions can be found under [*Installation*](#installation). For the program to run successfully the prerequisites must be satisfied. Additional steps must be taken in order to utilize the knowledge sources this method was developed on. Specific instructions for accessing these sources is described in [*Prerequisites*](#prerequisites).

### Prerequisites

This program was written on a system running OS X Sierra. Successful execution of this program requires Python version 2.7. In addition, the following data sources were utilized during the development of the method.

  * Python Modules
    * python 2.7.10 or greater
    * Modules are described under [*Installation*](#Installation)


#### Data Sources
While not a requirement, OWL-NETS was originally designed for use with the Knowledge Base Of Biomedicine (KaBOB). We also have versions of the method that work with RDF (tested using DisGeNet) in development. As the method is data-driven and built on OWL, only minor modifications should be needed in order to adapt it to other systems that use Semantic Web Technologies, especially OWL. If this is something you are interested in please contact us directly for assistance.

If you don't have a data source in mind, but want to get started we recommended the following (note. OWL-NETS has not yet been adapted for use with Bio2RDF or AberOWL, but it is something we intend to explore in future work):
* KaBOB - described in [Livingston et al., BMC Bioinformatics 16, (2015)](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-015-0559-3). A wiki has been developed that provides detailed instructions to develop a personal copy of KaBOB. Installation requires the following steps:
   1. Download [StarDog](https://www.stardog.com/) - a free 30-day trial can be acquired
   2. Initialize [KaBOB instance](https://github.com/bill-baumgartner/kabob.app/wiki)
   3. Complete [Stardog-specific installation](https://github.com/bill-baumgartner/kabob.app/wiki/KaBOB-installation-(Stardog))
* [DisGeNet](http://www.disgenet.org/web/DisGeNET/menu/home) - a platform designed to facilitate human disease-gene variant research. The platform includes an RDF distribution and a [SPARQL endpoint](http://www.disgenet.org/web/DisGeNET/menu/rdf) with example SPARQL queries.
* [Bio2RDF](https://github.com/bio2rdf/bio2rdf-scripts/wiki) - Bio2RDF is a large open source project that leverages Semantic Web technologies to derive large Linked data for use in life sciences research.
* [AberOWL](http://aber-owl.net/) - Provides an infrastructure for performing OWL reasoning over biomedical ontologies.

### Installation

To install and execute the program designate the cloned project folder as the current working directory. Please note that any outside files should be placed within the working directory prior to executing the program. This program has prerequisites that must be installed and imported.

Program dependencies can be installed using the following:

```
pip install argparse
pip install datetime
pip install networkx
pip install progressbar
pip install requests
pip install SPARQLWrapper
pip install urllab2
```

and imported with (scripts will automatically import needed modules):

```
import argparse
from datetime import datetime
import json
import networkx as nx
import os
from progressbar import ProgressBar, FormatLabel, Percentage, Bar
import re
import requests
import simplejson as json
from SPARQLWrapper import SPARQLWrapper, JSON
import tkFileDialog
from Tkinter import *
import tkMessageBox
import urllib2
```

#### Authentication
VERY IMPORTANT: This file must be placed in the same directory as any SPARQL queries you wish to run. Inside the file, on three separate lines provide:
* endpoint url
* username
* password

This information must be provided to query an endpoint. Provide an empty string for the username and password fields for endpoints not requiring this information. See example below as well [authentication](https://github.com/callahantiff/owl-nets/blob/master/authentication).
```
# username/password required
"http://rdf.disgenet.org/sparql/"
'username'
'password'
```


## Running OWL-NETS
OWL-NETS can be run from the command line via argparse arguments, but also has a user-friendly GUI. See specific instructions for using both methods below.

Running program from the command line
```
# from project directory - find help menu
tiffanycallahan$ python OWL_NETS.py -h

usage: OWL_NETS.py [-h] [-a INPUT] [-b OWL] [-c NETS] [-d BOTH]

OWL-NETS: NEtwork Entity Transformation for Statistical Learning. For program
to run correctly the input arguments must be formatted as shown below.

optional arguments:
  -h, --help            show this help message and exit
  -a INPUT, --input INPUT
                        name/path to SPARQL query file (e.g.,
                        Folder/Query1_query)
  -b OWL, --owl OWL     type "owl" to generate OWL representation
  -c NETS, --nets NETS  type "owl-nets" to generate OWL-NETS representation
  -d BOTH, --both BOTH  type "both" to generate both representations

# to run the program
tiffanycallahan$ python OWL_NETS.py -a Queries/drug_interaction_query.txt
-b Output/owl_drug_int_graph.gml -c Output/owlnet_drug_int_graph.gml -d
 Output/drug_int_query_results.json
```


Running program using the GUI
```
# from project directory
tiffanycallahan$ python OWL_NETS.py
```

After running the above code the following window will appear. This window will guide you through the program. A second window will appear when the program is finished instructing you where the output files can be found.

<img src="https://github.com/callahantiff/owl-nets/blob/master/images/OWL-NETS_GUI.png" width="400">


## Contributing

Please read [CONTRIBUTING.md](https://github.com/callahantiff/owl-nets/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

* Tiffany J. Callahan
* William A. Baumgartner, Jr. [bill-baumgartner](https://github.com/bill-baumgartner)
* Michael Bada
* Lawrence E. Hunter


## License

This project is licensed under 3-Clause BSD License - see the [LICENSE.md](https://github.com/callahantiff/owl-nets/blob/master/LICENSE) file for details.

## Acknowledgments

* We thank Ignacio Tripodi, Adrianne Stefanski, Marc Daya, Drs. Kevin Bretonnel Cohen, Elizabeth White, Anis Karimpour-Fard, Carsten Görg, and Daniel McShan, as well as Laura Stevens for their feedback.

* Work supported by the National Library of Medicine Training Grant T15 LM009451, as well as R01 LM009254 and R01LM008111 to LH. The content is solely the responsibility of the authors and does not necessarily represent the views of the National Institutes of Health or the National Library of Medicine.

* README was generated from a modified markdown template originally created by **Billie Thompson [PurpleBooth](https://github.com/PurpleBooth)**.
