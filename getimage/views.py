from django.shortcuts import render
import pandas as pd
from lodstorage.sparql import SPARQL
from lodstorage.csv import CSV
import ssl
import json
from urllib.error import HTTPError
from urllib.request import urlopen

def iiifmanifest():
    ssl._create_default_https_context = ssl._create_unverified_context

    sparqlQuery = """
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    SELECT ?o WHERE {
    ?s cidoc:P129i_is_subject_of ?o .
    BIND(RAND() AS ?random) .
    } ORDER BY ?random
    LIMIT 1
    """

    df_sparql = pd.DataFrame()
    sparql = SPARQL("https://stad.gent/sparql")
    qlod = sparql.queryAsListOfDicts(sparqlQuery)
    csv = CSV.toCSV(qlod)
    df_result = pd.DataFrame([x.split(',') for x in csv.split('\n')])
    df_sparql = df_sparql.append(df_result, ignore_index=True)
    df_sparql[0] = df_sparql[0].str.replace(r'"', '')
    df_sparql[0] = df_sparql[0].str.replace(r'\r', '')

    iiifmanifest = df_sparql[0].iloc[1]
    return iiifmanifest

def image(request):
    manifest = iiifmanifest()
    try:
        response = urlopen(manifest)
    except ValueError:
        return image(request)
    except HTTPError:
        return image(request)
    else:
        data_json = json.loads(response.read())
        iiif_manifest = data_json["sequences"][0]['canvases'][0]["images"][0]["resource"]["@id"]
        iiif_manifest = iiif_manifest.replace("full/full/0/default.jpg","full/1000,/0/default.jpg")
        label = data_json["label"]['@value']
        if 'stam' in manifest:
            instelling = 'STAM'
        elif 'hva' in manifest:
            instelling = 'Huis van Alijn'
        elif 'dmg' in manifest:
            instelling = 'Design Museum Gent'
        elif 'industriemuseum' in manifest:
            instelling = 'Industriemuseum'
        else:
            instelling = 'Archief Gent'
        return render(request, 'image.html', {'iiif_manifest': iiif_manifest, 'instelling': instelling, 'label': label})






    
