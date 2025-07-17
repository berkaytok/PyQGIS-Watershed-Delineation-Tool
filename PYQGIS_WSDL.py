#!/usr/bin/env python3
"""
QGIS Watershed Delineation Automation Script
This script automates watershed delineation using PyQGIS and SAGA GIS tools.
"""

import sys
import os
from qgis.core import *
from qgis.analysis import *
from qgis.PyQt.QtCore import QVariant
import processing
from processing.core.Processing import Processing

class WatershedDelineator:
    def __init__(self, project_path=None):
        """
        Initialize the watershed delineator
        
        Args:
            project_path (str): Path to QGIS project file (optional)
        """
        # Initialize QGIS application
        QgsApplication.setPrefixPath("/usr", True)
        self.qgs = QgsApplication([], False)
        self.qgs.initQgis()
        
        # Initialize processing
        Processing.initialize()
        
        # Load project if provided
        if project_path and os.path.exists(project_path):
            self.project = QgsProject.instance()
            self.project.read(project_path)
        else:
            self.project = QgsProject.instance()
    
    def load_dem(self, dem_path):
        """
        Load Digital Elevation Model (DEM) raster
        
        Args:
            dem_path (str): Path to DEM raster file
            
        Returns:
            QgsRasterLayer: Loaded DEM layer
        """
        if not os.path.exists(dem_path):
            raise FileNotFoundError(f"DEM file not found: {dem_path}")
        
        dem_layer = QgsRasterLayer(dem_path, "DEM")
        if not dem_layer.isValid():
            raise ValueError(f"Invalid DEM layer: {dem_path}")
        
        QgsProject.instance().addMapLayer(dem_layer)
        print(f"DEM loaded successfully: {dem_path}")
        return dem_layer
    
    def load_pour_points(self, points_path):
        """
        Load pour points (outlet points) for watershed delineation
        
        Args:
            points_path (str): Path to pour points shapefile or layer
            
        Returns:
            QgsVectorLayer: Loaded pour points layer
        """
        if not os.path.exists(points_path):
            raise FileNotFoundError(f"Pour points file not found: {points_path}")
        
        points_layer = QgsVectorLayer(points_path, "Pour Points", "ogr")
        if not points_layer.isValid():
            raise ValueError(f"Invalid pour points layer: {points_path}")
        
        QgsProject.instance().addMapLayer(points_layer)
        print(f"Pour points loaded successfully: {points_path}")
        return points_layer
    
    def fill_sinks(self, dem_layer, output_path):
        """
        Fill sinks in DEM using SAGA Fill Sinks algorithm
        
        Args:
            dem_layer (QgsRasterLayer): Input DEM layer
            output_path (str): Output path for filled DEM
            
        Returns:
            str: Path to filled DEM
        """
        print("Filling sinks in DEM...")
        
        params = {
            'DEM': dem_layer,
            'RESULT': output_path
        }
        
        result = processing.run('saga:fillsinks', params)
        print(f"Sinks filled successfully: {output_path}")
        return result['RESULT']
    
    def calculate_flow_direction(self, filled_dem_path, output_path):
        """
        Calculate flow direction from filled DEM
        
        Args:
            filled_dem_path (str): Path to filled DEM
            output_path (str): Output path for flow direction raster
            
        Returns:
            str: Path to flow direction raster
        """
        print("Calculating flow direction...")
        
        params = {
            'ELEVATION': filled_dem_path,
            'DIRECTION': output_path
        }
        
        result = processing.run('saga:flowdirection', params)
        print(f"Flow direction calculated: {output_path}")
        return result['DIRECTION']
    
    def calculate_flow_accumulation(self, flow_direction_path, output_path):
        """
        Calculate flow accumulation from flow direction
        
        Args:
            flow_direction_path (str): Path to flow direction raster
            output_path (str): Output path for flow accumulation raster
            
        Returns:
            str: Path to flow accumulation raster
        """
        print("Calculating flow accumulation...")
        
        params = {
            'DIRECTION': flow_direction_path,
            'ACCUMULATION': output_path
        }
        
        result = processing.run('saga:flowaccumulation', params)
        print(f"Flow accumulation calculated: {output_path}")
        return result['ACCUMULATION']
    
    def create_stream_network(self, flow_accumulation_path, threshold, output_path):
        """
        Create stream network from flow accumulation
        
        Args:
            flow_accumulation_path (str): Path to flow accumulation raster
            threshold (float): Threshold value for stream initiation
            output_path (str): Output path for stream network
            
        Returns:
            str: Path to stream network raster
        """
        print(f"Creating stream network with threshold: {threshold}")
        
        params = {
            'INPUT': flow_accumulation_path,
            'THRESHOLD': threshold,
            'OUTPUT': output_path
        }
        
        result = processing.run('saga:streamnetwork', params)
        print(f"Stream network created: {output_path}")
        return result['OUTPUT']
    
    def delineate_watersheds(self, flow_direction_path, pour_points_layer, output_path):
        """
        Delineate watersheds from flow direction and pour points
        
        Args:
            flow_direction_path (str): Path to flow direction raster
            pour_points_layer (QgsVectorLayer): Pour points layer
            output_path (str): Output path for watershed polygons
            
        Returns:
            str: Path to watershed polygons
        """
        print("Delineating watersheds...")
        
        params = {
            'DIRECTION': flow_direction_path,
            'POINTS': pour_points_layer,
            'BASINS': output_path
        }
        
        result = processing.run('saga:watershedbasins', params)
        print(f"Watersheds delineated: {output_path}")
        return result['BASINS']
    
    def calculate_watershed_statistics(self, watershed_path, dem_layer):
        """
        Calculate basic statistics for delineated watersheds
        
        Args:
            watershed_path (str): Path to watershed polygons
            dem_layer (QgsRasterLayer): DEM layer for elevation statistics
            
        Returns:
            dict: Dictionary containing watershed statistics
        """
        print("Calculating watershed statistics...")
        
        watershed_layer = QgsVectorLayer(watershed_path, "Watersheds", "ogr")
        if not watershed_layer.isValid():
            raise ValueError(f"Invalid watershed layer: {watershed_path}")
        
        stats = {}
        features = watershed_layer.getFeatures()
        
        for i, feature in enumerate(features):
            geom = feature.geometry()
            area = geom.area()
            
            # Calculate zonal statistics for elevation
            zonal_stats = QgsZonalStatistics(
                watershed_layer, 
                dem_layer, 
                f"elev_", 
                1, 
                QgsZonalStatistics.All
            )
            zonal_stats.calculateStatistics(None)
            
            stats[f"watershed_{i}"] = {
                'area_sq_meters': area,
                'area_sq_km': area / 1000000,
                'perimeter_meters': geom.length()
            }
        
        return stats
    
    def run_complete_delineation(self, dem_path, pour_points_path, output_dir, 
                                stream_threshold=1000):
        """
        Run complete watershed delineation workflow
        
        Args:
            dem_path (str): Path to DEM raster
            pour_points_path (str): Path to pour points shapefile
            output_dir (str): Output directory for results
            stream_threshold (float): Threshold for stream network creation
            
        Returns:
            dict: Dictionary containing paths to all output files
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output file paths
        filled_dem = os.path.join(output_dir, "filled_dem.tif")
        flow_direction = os.path.join(output_dir, "flow_direction.tif")
        flow_accumulation = os.path.join(output_dir, "flow_accumulation.tif")
        stream_network = os.path.join(output_dir, "stream_network.tif")
        watersheds = os.path.join(output_dir, "watersheds.shp")
        
        try:
            # Load input data
            dem_layer = self.load_dem(dem_path)
            pour_points = self.load_pour_points(pour_points_path)
            
            # Step 1: Fill sinks
            self.fill_sinks(dem_layer, filled_dem)
            
            # Step 2: Calculate flow direction
            self.calculate_flow_direction(filled_dem, flow_direction)
            
            # Step 3: Calculate flow accumulation
            self.calculate_flow_accumulation(flow_direction, flow_accumulation)
            
            # Step 4: Create stream network
            self.create_stream_network(flow_accumulation, stream_threshold, stream_network)
            
            # Step 5: Delineate watersheds
            self.delineate_watersheds(flow_direction, pour_points, watersheds)
            
            # Step 6: Calculate statistics
            stats = self.calculate_watershed_statistics(watersheds, dem_layer)
            
            # Save statistics to file
            stats_file = os.path.join(output_dir, "watershed_statistics.txt")
            with open(stats_file, 'w') as f:
                f.write("Watershed Delineation Statistics\n")
                f.write("================================\n\n")
                for watershed_id, data in stats.items():
                    f.write(f"{watershed_id}:\n")
                    f.write(f"  Area: {data['area_sq_km']:.2f} sq km\n")
                    f.write(f"  Perimeter: {data['perimeter_meters']:.2f} meters\n\n")
            
            results = {
                'filled_dem': filled_dem,
                'flow_direction': flow_direction,
                'flow_accumulation': flow_accumulation,
                'stream_network': stream_network,
                'watersheds': watersheds,
                'statistics': stats_file
            }
            
            print("Watershed delineation completed successfully!")
            print(f"Results saved to: {output_dir}")
            
            return results
            
        except Exception as e:
            print(f"Error during watershed delineation: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up QGIS application"""
        self.qgs.exitQgis()

def main():
    """
    Main function to run the watershed delineation script
    """
    # Configuration - Update these paths according to data location
    DEM_PATH = "/path/to/your/dem.tif"
    POUR_POINTS_PATH = "/path/to/your/pour_points.shp"
    OUTPUT_DIR = "/path/to/output/directory"
    STREAM_THRESHOLD = 1000  # Adjust based on DEM resolution and area
    
    # Initialize delineator
    delineator = WatershedDelineator()
    
    try:
        # Run complete delineation workflow
        results = delineator.run_complete_delineation(
            DEM_PATH, 
            POUR_POINTS_PATH, 
            OUTPUT_DIR,
            STREAM_THRESHOLD
        )
        
        print("\n" + "="*50)
        print("DELINEATION RESULTS:")
        print("="*50)
        for key, value in results.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        
    finally:
        # Clean up
        delineator.cleanup()

if __name__ == "__main__":
    main()
