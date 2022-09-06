from django.shortcuts import render
import pandas as pd
from lodstorage.sparql import SPARQL
from lodstorage.csv import CSV
import ssl
import json
import math
import random
from urllib.error import HTTPError
from urllib.request import urlopen

ssl._create_default_https_context = ssl._create_unverified_context

sparqlQuery = """PREFIX purl: <http://purl.org/dc/terms/>
PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
SELECT COUNT (DISTINCT ?title )
WHERE {
SELECT ?title
FROM <http://stad.gent/ldes/hva> 
FROM <http://stad.gent/ldes/dmg>
FROM <http://stad.gent/ldes/industriemuseum>
FROM <http://stad.gent/ldes/archief>

WHERE {
?s cidoc:P102_has_title ?title.
?s cidoc:P129i_is_subject_of ?beeld.
?s purl:isVersionOf ?priref.
}
}
"""

sparql = SPARQL("https://stad.gent/sparql")
qlod = sparql.queryAsListOfDicts(sparqlQuery)
aantal = qlod[0]['callret-0']
offsetrange = aantal / 1000

# determine number of pages to query
pages = math.ceil(offsetrange)

# determine offset range to query
offsetrange = list(range(0, 1000 * pages, 1000))

querylist = []
for offset in offsetrange:
    querylist.append("""PREFIX purl: <http://purl.org/dc/terms/>
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    
    SELECT DISTINCT ?title ?beeld ?priref
    FROM <http://stad.gent/ldes/hva> 
    FROM <http://stad.gent/ldes/dmg>
    FROM <http://stad.gent/ldes/industriemuseum>
    FROM <http://stad.gent/ldes/archief>
    
    WHERE {
    ?s cidoc:P102_has_title ?title.
    ?s cidoc:P129i_is_subject_of ?beeld.
    ?s purl:isVersionOf ?priref.
    } LIMIT 1000""" + str(offset))

df_sparql = pd.DataFrame()
for query in querylist:
    sparqlQuery = query
    sparql = SPARQL("https://stad.gent/sparql")
    qlod = sparql.queryAsListOfDicts(sparqlQuery)
    csv = CSV.toCSV(qlod)
    df_result = pd.DataFrame([x.split(',') for x in csv.split('\n')])
    df_sparql = df_sparql.append(df_result, ignore_index=True)

df_sparql = df_sparql[df_sparql[1].str.contains("api", na=False)]
df_sparql[1] = df_sparql[1].str.replace(r'"', '')
df_sparql[1] = df_sparql[1].str.replace(r'\r', '')

iiifmanifesten = df_sparql[1].tolist()


def image(request):
    x = random.randint(0, len(iiifmanifesten))
    manifest = iiifmanifesten[x]

    try:
        response = urlopen(manifest)
    except ValueError:
        return image(request)
    except HTTPError:
        return image(request)
    else:
        print(response)
        data_json = json.loads(response.read())
        print(data_json)
        iiif_manifest = data_json["sequences"][0]['canvases'][0]["images"][0]["resource"]["@id"]
        print(iiif_manifest)
        label = data_json["label"]['@value']
        print(label)
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
        print(instelling)            
        return render(request, 'image.html', {'iiif_manifest': iiif_manifest, 'instelling': instelling, 'label': label})






    