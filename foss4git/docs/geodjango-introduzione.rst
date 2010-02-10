========================
Introduzione a GeoDjango
========================

* **Django**: The Web framework for perfectionists with deadlines
* **GeoDjango**: The Geographic Web Framework for perfectionists with deadlines
* dalla versione 1.0 di Django fa parte dei **core packages** disponibili di base
* è un insieme di API, utility e tool che consente di creare GIS application con Django
* come Django puo' essere utilizzato sia in ambito **web** che in ambito **desktop**


Indice
======

* Architettura GeoDjango

* Panoramica delle funzionalità disponibili con GeoDjango
    * GeoDjango Model API
    * GEOS API
    * GDAL/OGR API
    * Measurement Units API
    * GeoModelAdmin
    * Utilities (LayerMapping, OgrInspect)
    
* Tutorial!

Architettura GeoDjango
======================

* Spatial Database
    * PostGis
    * Spatialite
    * MySql Spatial
    * Oracle Spatial
* GIS Libraries
    * GEOS (Geometry Engine Open Source)
    * GDAL/OGR (Geospatial Data Abstraction Library)
    * PROJ.4 (Cartographic Projections Library)
    * GeoIP


Panoramica delle funzionalita' disponibili con GeoDjango
========================================================

* 1. GeoDjango Model API (Geometry Field, GeoManager, geo-CRUD)
* 2. GEOS API (operatori spaziali secondo OGC Simple Feature)
* 3. GDAL OGR API (accesso a dati esterni)
* 4. Measurement Units API
* 5. GeoModelAdmin
* 6. Alcune utilities: LayerMapping, OgrInspect
* ed altro ancora (GeoIP API, Geographic Feeds, ...)


1.1 GeoDjango Model API (Geometry Field e GeoManager)
=====================================================

    Geometry Field (django.contrib.gis.db estende django.db)
    
* PointField, LineStringField, PolygonField
* MultiPointField, MultiLineStringField, MultiPolygonField
* GeometryCollectionField
* GeometryField <novità 1.2>

    Opzioni Geometry Field
    
* **srid** (default 4326, ovvero WGS84 dd)
* **dim** (default 2, con 3 supporto z) <novità 1.2>
* **spatial_index** (default True, crea l'indice spaziale)


1.2 GeoDjango Model API (Geometry Field e GeoManager)
=====================================================

    Nel modello ho a disposizione Geographic Field e GeoManager

.. sourcecode:: python

    from django.contrib.gis.db import models
    
    class Provincia(models.Model):
        """Modello spaziale per rappresentare le regioni"""
        codice = models.IntegerField()
        nome = models.CharField(max_length=50)
        geometry = models.MultiPolygonField(srid=4326) 
        objects = models.GeoManager()

        
1.3 GeoDjango Model API (Geometry Field e GeoManager)
=====================================================

.. sourcecode:: bash

    $ ./manage.py sqlall fauna

.. sourcecode:: sql

    BEGIN;
    CREATE TABLE "fauna_regione" (
        "id" serial NOT NULL PRIMARY KEY,
        "codice" integer NOT NULL,
        "nome" varchar(50) NOT NULL
    )
    ;
    SELECT AddGeometryColumn('fauna_regione', 'geometry', 4326, 'MULTIPOLYGON', 2);
    ALTER TABLE "fauna_regione" ALTER "geometry" SET NOT NULL;
    CREATE INDEX "fauna_regione_geometry_id" 
        ON "fauna_regione" USING GIST ( "geometry" GIST_GEOMETRY_OPS );
    COMMIT;

    
1.4 Metodi CRUD: Create, Update
===============================

    GeoDjango estende l'API di Django abilitandolo spazialmente     

.. sourcecode:: python

    >>> from fauna.models import *
    >>> new_point = SandboxLayer(nome='punto 1', geometry='POINT(13.8 42.5)')
    >>> new_point.save()
    >>> print(connection.queries[-1])
    {'time': '0.061', 'sql': 'INSERT INTO "fauna_sandboxlayer" ("nome", "geometry") 
    VALUES (E\'punto 1\', ST_GeomFromEWKB(E\'\\\\001\\\\...'))'}

.. sourcecode:: python 
        
    >>> new_point = SandboxLayer.objects.get(nome__contains='pun')
    >>> new_point.nome = 'punto 2'     
    >>> new_point.save()
    >>> print(connection.queries[-1])
    {'time': '0.002', 'sql': 'UPDATE "fauna_sandboxlayer" SET "nome" = E\'punto 2\', 
        "geometry" = ST_GeomFromEWKB(E\'\\\\001\\\\...') 
        WHERE "fauna_sandboxlayer"."id" = 1 '}
 
        
1.5 Metodi CRUD: Read, Delete
=============================

.. sourcecode:: python

    >>> avvistamento = Avvistamento.objects.get(id=1)
    >>> regione = Regione.objects.filter(geometry__intersects=avvistamento.geometry)
    >>> regione
    [<Regione: ABRUZZO>]
    >>> print(connection.queries[-1])
    {'time': '0.187', 'sql': 'SELECT "fauna_regione"."id", "fauna_regione"."codice", 
        "fauna_regione"."nome", "fauna_regione"."geometry" 
        FROM "fauna_regione" WHERE ST_Intersects("fauna_regione"."geometry", 
        ST_GeomFromEWKB(E\'\\\\001\...')) LIMIT 21'}
        
.. sourcecode:: python

    >>> sandfeat = SandboxLayer.objects.get(id=1)
    >>> sandfeat.delete()
    >>> print(connection.queries[-1])
    {'time': '0.002', 'sql': 'DELETE FROM "fauna_sandboxlayer" WHERE "id" IN (1)'}
    >>> SandboxLayer.objects.all().delete()
    >>> print(connection.queries[-2])
    {'time': '0.002', 'sql': 'DELETE FROM "fauna_sandboxlayer" WHERE "id" IN (3, 2)'}
 
   
2. GEOS API: Simple Feature Access
==================================

    **GEOS** È un' implementazione delle spatial predicate functions e degli spatial operators
    secondo specifiche OGC "Simple Features for SQL"
    
L'interfaccia GEOS in GeoDjango offre principalmente due vantaggi
    
    * 1. mapping delle geometrie secondo le specifiche OGC Simple Feature Access
    * 2. funzionalità geometriche, topologiche e di geoprocessing
    
    
2.1 GEOS API: Simple Feature Access
===================================

    1. API per il mapping delle geometrie secondo le specifiche OGC Simple Feature Access
    
* Point
* LineString, LinearRing
* Polygon
* Geometry Collections (MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)


2.2 GEOS API: Funzionalità geometriche e topologiche
====================================================

    2. Funzionalità geometriche e topologiche

* **Proprietà geometriche** (empty, geom_type, hasz, num_coords, simple, valid...)
* **Proprietà rappresentative** (ewkt, hex, hexewkb, json, geojson, kml, ogr, wkb, ewkb, wkt)
* **Predicati spaziali e topologici** (contains, crosses, equals, intersects, touches, within, ...)
* **Metodi di geoprocessing** (buffer, difference, intersection, simplify, union, ...)
* **Altre proprietà e metodi** (centroid, envelope, area, distance, length, srs, transform)


2.3 GEOS API: Esempio 1
=======================

    Mapping delle geometrie (point), proprietà geometriche (hasz, geom_type)
    e proprietà rappresentative 

.. sourcecode:: python

    >>> from fauna.models import *
    >>> avvistamento = Avvistamento.objects.get(id=1)
    >>> point = avvistamento.geometry
    >>> point.x, point.y
    (13.798828125, 42.5390625)
    >>> point.hasz
    False
    >>> point.geom_type
    'Point'
    >>> point.json
    '{ "type": "Point", "coordinates": [ 13.798828, 42.539062 ] }'
    >>> point.ewkt # extended wkt
    'SRID=4326;POINT (13.7988281250000000 42.5390625000000000)'


2.4 GEOS API: Esempio 2
=======================    

    Predicati spaziali, trasformazioni (richiede GDAL), metodi di geoprocessing
    
.. sourcecode:: python
    
    >>> from fauna.models import *
    >>> abruzzo = Regione.objects.get(nome='ABRUZZO')
    >>> avvistamento = Avvistamento.objects.get(id=1)
    >>> abruzzo.geometry.contains(avvistamento.geometry)
    True
    >>> avvistamento.geometry.ewkt
    'SRID=4326;POINT (13.7988281250000000 42.5390625000000000)'
    >>> transformed_point = avvistamento.geometry.transform(3395,clone=True)
    >>> transformed_point.ewkt
    'SRID=3395;POINT (1536078.5204189007636160 5213176.4834084874019027)'
    >>> buffer = SandboxLayer(nome='buffer',geometry=transformed_point.buffer(20000))
    >>> buffer.save()

    
3. GDAL OGR API
===============

    L'interfaccia di GeoDjango con GDAL (Geospatial Data Abstraction Library), 
    mediante la libreria OGR (Simple Feature library) permette di leggere/scrivere numerosi
    formati vettoriali
    
Caratteristiche:

* è **facoltativa** per GeoDjango (obbligatoria per accesso a srs e trasformazioni e per LayerMapping)
* permette, mediante la classe di ingresso **DataSource**, l'accesso a tutti i formati **OGR**, in molti casi in lettura/scrittura
* consente l'accesso alle informazioni sulle **feature** che compongono il DataSource
* nelle funzionalità è simile alla combinazione dell'API di GeoDjango e GEOS viste in precedenza
* è possibile ottenere una **GEOSGeometry** mediante il metodo geos di **OGRGeometry**
* oppure si possono usare le proprietà rappresentative (wkt, wkb, json, ...)


3.1 GDAL OGR API: un esempio
============================

.. sourcecode:: python

    >>> from django.contrib.gis.gdal import *
    >>> ds = DataSource('data/shapefile/regioni.shp')
    >>> print(ds)
    data/shapefile/regioni.shp (ESRI Shapefile)
    >>> print(len(ds))
    1
    >>> lyr = ds[0]
    >>> print(lyr)
    regioni
    >>> print(lyr.num_feat)
    20
    >>> print(lyr.geom_type)
    Polygon
    >>> print(lyr.srs.srid)
    4326


3.1 GDAL OGR API: un esempio (segue)
====================================

.. sourcecode:: python

    >>> print(lyr.fields)
    ['gid', 'objectid', 'regione', 'cod_rip1', 'cod_rip2', 'cod_reg', 'shape_area', 'shape_len', 'boundingbo']
    >>> for feat in lyr:
       ....:        print(feat.get('regione'), feat.geom.num_points)
       ....: 
    PIEMONTE 14811
    VALLE D'AOSTA 3598
    ...
    LOMBARDIA 14909
    LAZIO 19131
    >>> feat = lyr[1]
    >>> print(feat.get('regione'))
    VALLE D'AOSTA
    >>> geom = feat.geom # OGRGeometry, non GEOSGeometry 
    >>> print(geom.srid)
    4326
    >>> print(feat.geom.wkt[:100])
    MULTIPOLYGON (((8.439415832216145 46.465900481500874,8.439484266241374 46.465576832714113,8.43950386


4. Measurement Units API
========================

    Un API per gestire in maniera immediata le operazioni e le conversioni tra unità di misura

.. sourcecode:: python

    >>> from django.contrib.gis.measure import Distance
    >>> d1 = Distance(km=5)
    >>>  print d1
    5.0 km
    >>>  print d1.mi
    3.10685596119
    >>>  d2 = Distance(mi=5)
    >>>  print d1 + d2
    13.04672 km
    >>>  a = d1 * d2
    print a
    40.2336 sq_km
    
    
5. GeoModelAdmin
================

.. sourcecode:: python

    from django.contrib import admin
    from django.contrib.gis.admin import GeoModelAdmin
    from models import *

    class AvvistamentoAdmin(GeoModelAdmin):

        model = Avvistamento

        list_display = ['data', 'animale', 'interesse']
        list_filter = ['data', 'animale', 'interesse']
        date_hierarchy = 'data'
        fieldsets = (
          ('Caratteristiche avvistamento', {'fields': (('data', 'animale', 'note', 'interesse'))}),
          ('Mappa', {'fields': ('geometry',)}),
        )

        # Openlayers settings
        scrollable = False
        map_width = 500
        map_height = 500
        openlayers_url = '/static/openlayers/lib/OpenLayers.js'
        default_zoom = 6
        default_lon = 13
        default_lat = 42
        
    admin.site.register(Avvistamento, AvvistamentoAdmin)
    
    
6 Alcune utilities
==================

    GeoDjango mette a disposizione alcune utility

* LayerMapping per importare dati sullo spatialdb
* OgrInspect per generare il mapping necessario a LayerMapping
* OgrInspect può anche generare un modello a partire da un dato OGR


6.1 Utility per importazione dati OGR: LayerMapping
===================================================

.. sourcecode:: python

    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from django.contrib.gis.utils import mapping, LayerMapping
    from fauna.models import Regione, Provincia

    print 'carico regioni...'

    regioni_mapping = {
        'codice' : 'cod_reg',
        'nome' : 'regione',
        'geometry' : 'MULTIPOLYGON',
    }
    
    regioni_shp = 'data/shapefile/regioni.shp'
    regioni =  LayerMapping(model=Regione, data_source=regioni_shp, mapping=regioni_mapping, 
        transform=False, encoding='iso-8859-1')
    regioni.save(verbose=True, progress=True)
    
    
6.2 Utility per importazione dati: OgrInspect
=============================================

.. sourcecode:: bash

    $ ./manage.py ogrinspect data/shapefile/regioni.shp Regione --srid=4326 --mapping --multi
    
* --srid setta il SRID del campo geografico
* --mapping richiede la generazione del mapping dictionary da usare con LayerMapping
* --multi impone il campo come multi geometrico (ad es come MultiPolygonField invece di PolygonField)


6.3 Output di OgrInspect
========================

    OgrInspect genera il codice necessario per il modello e per il mapping
    
.. sourcecode:: python

    # This is an auto-generated Django model module created by ogrinspect.
    from django.contrib.gis.db import models

        class Regione(models.Model):
            gid = models.IntegerField()
            objectid = models.IntegerField()
            regione = models.CharField(max_length=255)
            ...
            geom = models.MultiPolygonField(srid=4326)
            objects = models.GeoManager()

        # Auto-generated `LayerMapping` dictionary for Regione model
        regione_mapping = {
            'gid' : 'gid',
            'objectid' : 'objectid',
            'regione' : 'regione',
            ...
            'geom' : 'MULTIPOLYGON',
        }


Tutorial
========

A partire dall'applicazione creata in precedenza:

* 1. attivazione di GeoDjango
* 2. aggiunta del campo geografico e del GeoManager nel modello
* 3. GeoModelAdmin: gestione di dati geografici con l'admin
* 4. importazione di dati da altri formati con LayerMapping
* 5. l'utility ogrinspect
* 6. creazione di una vista che espone il kml delle geometrie
* 7. creazione di una mappa dell'italia e caricamento del kml con OpenLayers
* 8. creazione di una vista regionale e caricamento dei dati appartenenti a una regione
* 9. creazione di un modello sandbox per testare le API di GeoDjango
* 10. uso dell'API: metodi CRUD
* 11. uso dell'API GEOS
* 12. uso dell'API GDAL/OGR
* 13. uso dell'API Measurement Units

1. Attivazione di GeoDjango
===========================

    GeoDjango è un'applicazione Django

(settings.py)

.. sourcecode:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.admin',
        'django.contrib.gis',
    )

2.1 Aggiunta del campo geografico e del GeoManager nel modello
==============================================================

Eliminare la tabella fauna_avvistamento (va rigenerata con il nuovo campo)

Inserire il campo geografico e il GeoManager nel modello

(fauna/models.py)

.. sourcecode:: python

    from django.db import models
    from django.contrib.gis.db import models as gismodels

    class Avvistamento(gismodels.Model):
        """Modello spaziale per rappresentare gli avvistamenti"""
        data = gismodels.DateTimeField()
        note = gismodels.TextField(blank=True, null=True)
        animale = gismodels.ForeignKey(Animale)
        geometry = gismodels.PointField(srid=4326)
        objects = gismodels.GeoManager()
        
2.2 Aggiunta del campo geografico e del GeoManager nel modello
==============================================================

    Verifichiamo l'output e sincronizziamo
    
.. sourcecode:: bash

    $ ./manage.py sqlall fauna
    
    BEGIN;
    ...
    CREATE TABLE "fauna_avvistamento" (
        "id" serial NOT NULL PRIMARY KEY,
        "data" timestamp with time zone NOT NULL,
        "note" text,
        "animale_id" integer NOT NULL REFERENCES "fauna_animale" ("id") DEFERRABLE INITIALLY DEFERRED
    )
    ;
    CREATE INDEX "fauna_avvistamento_animale_id" ON "fauna_avvistamento" ("animale_id");
    SELECT AddGeometryColumn('fauna_avvistamento', 'geometry', 4326, 'POINT', 2);
    ALTER TABLE "fauna_avvistamento" ALTER "geometry" SET NOT NULL;
    CREATE INDEX "fauna_avvistamento_geometry_id" ON "fauna_avvistamento" USING GIST ( "geometry" GIST_GEOMETRY_OPS );
    COMMIT;
    
    ./manage.py syncdb
    Creating table fauna_avvistamento
    Installing index for fauna.Avvistamento model
    
3. GeoModelAdmin: gestione di dati geografici con l'admin
=========================================================

(fauna/admin.py)

.. sourcecode:: python    
    
    from django.contrib.gis.admin import GeoModelAdmin

    class AvvistamentoAdmin(GeoModelAdmin):

        model = Avvistamento

        list_display = ['data', 'animale']
        list_filter = ['data', 'animale']
        date_hierarchy = 'data'
        fieldsets = (
          ('Caratteristiche avvistamento', {'fields': (('data', 'animale', 'note',))}),
          ('Mappa', {'fields': ('geometry',)}),
        )
        # Openlayers settings
        scrollable = False
        map_width = 500
        map_height = 500
        #openlayers_url = '/static/openlayers/lib/OpenLayers.js'
        default_zoom = 6
        default_lon = 13
        default_lat = 42

4.1 Importazione di dati da altri formati con LayerMapping
==========================================================

    Analizziamo il dato da importare con ogrinfo (usando l'opzione
    -so = summary only)
    
.. sourcecode:: bash

    $ ogrinfo -so data/shapefile/regioni.shp
    INFO: Open of `data/shapefile/regioni.shp'
          using driver `ESRI Shapefile' successful.
    1: regioni (Polygon)
    $ ogrinfo -so data/shapefile/regioni.shp regioni
    ...
    Layer name: regioni
    Geometry: Polygon
    Feature Count: 20
    Extent: (6.627586, 35.493472) - (18.521529, 47.093684)
    Layer SRS WKT:
    GEOGCS["WGS 84",...
    gid: Integer (10.0)
    objectid: Integer (10.0)
    regione: String (255.0)
    ...
    
4.2 Importazione di dati da altri formati con LayerMapping
==========================================================

    Creiamo il modello con i campi che abbiamo deciso di importare,
    analizziamo gli oggetti che verranno prodotti sul db e sincronizziamo
    
(fauna/models.py)

.. sourcecode:: python
    
    class Regione(gismodels.Model):
        """Modello spaziale per rappresentare le regioni"""
        codice = gismodels.IntegerField()
        nome = gismodels.CharField(max_length=50)
        geometry = gismodels.MultiPolygonField(srid=4326) 
        objects = gismodels.GeoManager()

        def __unicode__(self):
            return '%s' % (self.nome)
            

4.3 Importazione di dati da altri formati con LayerMapping
==========================================================

    Creiamo uno script di importazione

(carica_dati.py)

.. sourcecode:: python

    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from django.contrib.gis.utils import mapping, LayerMapping
    from fauna.models import Regione

    print 'carico regioni...'

    regioni_mapping = {
        'codice' : 'cod_reg',
        'nome' : 'regione',
        'geometry' : 'MULTIPOLYGON',
    }
    
    regioni_shp = 'data/shapefile/regioni.shp'
    regioni =  LayerMapping(Regione, regioni_shp, regioni_mapping, transform=False, encoding='iso-8859-1')
    regioni.save(verbose=True, progress=True)
    

5. l'utility ogrinspect
=======================

questa utility consente di:

    * autogenerare il codice per la definizione del modello a partire da un layer ogr
    * autogenerare il dizionario necessario per il LayerMapping che abbiamo usato nello script di importazione
    
.. sourcecode:: bash

    $ ./manage.py ogrinspect data/shapefile/regioni.shp Regione --srid=4326 --multi --mapping

    # This is an auto-generated Django model module created by ogrinspect.
    from django.contrib.gis.db import models

    class Regione(models.Model):
        gid = models.IntegerField()
        objectid = models.IntegerField()
        ...
        geom = models.MultiPolygonField(srid=4326)
        objects = models.GeoManager()

    # Auto-generated `LayerMapping` dictionary for Regione model
    regione_mapping = {
        'gid' : 'gid',
        'objectid' : 'objectid',
        ...
        'geom' : 'MULTIPOLYGON',
    }
    

6. creazione di una vista che espone il kml delle geometrie
===========================================================

(urls.py)

.. sourcecode:: python
    
    urlpatterns = patterns('',
        ...
        (r'^admin/', include(admin.site.urls)),
        # indirizzi non soggetti ad autenticazione
        (r'^avvistamenti/', avvistamenti),
        (r'^kml/', all_kml),
        ...

(fauna/views.py)

.. sourcecode:: python   
    
    from django.shortcuts import render_to_response, get_object_or_404
    from django.contrib.gis.shortcuts import render_to_kml
    from fauna.models import *

    def all_kml(request):
        """vista per generare il kml di tutti i punti di avvistamento"""
        avvistamenti  = Avvistamento.objects.kml()
        return render_to_kml("gis/kml/placemarks.kml", {'places' : avvistamenti})


7.1 creazione di una mappa dell'italia e caricamento del kml con OpenLayers
===========================================================================

(urls.py)

.. sourcecode:: python

    urlpatterns = patterns('',
        ...:
        (r'^admin/', include(admin.site.urls)),
        # indirizzi non soggetti ad autenticazione
        (r'^avvistamenti/', avvistamenti),
        (r'^kml/', all_kml),
        (r'^$', italia),
        ...

(fauna/views.py)

.. sourcecode:: python

    def italia(request):
        """vista con zoom su italia e il numero dei punti di avvistamento inseriti nel sistema"""
        num_avvistamenti = Avvistamento.objects.all().count()
        return render_to_response('italia.html', {'num_avvistamenti' : num_avvistamenti})
        
        
7.1 creazione di una mappa dell'italia e caricamento del kml con OpenLayers
===========================================================================

(fauna/templates/italia.html)

.. sourcecode:: html

    <html>
      <head>
        <script src="/static/openlayers/lib/OpenLayers.js"></script>
        <style type="text/css"> #map { width:500px; height: 500px; } </style>
        <script type="text/javascript">
            var map, base_layer, kml;
            var ms_url = "http://localhost/cgi-bin/mapserv?map=/home/geodjango/tutorial/django-1.2-alpha-1-env/geodjango-tutorial/foss4git/mapserver/italia.map&"
            function init(){
                map = new OpenLayers.Map('map');
                base_layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                   "http://labs.metacarta.com/wms/vmap0", {layers: 'basic'} );
                var regioni = new OpenLayers.Layer.WMS("Regioni",
                   ms_url, {layers : 'regioni'} );
                kml = new OpenLayers.Layer.GML("KML", "/kml", 
                   { format: OpenLayers.Format.KML });
                map.addLayers([base_layer, regioni, kml]);
                map.addControl(new OpenLayers.Control.LayerSwitcher());
                map.setCenter(new OpenLayers.LonLat(13,42),6); 
                }
        </script>
      </head>
      <body onload="init()">
        <h3>Avvistamenti in Italia</h3>
        <div id="map"></div>
        <p>Sono stati inseriti {{num_avvistamenti}} avvistamenti.</p>
      </body>
    </html>


8.1 creazione di una vista regionale e caricamento dei dati appartenenti a una regione
======================================================================================

(urls.py)

.. sourcecode:: python

    urlpatterns = patterns('',
        ...:
        (r'^admin/', include(admin.site.urls)),
        # indirizzi non soggetti ad autenticazione
        (r'^avvistamenti/', avvistamenti),
        (r'^kml/', all_kml),
        (r'^$', italia),
        (r'^regione/(?P<id>[0-9]*)/', regione),
        ...

(fauna/views.py)

.. sourcecode:: python

    def regione(request, id):
        """vista con zoom su regione e l'elenco dei punti di avvistamento inseriti nel sistema per la regione in questione"""
        regione = get_object_or_404(Regione, codice=id)
        avvistamenti = Avvistamento.objects.filter(geometry__intersects=regione.geometry)
        return render_to_response("regione.html", { 'regione': regione, 'avvistamenti': avvistamenti })
        
        
8.2 creazione di una mappa dell'italia e caricamento del kml con OpenLayers
===========================================================================

(fauna/templates/regione.html)

.. sourcecode:: html

    <html>
      <head>
        <script src="http://openlayers.org/api/OpenLayers.js"></script>
        <style type="text/css"> #map { width:400px; height: 400px; } </style>
        <script type="text/javascript">
            var map, base_layer, kml;
            var ms_url = "http://localhost/cgi-bin/mapserv?map=/home/geodjango/tutorial/django-1.2-alpha-1-env/geodjango-tutorial/foss4git/mapserver/italia.map&"
            function init(){
                map = new OpenLayers.Map('map');
                base_layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                   "http://labs.metacarta.com/wms/vmap0", {layers: 'basic'} );
                var regioni = new OpenLayers.Layer.WMS("Regioni",
                   ms_url, {layers : 'regioni'} );
                var format = new OpenLayers.Format.GeoJSON()
                regione = format.read({{ regione.geometry.geojson|safe}})[0]; 
                // We mark it 'safe' so that Django doesn't escape the quotes.
                regione.attributes = { 'nome': "{{regione.nome}}", 'type': 'regione'}; 
                vectors = new OpenLayers.Layer.Vector("Data");
                vectors.addFeatures(regione); 
                for (var i = 0; i < points.length; i++) {
                    point = format.read(points[i])[0]; 
                    point.attributes = {'type':'point'}; 
                    vectors.addFeatures(point);
                }
                map.addLayers([base_layer, regioni, vectors]);
                map.addControl(new OpenLayers.Control.LayerSwitcher());
                map.zoomToExtent(regione.geometry.getBounds());
    }
        </script>
      </head>
      <body onload="init()">
        <h3>Avvistamenti nella regione: {{ regione.nome}}</h3>
        <div id="map"></div>
        In questa regione ci sono stati {{avvistamenti.count}} avvistamenti.<br>
        <script> var points = []; </script>
        <ul>
        {% for avvistamento in avvistamenti %}
            <li>{{ avvistamento.data }}, {{ avvistamento.animale.nome }}</li>
            <script>points.push({{avvistamento.geometry.geojson|safe}});</script>
        {% endfor %}
        </ul>
      </body>
    </html>


9. creazione di un modello sandbox per testare le API di GeoDjango
==================================================================

(fauna/models.py)

.. sourcecode:: python

    class SandboxLayer(gismodels.Model):
        """Modello spaziale per effettuare test con l'API GeoDjango"""
        nome = gismodels.CharField(max_length=50)
        geometry = gismodels.GeometryField(srid=3395) # WGS84 mercatore
        objects = gismodels.GeoManager()

        def __unicode__(self):
            return '%s' % (self.nome)

10. uso delle API
=================
* uso dell'API: metodi CRUD
* uso dell'API GEOS
* uso dell'API GDAL/OGR
* uso dell'API Measurement Units
    
Risorse aggiuntive
==================

* sito progetto Django: http://www.djangoproject.com/
* sito progetto GeoDjango: http://geodjango.org/
* GeoDjango basic applications: http://code.google.com/p/geodjango-basic-apps/
* questo tutorial: (TODO)
    * http://github.com/capooti/geodjango-tutorial
    * http://github.com/elpaso/geodjango-tutorial




