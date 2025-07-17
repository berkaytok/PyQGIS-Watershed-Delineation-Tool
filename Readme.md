# QGIS Watershed Delineation Automation Script

A comprehensive Python script for automating watershed delineation using PyQGIS and SAGA GIS algorithms. This tool streamlines the process of delineating watershed boundaries from Digital Elevation Models (DEMs) and pour points.

## 🌊 Overview

Watershed delineation is a fundamental process in hydrology that identifies the drainage area contributing flow to a specific outlet point. This script automates the entire workflow, from DEM preprocessing to final watershed polygon creation, making it easy to process multiple watersheds consistently.

## ✨ Features

- **Complete Hydrological Workflow**: Automated sink filling, flow direction, flow accumulation, and stream network generation
- **Batch Processing Ready**: Process multiple watersheds with consistent parameters
- **Statistical Analysis**: Automatic calculation of watershed metrics (area, perimeter, elevation statistics)
- **Error Handling**: Robust error handling and validation for all processing steps
- **Flexible Output**: Multiple output formats and detailed logging
- **SAGA Integration**: Leverages proven SAGA GIS algorithms through QGIS processing

## 📋 Requirements

### Software Dependencies
- **QGIS 3.x** with PyQGIS support
- **SAGA GIS** (integrated with QGIS)
- **Python 3.x** (usually bundled with QGIS)

### Python Libraries
```
qgis.core
qgis.analysis
qgis.PyQt.QtCore
processing
```

### Input Data Requirements
- **Digital Elevation Model (DEM)**: Raster format (GeoTIFF recommended)
- **Pour Points**: Vector shapefile with outlet locations
- **Coordinate System**: Both inputs should be in the same projected coordinate system

## 🚀 Installation

### 1. Install QGIS
```bash
# Ubuntu/Debian
sudo apt-get install qgis qgis-plugin-grass saga

# Windows
# Download and install QGIS from https://qgis.org/
# SAGA GIS is typically bundled with QGIS installation

# macOS
brew install qgis
```

### 2. Verify SAGA Integration
Open QGIS and check that SAGA algorithms are available:
1. Go to `Processing` → `Toolbox`
2. Look for `SAGA` algorithms in the processing toolbox
3. If not available, install SAGA GIS separately

### 3. Download the Script
```bash
git clone <repository-url>
cd watershed-delineation
```

## 🔧 Configuration

### Basic Setup
Edit the configuration section in `main()` function:

```python
# Configuration - Update these paths according to your data
DEM_PATH = "/path/to/your/dem.tif"
POUR_POINTS_PATH = "/path/to/your/pour_points.shp"
OUTPUT_DIR = "/path/to/output/directory"
STREAM_THRESHOLD = 1000  # Adjust based on your DEM resolution and area
```

### Stream Threshold Guidelines
| DEM Resolution | Typical Threshold | Watershed Size |
|---------------|-------------------|----------------|
| 10m | 500-1000 | Small watersheds |
| 30m | 1000-5000 | Medium watersheds |
| 90m | 5000-10000 | Large watersheds |

### Pour Points Preparation
Your pour points shapefile should:
- Be in the same coordinate system as your DEM
- Contain point geometries at watershed outlets
- Have unique identifiers if processing multiple watersheds

## 🏃 Usage

### Basic Usage
```bash
python watershed_delineation.py
```

### Advanced Usage
```python
from watershed_delineation import WatershedDelineator

# Initialize
delineator = WatershedDelineator()

# Run complete workflow
results = delineator.run_complete_delineation(
    dem_path="/path/to/dem.tif",
    pour_points_path="/path/to/points.shp",
    output_dir="/path/to/output",
    stream_threshold=1000
)

# Access individual components
dem_layer = delineator.load_dem("/path/to/dem.tif")
filled_dem = delineator.fill_sinks(dem_layer, "/path/to/filled.tif")
```

### Command Line Arguments (Optional Enhancement)
```bash
python watershed_delineation.py --dem /path/to/dem.tif --points /path/to/points.shp --output /path/to/output --threshold 1000
```

## 📁 Output Files

The script generates the following outputs in your specified directory:

| File | Description | Format |
|------|-------------|---------|
| `filled_dem.tif` | Sink-filled Digital Elevation Model | GeoTIFF |
| `flow_direction.tif` | Flow direction raster (D8 algorithm) | GeoTIFF |
| `flow_accumulation.tif` | Flow accumulation values | GeoTIFF |
| `stream_network.tif` | Generated stream network | GeoTIFF |
| `watersheds.shp` | Delineated watershed polygons | Shapefile |
| `watershed_statistics.txt` | Statistical summary | Text |

### Statistics Output Example
```
Watershed Delineation Statistics
================================

watershed_0:
  Area: 156.42 sq km
  Perimeter: 87543.21 meters

watershed_1:
  Area: 89.73 sq km
  Perimeter: 52108.76 meters
```

## 🛠️ Workflow Details

### Step-by-Step Process
1. **Load Input Data**: Validate and load DEM and pour points
2. **Fill Sinks**: Remove spurious depressions in DEM
3. **Flow Direction**: Calculate D8 flow direction for each cell
4. **Flow Accumulation**: Compute accumulated flow for drainage network
5. **Stream Network**: Generate stream network using accumulation threshold
6. **Watershed Delineation**: Delineate watersheds from flow direction and outlets
7. **Statistics**: Calculate area, perimeter, and elevation statistics

### Algorithm Details
- **Sink Filling**: SAGA Fill Sinks algorithm
- **Flow Direction**: D8 single flow direction algorithm
- **Flow Accumulation**: Recursive flow accumulation
- **Stream Network**: Threshold-based stream initiation
- **Watershed Delineation**: Recursive watershed basin delineation

## 🔍 Troubleshooting

### Common Issues

**1. SAGA algorithms not found**
```
Error: Algorithm 'saga:fillsinks' not found
```
**Solution**: Install SAGA GIS and ensure it's integrated with QGIS

**2. Invalid DEM layer**
```
Error: Invalid DEM layer: /path/to/dem.tif
```
**Solution**: 
- Check file path and format
- Ensure DEM is in a projected coordinate system
- Verify DEM has valid elevation values

**3. Pour points outside DEM extent**
```
Error: Pour points outside DEM boundary
```
**Solution**: 
- Verify coordinate systems match
- Check spatial extent overlap
- Reproject data if necessary

**4. Memory issues with large DEMs**
```
Error: Insufficient memory for processing
```
**Solution**: 
- Tile large DEMs into smaller chunks
- Increase system memory
- Use lower resolution DEM for initial testing

### Performance Tips
- Use projected coordinate systems (UTM recommended)
- Ensure DEM resolution matches analysis scale
- Pre-process DEM to remove NoData values
- Use appropriate stream threshold values

## 🎯 Best Practices

### Data Preparation
1. **Coordinate Systems**: Use projected coordinate systems for accurate area calculations
2. **DEM Quality**: Remove artifacts and ensure proper elevation values
3. **Pour Point Placement**: Position outlets at stream intersections or known gauging stations
4. **Resolution**: Match DEM resolution to analysis scale and computational resources

### Parameter Tuning
1. **Stream Threshold**: Start with conservative values and adjust based on results
2. **Validation**: Compare results with known watershed boundaries
3. **Iterative Refinement**: Use multiple threshold values to find optimal settings

## 📊 Example Workflows

### Single Watershed Analysis
```python
delineator = WatershedDelineator()
results = delineator.run_complete_delineation(
    dem_path="data/study_area_dem.tif",
    pour_points_path="data/outlet_point.shp",
    output_dir="results/single_watershed",
    stream_threshold=1000
)
```

### Multiple Watershed Batch Processing
```python
watersheds = [
    {"dem": "data/area1_dem.tif", "points": "data/area1_points.shp"},
    {"dem": "data/area2_dem.tif", "points": "data/area2_points.shp"},
]

for i, watershed in enumerate(watersheds):
    results = delineator.run_complete_delineation(
        dem_path=watershed["dem"],
        pour_points_path=watershed["points"],
        output_dir=f"results/watershed_{i}",
        stream_threshold=1000
    )
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

### Development Setup
```bash
git clone <repository-url>
cd watershed-delineation
# Set up development environment
pip install -r requirements-dev.txt
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SAGA GIS development team for robust hydrological algorithms
- QGIS community for PyQGIS framework
- Contributors to open-source GIS ecosystem

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Consult QGIS and SAGA GIS documentation

## 🔄 Version History

- **v1.0.0**: Initial release with basic watershed delineation
- **v1.1.0**: Added statistical analysis and improved error handling
- **v1.2.0**: Enhanced batch processing capabilities

---

**Note**: This script requires a properly configured QGIS environment with SAGA GIS integration. Test with small datasets before processing large DEMs.