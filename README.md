# harris2graph

### A tool to convert legacy .LST Harris Matrix files into modern graph formats.

harris2graph is a script to help migrate data from the LST file format used by the BASP Harris, Stratify and ArchEd packages into modern graph file formats.

The supported output formats are:
* Graph Modelling Language (GML)
* GraphViz / Dot (GV/DOT)
* GraphML
* Graph Exchange Language (GXL)
* Trivial Graph Format (TGF)
* Comma Separated Value (CSV)

harris2graph can be run in simple mode, where only the basic relationship data is written out, or by default will attempt to populate more detailed graph attributes such as node shape and size to assist in the graph layout. GML and GV provide the best support for these attributes. harris2graph does not provide an actual layout of the nodes or edges, this must be calculated by a separate process.

Currently, harris2graph only supports the basic above/below relationships. The equal/contemporary relationships and the additional attributes supported by Stratify and ArchEd are not currently supported.
