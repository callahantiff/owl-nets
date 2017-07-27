# OWL-NETS
## What is OWL-NETS?

The Web Ontology Language (OWL) is a Semantic Web standard, which, in conjunction with biomedical ontologies, is widely used to model complex biological knowledge. Network inference techniques, when applied to biological data, have the potential to generate novel biological insights. While OWL facilitates logically consistent integration of independent and conflicting sources of semantic knowledge, its representational complexity reduces the effectiveness of certain types of network inference.

OWL-NETS (NEtwork Transformation for Statistical learning) is a novel computational method that reversibly abstracts Web Ontology Language (OWL)-encoded biomedical knowledge into a network representation well-suited for network inference. OWL-NETS generates semantically rich network representations that contain heterogeneous nodes and edges, and are more easily consumed by network inference algorithms than their corresponding OWL representations. We argue that OWL-NETS can be used to leverage existing ontology-based knowledge representations and network inference methods to generate novel, significant biological hypotheses.

## How Does it Work?
### Assumptions
OWL-NETS is implemented in Python (v2.7) and can be run from a simple GUI or from the command line. While primarily developed for use with OWL, the program can be extended for use with other Semantic Web technologies by modifying two primary assumptions:
  * Relations in the knowledge source denote (e.g., IAO:000219 "denotes") or identify (e.g., dc:identifier) biological entities (i.e., "NETS nodes"). The default relation is IAO:denotes.
  * Object properties (e.g., owl:Restriction, SIO:gene-disease association) specify relationships between biological entities (i.e.,"NETS edges"). The default object property is owl:Restriction.

### Overview
We describe the OWL-NETS methodology using an example query that investigates disease-associated proteins that participate in angiogenesis (Figure 1). The method takes a SPARQL query as input and outputs a directed OWL-NETS abstraction network, directed OWL representation, or both directed network representations. To improve processing efficiency, the majority of the computational workload is performed on the input SPARQL query (steps 1-4 in Figure 1) rather than the resulting output.

<!--<img src="https://github.com/callahantiff/owl-nets/blob/master/docs/images/Figure1.png" width="1200"> -->
<!--![ScreenShot](/images/Figure1.png)-->
<img src="/owl-nets/images/Figure1.png" alt="Figure 1" width="1500"/>

**1. Construct Query Graph and Identify NETS Nodes:** the input SPARQL query is used to create a directed query graph, where each triple (shown in a pink box) represents a directed edge in the query graph. The graph is searched for edges containing denotes relations (\textit{Assumption 1}, shown in the figure as a dashed orange arrow). NETS nodes (Angiogenesis, Participating Proteins, and Diseases) are identified as the object of these relations. 

**2. Identify NETS Edges:** The shortest path length between all pairs of NETS nodes determines which nodes should be connected by an edge. As shown in the figure, the path between Angiogenesis and Participating proteins is shorter than the path between Angiogenesis and Diseases. This information is stored as a list of edge tuples.  

**3. Determine NETS Edge Directionality:** The shortest path (calculated in step 2), is searched for restrictions (\textit{Assumption 2}, shown in the figure as light green nodes). The NETS node that is reachable from the restriction node's out-edges (typically owl:someValuesFrom) is the target of the NETS edge. In Figure 1, the green restriction node has an out-edge that points towards Diseases, thus an arrow is drawn from Participating Proteins to Diseases. In situations where both NETS nodes can be reached from a restriction node, an arrow is drawn from each NETS node.

**4. Create Network Edge and Node Metadata:** The source identifiers and labels denoting each node (shown in the figure as dark blue boxes) are stored as node metadata. Two types of edge metadata are stored; 1) the object property class and label (e.g., obo:RO\_0000057 "has participant", shown in the gray rectangle); and 2) all edges from the query graph needed to connect the NETS nodes in a given edge (shown as the colored edge list). This metadata is needed to integrate inferred edges in the OWL-NETS abstraction network into the knowledge base.

**5. Query Endpoint and Construct Network:** Using the node and edge metadata from Step 4, the original SPARQL query is updated and run against an endpoint. The endpoint results and node and edge metadata dictionaries are then used to construct the OWL-NETS abstraction network. The program outputs a json file that contains the directed OWL-NETS abstraction network (.gml) and node and edge metadata.
  
## Biomedical Use Case
 
| Description                                                                                   | Data Source            |     
|:---------------------------------------------------------------------------------------------:|:----------------------:|
| Human Protein-protein interactions that participate in the biological process of angiogenesis | Gene Ontology; Uniprot  
  
  
The image on the left shows the directed OWL network representation of Query 1. The image on the right is the directed absraction network that results when using OWL-NETS. The OWL representation consists of 32,850 nodes and 65,526 edges. The OWL-NETS abstraction network contained 2,2926 nodes and 9,549 edges.

<img src="/owl-nets/images/angiogenesis_owl+nets.png" alt="OWL + OWL-NETS Representation" width="800"/>
