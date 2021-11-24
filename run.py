import uuid

import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, VOID, XSD, SOSA, DCTERMS, PROV, TIME

sites_csv = "source-data/sample-sites.csv"
site_of_interest = "RC16MEA0004"
fauna_csv = "source-data/fauna.csv"

sites_df = pd.read_csv(sites_csv)
fauna_df = pd.read_csv(fauna_csv)

# Get the "site visit" by SiteName and EndDate.
site_subset_df = sites_df[
    (sites_df["SiteName"] == site_of_interest) & (sites_df["EndDate"] == "2017/03/23")
]

g = Graph()
g.bind("void", VOID)
g.bind("sosa", SOSA)
g.bind("dcterms", DCTERMS)
g.bind("prov", PROV)
g.bind("time", TIME)
BASE_URI = Namespace("https://linked.data.gov.au/dataset/IBSA-2018-0064/")
method_uri = URIRef("https://ecodata.ala.org.au/uploads/2020-10/12_Survey_Report.pdf")
TERN = Namespace("https://w3id.org/tern/ontologies/tern/")
g.bind("tern", TERN)
TERN_LOC = Namespace("https://w3id.org/tern/ontologies/loc/")
g.bind("loc", TERN_LOC)
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
g.bind("geo", GEO)
WGS = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
g.bind("wgs", WGS)
DWC = Namespace("http://rs.tdwg.org/dwc/terms/")
g.bind("dwc", DWC)
rdf_dataset_uri = URIRef("https://linked.data.gov.au/dataset/IBSA-2018-0064/1")


def get_uri_from_seed(seed):
    uri = uuid.uuid5(uuid.NAMESPACE_URL, seed)
    return BASE_URI[str(uri)]


# (Ultimate) Feature of Interest
ufoi_uri = URIRef(BASE_URI["survey-area"])
ufoi_wkt = "MultiPolygon (((387430.70000000001164153 7605294.58999999985098839, 387430.70000000001164153 7601068.2099999999627471, 382700.90000000002328306 7601068.2099999999627471, 382700.90000000002328306 7605294.58999999985098839, 387430.70000000001164153 7605294.58999999985098839)),((424171.11999999999534339 7598184.66000000014901161, 424171.11999999999534339 7597499.78000000026077032, 423138.52000000001862645 7597499.78000000026077032, 423138.52000000001862645 7598184.66000000014901161, 424171.11999999999534339 7598184.66000000014901161)))"
g.add((ufoi_uri, RDF.type, TERN.FeatureOfInterest))
g.add((ufoi_uri, RDFS.label, Literal("IBSA-2018-0064 survey area")))
g.add((ufoi_uri, VOID.inDataset, rdf_dataset_uri))
g.add((ufoi_uri, RDFS.label, Literal("Mesa A and K")))
# ufoi_geo_bnode = BNode("ufoi_geo_bnode" + ufoi_uri)
ufoi_geo_bnode = get_uri_from_seed("ufoi_geo_bnode" + ufoi_uri)
g.add((ufoi_uri, GEO.hasGeometry, ufoi_geo_bnode))
g.add((ufoi_geo_bnode, RDF.type, TERN_LOC.Polygon))
g.add((ufoi_geo_bnode, RDFS.label, Literal("IBSA-2018-0064 polygon")))
g.add((ufoi_geo_bnode, GEO.asWKT, Literal(ufoi_wkt, datatype=GEO.wktLiteral)))
g.add(
    (
        ufoi_uri,
        TERN.featureType,
        URIRef(
            "http://linked.data.gov.au/def/tern-cv/5bf7ae21-a454-440b-bdd7-f2fe982d8de4"
        ),
    )
)

for _, row in site_subset_df.iterrows():
    site_uri = BASE_URI[f"site/{row['SiteName']}"]

    # Sampling for Site
    sampling_uri = BASE_URI[f"sampling/{row['SiteName']}"]
    g.add((sampling_uri, RDF.type, TERN.Sampling))
    g.add(
        (sampling_uri, RDFS.label, Literal(f"Site establishment for {row['SiteName']}"))
    )
    g.add((sampling_uri, SOSA.hasFeatureOfInterest, ufoi_uri))
    g.add((sampling_uri, VOID.inDataset, rdf_dataset_uri))
    g.add((sampling_uri, SOSA.resultTime, Literal(row["StartDate"], datatype=XSD.date)))
    g.add((sampling_uri, SOSA.usedProcedure, method_uri))
    g.add((sampling_uri, SOSA.hasResult, site_uri))
    # Optionally, we can also add who performed the sampling using `prov:wasAssociatedWith`.
    g.add(
        (sampling_uri, PROV.wasAssociatedWith, Literal("Biota Environmental Sciences"))
    )

    # Sites
    g.add((site_uri, RDF.type, TERN.Site))
    g.add((site_uri, RDFS.label, Literal(f"Site {row['SiteName']}")))
    g.add((site_uri, DCTERMS.identifier, Literal(row["SiteName"])))
    g.add((site_uri, VOID.inDataset, rdf_dataset_uri))
    g.add((site_uri, SOSA.isResultOf, sampling_uri))
    g.add((site_uri, SOSA.isSampleOf, ufoi_uri))
    g.add((site_uri, TERN.locationProcedure, method_uri))
    g.add(
        (
            site_uri,
            GEO.sfWithin,
            URIRef("http://linked.data.gov.au/dataset/asgs2016/stateorterritory/5"),
        )
    )
    g.add(
        (
            site_uri,
            TERN.featureType,
            URIRef(
                "http://linked.data.gov.au/def/tern-cv/8cadf069-01d7-4420-b454-cae37740c2a2"
            ),
        )
    )

    site_geo_bnode = get_uri_from_seed("site_geo_bnode" + site_uri)
    g.add((site_uri, GEO.hasGeometry, site_geo_bnode))

    g.add((site_geo_bnode, RDF.type, TERN_LOC.Point))
    g.add((site_geo_bnode, RDFS.label, Literal(f"Site {row['SiteName']} point")))
    lat = row["Lat_GDA94"]
    long = row["Long_GDA94"]
    site_point_wkt = f"POINT({long} {lat})"
    g.add(
        (
            site_geo_bnode,
            GEO.asWKT,
            Literal(site_point_wkt, datatype=GEO.wktLiteral),
        )
    )
    g.add((site_geo_bnode, WGS.lat, Literal(lat, datatype=XSD.double)))
    g.add((site_geo_bnode, WGS.long, Literal(long, datatype=XSD.double)))

    site_fauna_df = fauna_df[(fauna_df["SiteName"] == row["SiteName"])]
    for _, fauna_row in site_fauna_df.iterrows():
        fauna_uri = BASE_URI[f"sample/{fauna_row['MuseumRef']}"]

        # Create the site visit
        site_visit_uri = BASE_URI[
            f"site-visit/{fauna_row['DateObs'].replace('/', '-')}"
        ]
        g.add((site_visit_uri, RDF.type, TERN.SiteVisit))
        g.add(
            (
                site_visit_uri,
                RDFS.label,
                Literal(
                    f"Site visit {fauna_row['DateObs'].replace('/', '-')} for {row['SiteName']}"
                ),
            )
        )
        g.add(
            (
                site_visit_uri,
                PROV.startedAtTime,
                Literal(fauna_row["DateObs"], datatype=XSD.date),
            )
        )
        g.add((site_visit_uri, VOID.inDataset, rdf_dataset_uri))
        g.add((site_visit_uri, TERN.hasSite, site_uri))

        # Sampling for fauna
        fauna_sampling_uri = BASE_URI[f"sampling/{fauna_row['MuseumRef']}"]
        g.add((fauna_sampling_uri, RDF.type, TERN.Sampling))
        g.add(
            (
                fauna_sampling_uri,
                RDFS.label,
                Literal(f"Sampling for fauna {fauna_row['MuseumRef']}"),
            )
        )
        g.add((fauna_sampling_uri, SOSA.hasFeatureOfInterest, site_uri))
        g.add((fauna_sampling_uri, VOID.inDataset, rdf_dataset_uri))
        g.add((fauna_sampling_uri, SOSA.usedProcedure, method_uri))
        g.add((fauna_sampling_uri, SOSA.hasResult, fauna_uri))
        g.add((fauna_sampling_uri, RDFS.comment, Literal(fauna_row["Comments"])))
        g.add((fauna_sampling_uri, TERN.samplingType, Literal(fauna_row["ObsMethod"])))
        g.add((fauna_sampling_uri, TERN.hasSiteVisit, site_visit_uri))
        g.add(
            (
                fauna_sampling_uri,
                PROV.wasAssociatedWith,
                Literal("Biota Environmental Sciences"),
            )
        )
        g.add(
            (
                fauna_sampling_uri,
                SOSA.resultTime,
                Literal(fauna_row["DateObs"], datatype=XSD.date),
            )
        )
        fauna_sampling_geo_bnode = get_uri_from_seed(
            "fauna_sampling_geo_bnode" + fauna_sampling_uri
        )
        g.add((fauna_sampling_uri, GEO.hasGeometry, fauna_sampling_geo_bnode))
        g.add((fauna_sampling_geo_bnode, RDF.type, TERN_LOC.Point))
        g.add(
            (
                fauna_sampling_geo_bnode,
                RDFS.label,
                Literal(f"Sampling point for fauna {fauna_row['MuseumRef']}"),
            )
        )
        sampling_point_wkt = (
            f"POINT({fauna_row['Long_GDA94']} {fauna_row['Lat_GDA94']})"
        )
        g.add(
            (
                fauna_sampling_geo_bnode,
                GEO.asWKT,
                Literal(sampling_point_wkt, datatype=GEO.wktLiteral),
            )
        )
        g.add((fauna_sampling_geo_bnode, WGS.lat, Literal(fauna_row["Lat_GDA94"])))
        g.add((fauna_sampling_geo_bnode, WGS.long, Literal(fauna_row["Long_GDA94"])))

        # Fauna sample
        # Fauna sample was taken from an animal occurrence. But since the animal occurrence is of
        # no interest to us, we only capture the material sample collected.
        g.add((fauna_uri, RDF.type, TERN.MaterialSample))
        g.add((fauna_uri, RDFS.label, Literal(f"{fauna_row['MuseumRef']} sample ID")))
        g.add((fauna_uri, DWC.materialSampleID, Literal(fauna_row["MuseumRef"])))
        g.add((fauna_uri, VOID.inDataset, rdf_dataset_uri))
        g.add((fauna_uri, SOSA.isResultOf, fauna_sampling_uri))
        g.add((fauna_uri, SOSA.isSampleOf, site_uri))
        g.add(
            (
                fauna_uri,
                TERN.featureType,
                URIRef(
                    "http://linked.data.gov.au/def/tern-cv/cd5cbdbb-07d9-4a5b-9b11-5ab9d6015be6"
                ),
            )
        )

        fauna_type_bnode = get_uri_from_seed("fauna_type_bnode" + fauna_uri)
        fauna_type_value_bnode = get_uri_from_seed("fauna_type_value_bnode" + fauna_uri)
        g.add((fauna_uri, TERN.hasAttribute, fauna_type_bnode))
        g.add((fauna_type_bnode, RDF.type, TERN.Attribute))
        g.add((fauna_type_bnode, RDFS.label, Literal("Fauna type attribute")))
        g.add((fauna_type_bnode, VOID.inDataset, rdf_dataset_uri))
        g.add((fauna_type_bnode, TERN.attribute, Literal("fauna type")))
        g.add((fauna_type_bnode, TERN.hasValue, fauna_type_value_bnode))
        g.add((fauna_type_value_bnode, RDF.type, TERN.Text))
        g.add((fauna_type_value_bnode, RDFS.label, Literal("Fauna type value")))
        g.add((fauna_type_value_bnode, RDF.value, Literal(fauna_row["FaunaType"])))
        g.add((fauna_type_bnode, TERN.hasSimpleValue, Literal(fauna_row["FaunaType"])))

        # Fauna observation - taxon name
        taxon_observation_uri = BASE_URI[
            f"observation/{fauna_row['MuseumRef']}/taxon-name"
        ]
        g.add((taxon_observation_uri, RDF.type, TERN.Observation))
        g.add(
            (
                taxon_observation_uri,
                RDFS.label,
                Literal(f"Taxon name observation for fauna {fauna_row['MuseumRef']}"),
            )
        )
        g.add(
            (
                taxon_observation_uri,
                RDFS.label,
                Literal(f"{fauna_row['MuseumRef']} taxon name"),
            )
        )
        g.add((taxon_observation_uri, SOSA.usedProcedure, method_uri))
        g.add((taxon_observation_uri, SOSA.hasFeatureOfInterest, fauna_uri))
        g.add((taxon_observation_uri, VOID.inDataset, rdf_dataset_uri))
        g.add((taxon_observation_uri, RDFS.comment, Literal(fauna_row["Comments"])))
        g.add(
            (
                taxon_observation_uri,
                PROV.wasAssociatedWith,
                Literal("Biota Environmental Sciences"),
            )
        )
        g.add(
            (
                taxon_observation_uri,
                SOSA.resultTime,
                Literal(fauna_row["DateObs"], datatype=XSD.date),
            )
        )
        taxon_observation_phenomenon_time_bnode = get_uri_from_seed(
            "taxon_observation_phenomenon_time_bnode" + taxon_observation_uri
        )
        g.add(
            (
                taxon_observation_uri,
                SOSA.phenomenonTime,
                taxon_observation_phenomenon_time_bnode,
            )
        )
        g.add((taxon_observation_phenomenon_time_bnode, RDF.type, TERN.Instant))
        g.add(
            (
                taxon_observation_phenomenon_time_bnode,
                RDFS.label,
                Literal("Phenomenon time"),
            )
        )
        g.add(
            (
                taxon_observation_phenomenon_time_bnode,
                TIME.inXSDDate,
                Literal(fauna_row["DateObs"], datatype=XSD.date),
            )
        )
        g.add(
            (
                taxon_observation_uri,
                SOSA.observedProperty,
                URIRef(
                    "http://linked.data.gov.au/def/tern-cv/70646576-6dc7-4bc5-a9d8-c4c366850df0"
                ),
            )
        )
        g.add(
            (
                taxon_observation_uri,
                SOSA.hasSimpleResult,
                BASE_URI[
                    f"""taxon/{fauna_row["TaxonName"].replace(" ", "-").replace("'", "")}"""
                ],
            )
        )
        taxon_result_bnode = get_uri_from_seed(
            "taxon_result_bnode" + taxon_observation_uri
        )
        g.add((taxon_observation_uri, SOSA.hasResult, taxon_result_bnode))

        g.add((taxon_result_bnode, RDF.type, TERN.Taxon))
        g.add(
            (
                taxon_result_bnode,
                RDFS.label,
                Literal(f"Taxon result for fauna {fauna_row['MuseumRef']}"),
            )
        )
        g.add((taxon_result_bnode, DWC.scientificName, Literal(fauna_row["TaxonName"])))

        # The Survey Report PDF also contains taxonomy information which can be added here.
        if (
            fauna_row["TaxonName"] == "Paradraculoides sp. 'SCH034'"
            or fauna_row["TaxonName"] == "Paradraculoides anachoretus"
        ):
            g.add((taxon_result_bnode, DWC.order, Literal("Schizomida")))
            g.add((taxon_result_bnode, DWC.family, Literal("Hubbardiidae")))
        g.add((taxon_observation_uri, TERN.hasSiteVisit, site_visit_uri))

g.parse("rdf-metadata.ttl")
g.serialize("output.ttl")
