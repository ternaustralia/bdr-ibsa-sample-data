# Mesa A and K Targeted Troglofauna Survey

IBSA-2018-0064. Targeted Subterranean Fauna Survey conducted for Robe River Mining Co. Ply. Ltd, for the Robe Valley.

The data in this repository was obtained from _Biota Environmental Sciences (2017). Mesa A and K Targeted Troglofauna Survey. Unpublished report prepared for Rio Tinto._ The data was accessed on 2021-11-23 from https://biocollect.ala.org.au/ibsa/project/index/8043050a-f488-47f0-908f-ebc629b1f20c.

This repository provides a worked example on mapping the troglofauna survey data to the [TERN Ontology](https://w3id.org/tern/ontologies/tern/), and made available in a few RDF serialisation formats.

## Worked example

The following CSV files located in [source-data/](source-data/) were generated from the source ESRI files downloaded at https://biocollect.ala.org.au/ibsa/project/index/8043050a-f488-47f0-908f-ebc629b1f20c. The CSV files are a subset of the original data to provide a minimal example of the mapping and transformation process.

The [run.py](run.py) Python script converts the [source-data/](source-data/) CSVs into RDF and outputs the result into [output.ttl](output.ttl).

A copy of [output.ttl](output.ttl) is available online via SPARQL at https://graphdb.tern.org.au/repositories/bdr-ibsa-sample-data. One way to send SPARQL queries to the endpoint is to use https://yasgui.triply.cc/.

## Visualising the RDF data using Ontodia

During the 2021-11-25 BDR workshop, the RDF data was visualised using [metaphacts/ontodia](https://github.com/metaphacts/ontodia). 

View the data in Ontodia at https://ternaustralia.github.io/bdr-ibsa-sample-data.

## Worked example presentation slides

- [Download](https://docs.google.com/presentation/d/1PAfLXi-fX0R5n7V6otK2hDjfqpUa2hov/edit?usp=sharing&ouid=108129827562056706312&rtpof=true&sd=true)

## Conceptual modelling assumptions

The worked example was created based on the following assumptions:

- Mesa A and K are the (ultimate) `features-of-interest` of the investigation. They are treated as a single top-level `feature-of-interest` in this worked example.
- Mesa A and K contain sites where acts of `sampling` are conducted during site visits.
- `Material samples` were collected as a `result` of these acts of `sampling`. 
- The `samples` are the (proximate) `features-of-interest` of subsequent acts of `observation`. Each observed or measured value is the `result` of a separate `observation`. The `observed-property` of the most important `observation` is "taxon name" (this is the label of an entry from a controlled vocabulary). The `result` of this `observation` is an individual taxon name value. 
- Taxon name values are mapped to the `dwc:scientificName` property of an instance of `tern:Taxon` but data quality checks suggest not all values meet the definition of a "scientific name". For example, in cases where the taxon name values contains "SCH034", it should be modelled as a "field name" observation instead of a "taxon name" observation. The value type of a "field name" will use the `tern:Text` class instead of the `tern:Taxon` class.
- Some additional information were taken from the Survey Report PDF.
- Not all attributes were mapped and transformed, just some, as a demonstration.
- Although an occurrence must exist to obtain a material sample, the data does not record occurrences explicitly. Therefore, the material samples, instead of being sub-samples of an occurrence (sample), they are instead a sub-sample of the site.

## Contact

Edmond Chuc  
e.chuc@uq.edu.au
