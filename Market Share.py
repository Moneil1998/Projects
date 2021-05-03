# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis import processing

# new imports
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsVectorLayerJoinInfo,
                       QgsWkbTypes,
                       QgsField,
                       QgsDistanceArea)

from PyQt5.QtGui import QColor                     # new
from qgis.utils import iface                       # new
from qgis.core import (QgsVectorLayer,             # new
                       QgsSymbol,                  # new
                       QgsRendererRange,           # new
                       QgsGraduatedSymbolRenderer, # new
                       QgsProcessingUtils)         # new

# change class name: ExampleProcessingAlgorithm to ProQgsAlgorithm
class ProQgsAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_POINT = 'INPUT_POINT'
    INPUT_POLYGON = 'INPUT_POLYGON'
    INPUT_TABLE = 'INPUT_TABLE'
    INPUT_DISTANCE = 'INPUT_DISTANCE'
    INPUT_FEATURE_JOIN_FLD = 'INPUT_FEATURE_JOIN_FLD'
    INPUT_TABLE_JOIN_FLD = 'INPUT_TABLE_JOIN_FLD'
    INPUT_OLD_AREA_FLD = 'INPUT_OLD_AREA_FLD'
    INPUT_POPULATION = 'INPUT_POPULATION'
    OUTPUT = 'OUTPUT'
    dest_id = None
    
    def createInstance(self):
        return ProQgsAlgorithm()
    def name(self):
        return 'MarketShare'
    def displayName(self):
        return self.tr('Market Share Algorithm')

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ProQgsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'MarketShare'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Market Share Algorithm')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Market Share')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterFeatureSource(            # data source: point features
                self.INPUT_POINT,
                self.tr('Input point layer'),
                types=[QgsProcessing.TypeVectorPoint]       # point features (works for dropdown list)
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(            # data source: polygon features
                self.INPUT_POLYGON,
                self.tr('Input polygon layer'),
                types=[QgsProcessing.TypeVectorPolygon]     # polygon features (works for dropdown list)
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_FEATURE_JOIN_FLD,
                self.tr('Polygon join field'),
                parentLayerParameterName=self.INPUT_POLYGON, # use fields from the polygon layer
                type=QgsProcessingParameterField.Any         # all fields will be listed
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_OLD_AREA_FLD,
                self.tr('Old area field'),
                parentLayerParameterName=self.INPUT_POLYGON, # use fields from the polygon layer
                type=QgsProcessingParameterField.Numeric     # only numeric fields
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(             # data source: a population table
                self.INPUT_TABLE,
                self.tr('Input population table'),
                types=[QgsProcessing.TypeVector]             # tables only (works for the dropdown list)
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_TABLE_JOIN_FLD,
                self.tr('Table join field'),
                parentLayerParameterName=self.INPUT_TABLE,   # use fields from the table
                type=QgsProcessingParameterField.Any         # all fields will show in the list
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_POPULATION,
                self.tr('Population field'),
                parentLayerParameterName=self.INPUT_TABLE,  # use fields from the table
                type=QgsProcessingParameterField.Numeric    # numeric fields only
            )
        )



        self.addParameter(
            QgsProcessingParameterFeatureSink(             # output: sink (see below)
                self.OUTPUT,
                self.tr('Output layer')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # get input layers
        source_point = self.parameterAsSource(parameters, self.INPUT_POINT, context)
        source_polygon = self.parameterAsSource(parameters, self.INPUT_POLYGON, context)
        source_table = self.parameterAsSource(parameters, self.INPUT_TABLE, context)
        if source_point is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_POINT))
        if source_polygon is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_POLYGON))
        if source_table is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_TABLE))
               
    
        # get other inputs
        old_area_field = self.parameterAsString(parameters, self.INPUT_OLD_AREA_FLD, context)
        feature_join_field = self.parameterAsString(parameters, self.INPUT_FEATURE_JOIN_FLD, context)
        table_join_fld = self.parameterAsString(parameters, self.INPUT_TABLE_JOIN_FLD, context)
        population_fld = self.parameterAsString(parameters, self.INPUT_POPULATION, context)
        
        layer = QgsVectorLayer(self.INPUT_POLYGON, 'INPUT_POLYGON','ogr')
        out_path = 'C:\\temp\\results\\'
        out_thiessen = out_path + 'thiessen.shp'
        
       
        bbox = '307028.17483411473222077, 4406586.43433339707553387, 349860.56330853456165642, 4445904.67834466695785522'
        processing.run("grass7:v.voronoi", {
            'input':                       parameters[self.INPUT_POINT],
            'GRASS_REGION_PARAMETER':      bbox,
            'GRASS_OUTPUT_TYPE_PARAMETER': 0,
            'output':                      out_thiessen})
        
        intersect= processing.run("qgis:intersection", {
            'INPUT': parameters[self.INPUT_POLYGON],
            'OVERLAY': out_thiessen , 
            'OUTPUT': 'memory:' }, context=context, feedback=feedback)['OUTPUT']
            
        # join
        joined = processing.run('qgis:joinattributestable', {
            'INPUT': intersect,
            'FIELD': feature_join_field,
            'INPUT_2': parameters[self.INPUT_TABLE],
            'FIELD_2': table_join_fld,
            'FIELDS_TO_COPY': [population_fld],
            'OUTPUT': 'memory:'}, context=context, feedback=feedback)['OUTPUT']
        
        # new area
        calculator = QgsDistanceArea()
        calculator.setEllipsoid('NAD83')
        lProvider = joined.dataProvider()
        lProvider.addAttributes([QgsField("AreaNew", QVariant.Double)])
        joined.updateFields()
        field_id = lProvider.fieldNameIndex('AreaNew')
        
        for f in joined.getFeatures():
            geom = f.geometry()
            area = 0
            if not geom.isMultipart(): # simple polygon
                polyg = geom.asPolygon()
                if len(polyg) > 0:
                    area = calculator.measurePolygon(polyg[0])
            else: # mutipolygon
                multi = geom.asMultiPolygon()
                for polyg in multi:
                    area = area + calculator.measurePolygon(polyg[0])
            lProvider.changeAttributeValues({f.id(): {field_id: area}})

        joined.updateFields()
        lProvider.addAttributes([QgsField("PopNew", QVariant.Double)])
        joined.updateFields()
        field_id = lProvider.fieldNameIndex('PopNew')
        # calculation proportion
        total = 0
        for f in source_table.getFeatures():
            total += f[population_fld]

        subtotal = 0
        for f in joined.getFeatures():
            subtotal = f[population_fld] * f['AreaNew']/f[old_area_field]
            lProvider.changeAttributeValues({f.id(): {field_id: subtotal}})
            subtotal=0
        
        joined.updateFields()
        
        # Dissolve by NAME field
        
        out_dissolve = out_path + 'dissolve.shp'
        dis = processing.run("gdal:dissolve",{
            'INPUT': joined,
            'FIELD': 'NAME',
            'GEOMETRY': 'geom',
            'COMPUTE_STATISTICS': 'sum',
            'STATISTICS_ATTRIBUTE':'PopNew',
            'OUTPUT': out_dissolve})
        
        layer_dissolved = QgsVectorLayer(out_dissolve, 'Dissolved','ogr')
        lProvider = layer_dissolved.dataProvider()
        lProvider.addAttributes([QgsField("Percent", QVariant.Double)])
        layer_dissolved.updateFields()
        field_id = lProvider.fieldNameIndex('Percent')
        
        for f in layer_dissolved.getFeatures():
            percent = (f['sum']/total)*100
            lProvider.changeAttributeValues({f.id(): {field_id: percent}})
        
        # get sink as output
        (sink, self.dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            layer_dissolved.fields(),
            QgsWkbTypes.Polygon,
            source_point.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
            
       
        # sink gets automatically loaded to canvas
        # we need this to add features from the output into the sink, otherwise sink will be empty
        
        for f in layer_dissolved.getFeatures():
            sink.addFeature(f)
        
        return {self.OUTPUT: self.dest_id}
        
    
    
    def postProcessAlgorithm(self, context, feedback):
        
        that_layer = QgsProcessingUtils.mapLayerFromString(self.dest_id, context)
        field='Percent'
        rangelist=[]
        symbol = QgsSymbol.defaultSymbol(that_layer.geometryType())  
     
        # Ranges from 0 to 3
        symbol = QgsSymbol.defaultSymbol(that_layer.geometryType())
        symbol.setColor(QColor("#deebf7"))                              
        range = QgsRendererRange(0.0,3.0, symbol, '0 to 3')                   
        rangelist.append(range)    
        
        # Ranges from 3 to 6
        symbol = QgsSymbol.defaultSymbol(that_layer.geometryType())
        symbol.setColor(QColor("#9ecae1"))                              
        range = QgsRendererRange(3.1,6.0, symbol, '3 to 6')                   
        rangelist.append(range)    

        # Ranges from 6 and >
        symbol = QgsSymbol.defaultSymbol(that_layer.geometryType())
        symbol.setColor(QColor("#3182bd"))                              
        range = QgsRendererRange(6.1,100, symbol, '> 6')                   
        rangelist.append(range)   
        
        myRenderer = QgsGraduatedSymbolRenderer(field, rangelist)  
        myRenderer.setMode(QgsGraduatedSymbolRenderer.Custom)               

        that_layer.setRenderer(myRenderer)   
        return {self.OUTPUT: self.dest_id}
        '''
        renderer1 = that_layer.renderer()
        symbol = renderer1.symbol()
        symbol.setColor(QColor.fromRgb(180, 180, 180))
        that_layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(that_layer.id()) # refresh treeview

        return {self.OUTPUT: self.dest_id}
        '''
        