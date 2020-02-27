# OWL-NETS

OWL-NETS (NEtwork Transformation for Statistical learning) is a novel computational method that reversibly abstracts Web Ontology Language (OWL)-encoded biomedical knowledge into a network representation well-suited for network inference. OWL-NETS generates semantically rich network representations that contain heterogeneous nodes and edges, and are more easily consumed by network inference algorithms than their corresponding OWL representations. We argue that OWL-NETS can be used to leverage existing ontology-based knowledge representations and network inference methods to generate novel, biologically-relevant hypotheses.  

*Callahan TJ, Baumgartner Jr WA, Bada M, Stefanski AL, Tripodi I, White EK, Hunter LE. OWL-NETS: Transforming OWL Representations for Improved Network Inference. In Pacific Symposium on Biocomputing. Pacific Symposium on Biocomputing 2018 (Vol. 23, p. 133). NIH Public Access. [PMC5737627](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5737627/)*

[![DOI](https://zenodo.org/badge/98161637.svg)](https://zenodo.org/badge/latestdoi/98161637)

### Updates (02/27/20)  
An alternative and more generalizable version of OWL-NETS has been created. The verison of this code was created as part of the [PheKnowLator](https://github.com/callahantiff/PheKnowLator/wiki) project. For details, please see the [OWL-NETS 2.0 Wiki page](https://github.com/callahantiff/PheKnowLator/wiki/OWL-NETS-2.0). The code can be found [here](https://github.com/callahantiff/PheKnowLator/blob/master/scripts/python/removes_owl_semantics.py).

<br> 

## Getting Started

To use OWL-NETS, download zip file or fork the project repository. Additional instructions can be found under [*Installation*](#installation). For the program to run successfully the prerequisites must be satisfied. Additional steps must be taken in order to utilize the knowledge sources this method was developed on. Specific instructions for accessing these sources is described in [*Prerequisites*](#prerequisites).

We have provided a directory called "Example_Data" that includes an example query, query results, and the resulting OWL-NETS abstraction and OWL representation networks. See [*Example Data*](#example-data) below for specific instructions on how to use these resources.

### Prerequisites

This program was written on a system running OS X Sierra. Successful execution of this program requires Python version 2.7. In addition, the following data sources were utilized during the development of the method.

  * Python Modules
    * python 2.7
    * Modules are described under [*Installation*](#Installation)


#### Data Sources
OWL-NETS was originally designed for use with the Knowledge Base Of Biomedicine (KaBOB). Only minor modifications should be needed in order to adapt OWL-NETS to other systems using OWL. If this is something you are interested in please contact us directly for assistance.

If you don't have a data source in mind, but want to get started we recommended the following (note. OWL-NETS has not yet been adapted for use with Bio2RDF or AberOWL):
* KaBOB - described in [Livingston et al., BMC Bioinformatics 16, (2015)](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-015-0559-3). A wiki has been developed that provides detailed instructions to develop a personal copy of KaBOB. Installation requires the following steps:
   1. Download [StarDog](https://www.stardog.com/) - a free 30-day trial can be acquired
   2. Initialize [KaBOB instance](https://github.com/bill-baumgartner/kabob.app/wiki)
   3. Complete [Stardog-specific installation](https://github.com/bill-baumgartner/kabob.app/wiki/KaBOB-installation-(Stardog))
* [DisGeNet](http://www.disgenet.org/web/DisGeNET/menu/home) - a platform designed to facilitate human disease-gene variant research. The platform includes an RDF distribution and a [SPARQL endpoint](http://www.disgenet.org/web/DisGeNET/menu/rdf) with example SPARQL queries.
* [Bio2RDF](https://github.com/bio2rdf/bio2rdf-scripts/wiki) - Bio2RDF is a large open source project that leverages Semantic Web technologies to derive large Linked data for use in life sciences research.
* [AberOWL](http://aber-owl.net/) - Provides an infrastructure for performing OWL reasoning over biomedical ontologies.

### Installation

To install and execute the program designate the cloned project folder as the current working directory. Place any outside files within the working directory prior to executing the program.

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
VERY IMPORTANT: A file containing endpoint authentication information must be placed in the same directory as any SPARQL queries you wish to run. On three separate lines, the file should include:
* endpoint url
* username
* password

Provide an empty string for the username and password fields for endpoints with no username/passowrd. See example below as well [authentication](https://github.com/callahantiff/owl-nets/blob/master/authentication).
```
# username/password required
"http://rdf.disgenet.org/sparql/"
'username'
'password'
```

## Running OWL-NETS
OWL-NETS can be run from the command line via argparse arguments, but also has a user-friendly GUI.

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

This window will guide you through the program. A second window will appear when the program is finished instructing you where the output files can be found.

<img src="https://github.com/callahantiff/owl-nets/blob/master/images/OWL-NETS_GUI.png" width="400">


## Example Data
This directory contains data that were produced from running OWL-NETS. The following files are included:
  * Angiogenesis_query: this is an example SPARQL query. This query is searching for human protein-protein interactions that participate in Angiogenesis-related GO biological processes.
  * Angiogenesis_query_results.json.zip: the results from the augmented SPARQL query against KaBOB.
  * Angiogenesis_query_NETS_network.gml: the directed OWL-NETS abstraction network.
  * Angiogenesis_query_NETS_network.json: the metadata for the directed OWL-NETS abstraction network.
  * Angiogenesis_query_OWL_network.gml: the directed OWL representation network.

To use these files unzip Angiogenesis_query_results.json.zip within the 'Example_Data' directory and run the code as described in [*Running OWL-NETS*](#running-owl-nets). Placing the SPARQL query and Angiogenesis_query_results.json in the same directory will allow users to explore the functionality of the code without requiring access to KaBOB.

## Contributing

Please read [CONTRIBUTING.md](https://github.com/callahantiff/owl-nets/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Testing
We are in the process of developing tests for each module. We will create documentation as they are created.

## Authors

* Tiffany J. Callahan
* William A. Baumgartner, Jr. [bill-baumgartner](https://github.com/bill-baumgartner)
* Michael Bada
* Lawrence E. Hunter


## License

This project is licensed under 3-Clause BSD License - see the [LICENSE.md](https://github.com/callahantiff/owl-nets/blob/master/LICENSE) file for details.

## Acknowledgments

* README was generated from a modified markdown template originally created by **Billie Thompson [PurpleBooth](https://github.com/PurpleBooth)**.
