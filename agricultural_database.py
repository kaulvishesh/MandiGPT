import json
from typing import Dict, List, Tuple
from models import Season, SoilType
from config import Config

class IndianAgriculturalDatabase:
    """Database containing Indian agricultural knowledge and crop data"""
    
    def __init__(self, crop_data_path="crop_data.json"):
        self.crop_data = self._initialize_crop_database(crop_data_path)
        self.regional_data = self._initialize_regional_data()
        self.seasonal_data = self._initialize_seasonal_data()
    
    def _initialize_crop_database(self, crop_data_path: str) -> Dict:
        """Initialize comprehensive crop database from a JSON file"""
        try:
            with open(crop_data_path, 'r') as f:
                data = json.load(f)

            # Convert string representations of enums to actual enum members
            for crop, details in data.items():
                if "seasons" in details:
                    details["seasons"] = [Season[season] for season in details["seasons"]]
                if "soil_types" in details:
                    details["soil_types"] = [SoilType[soil_type] for soil_type in details["soil_types"]]
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading crop data: {e}")
            return {}
    
    def _initialize_regional_data(self) -> Dict:
        """Initialize regional agricultural data for Indian states"""
        return {
            "Punjab": {
                "soil_type": SoilType.ALLUVIAL,
                "climate": "Semi-arid",
                "major_crops": ["Wheat", "Rice", "Cotton", "Sugarcane"],
                "irrigation_coverage": 95,
                "average_rainfall": 500
            },
            "Haryana": {
                "soil_type": SoilType.ALLUVIAL,
                "climate": "Semi-arid",
                "major_crops": ["Wheat", "Rice", "Cotton", "Sugarcane"],
                "irrigation_coverage": 90,
                "average_rainfall": 600
            },
            "Uttar Pradesh": {
                "soil_type": SoilType.ALLUVIAL,
                "climate": "Tropical",
                "major_crops": ["Wheat", "Rice", "Sugarcane", "Potato"],
                "irrigation_coverage": 70,
                "average_rainfall": 1000
            },
            "Maharashtra": {
                "soil_type": SoilType.BLACK,
                "climate": "Tropical",
                "major_crops": ["Sugarcane", "Cotton", "Soybean", "Onion"],
                "irrigation_coverage": 60,
                "average_rainfall": 800
            },
            "Gujarat": {
                "soil_type": SoilType.BLACK,
                "climate": "Arid",
                "major_crops": ["Cotton", "Groundnut", "Wheat", "Onion"],
                "irrigation_coverage": 50,
                "average_rainfall": 400
            },
            "Karnataka": {
                "soil_type": SoilType.RED,
                "climate": "Tropical",
                "major_crops": ["Maize", "Sugarcane", "Tomato", "Onion"],
                "irrigation_coverage": 40,
                "average_rainfall": 1200
            },
            "Tamil Nadu": {
                "soil_type": SoilType.RED,
                "climate": "Tropical",
                "major_crops": ["Rice", "Sugarcane", "Groundnut", "Cotton"],
                "irrigation_coverage": 80,
                "average_rainfall": 1000
            },
            "West Bengal": {
                "soil_type": SoilType.ALLUVIAL,
                "climate": "Tropical",
                "major_crops": ["Rice", "Potato", "Jute", "Tea"],
                "irrigation_coverage": 85,
                "average_rainfall": 1500
            }
        }
    
    def _initialize_seasonal_data(self) -> Dict:
        """Initialize seasonal agricultural data"""
        return {
            Season.KHARIF: {
                "months": ["June", "July", "August", "September", "October"],
                "description": "Monsoon season - suitable for crops requiring high rainfall",
                "typical_rainfall": 800,
                "temperature_range": (25, 35)
            },
            Season.RABI: {
                "months": ["October", "November", "December", "January", "February", "March"],
                "description": "Winter season - suitable for crops requiring moderate temperature",
                "typical_rainfall": 200,
                "temperature_range": (10, 25)
            },
            Season.ZAID: {
                "months": ["March", "April", "May"],
                "description": "Summer season - suitable for short duration crops",
                "typical_rainfall": 100,
                "temperature_range": (25, 40)
            }
        }
    
    def get_crop_suitability(self, crop: str, location: str, weather_conditions: Dict) -> float:
        """Calculate crop suitability score (0-1) based on location and weather"""
        if crop not in self.crop_data:
            return 0.0
        
        crop_info = self.crop_data[crop]
        score = 0.0
        factors = 0
        
        # Temperature suitability
        temp = weather_conditions.get("temperature", 25)
        temp_range = crop_info["temperature_range"]
        if temp_range[0] <= temp <= temp_range[1]:
            score += 1.0
        else:
            # Partial score based on how far from optimal range
            temp_diff = min(abs(temp - temp_range[0]), abs(temp - temp_range[1]))
            score += max(0, 1.0 - (temp_diff / 10))
        factors += 1
        
        # Rainfall suitability
        rainfall = weather_conditions.get("rainfall", 500)
        rain_range = crop_info["rainfall_requirement"]
        if rain_range[0] <= rainfall <= rain_range[1]:
            score += 1.0
        else:
            rain_diff = min(abs(rainfall - rain_range[0]), abs(rainfall - rain_range[1]))
            score += max(0, 1.0 - (rain_diff / 500))
        factors += 1
        
        # Humidity suitability
        humidity = weather_conditions.get("humidity", 60)
        humidity_range = crop_info["humidity_requirement"]
        if humidity_range[0] <= humidity <= humidity_range[1]:
            score += 1.0
        else:
            humidity_diff = min(abs(humidity - humidity_range[0]), abs(humidity - humidity_range[1]))
            score += max(0, 1.0 - (humidity_diff / 20))
        factors += 1
        
        # Regional suitability
        if location in self.regional_data:
            regional_info = self.regional_data[location]
            if crop in regional_info["major_crops"]:
                score += 1.0
            else:
                score += 0.5
        factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    def get_crop_info(self, crop: str) -> Dict:
        """Get detailed information about a specific crop"""
        return self.crop_data.get(crop, {})
    
    def get_regional_info(self, state: str) -> Dict:
        """Get agricultural information for a specific state"""
        return self.regional_data.get(state, {})
    
    def get_seasonal_crops(self, season: Season) -> List[str]:
        """Get crops suitable for a specific season"""
        suitable_crops = []
        for crop, data in self.crop_data.items():
            if season in data["seasons"]:
                suitable_crops.append(crop)
        return suitable_crops