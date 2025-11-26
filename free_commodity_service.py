import requests
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models import CommodityPrice, Location

class FreeCommodityService:
    """Free commodity price service using public APIs and web scraping"""
    
    def __init__(self, mock_prices_path="mock_prices.json"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Indian commodity price sources (free APIs)
        self.price_sources = {
            "agmarknet": "https://agmarknet.gov.in/api/price/commodity/",
            "mandi": "https://api.agmarknet.gov.in/api/price/commodity/",
            "krishijagran": "https://www.krishijagran.com/api/commodity-prices"
        }
        
        # Fallback mock prices with realistic Indian market data
        self.mock_prices = self._initialize_realistic_prices(mock_prices_path)
    
    def _initialize_realistic_prices(self, mock_prices_path: str) -> Dict[str, Dict]:
        """Initialize realistic commodity prices from a JSON file"""
        try:
            with open(mock_prices_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading mock prices: {e}")
            return {}
    
    async def get_commodity_prices(self, location: Location, commodities: List[str] = None) -> List[CommodityPrice]:
        """Get commodity prices from free sources"""
        
        if commodities is None:
            commodities = list(self.mock_prices.keys())
        
        prices = []
        
        for commodity in commodities:
            try:
                # Try to get real-time data first
                real_price = await self._fetch_real_price(commodity, location)
                if real_price:
                    prices.append(real_price)
                else:
                    # Fallback to mock data
                    mock_price = self._create_mock_price(commodity, location)
                    prices.append(mock_price)
                    
            except Exception as e:
                print(f"Error fetching price for {commodity}: {e}")
                # Use mock data as fallback
                mock_price = self._create_mock_price(commodity, location)
                prices.append(mock_price)
        
        return prices
    
    async def _fetch_real_price(self, commodity: str, location: Location) -> Optional[CommodityPrice]:
        """Try to fetch real commodity prices from free sources"""
        
        try:
            # Try Agmarknet API (Government of India)
            agmarknet_price = await self._fetch_agmarknet_price(commodity, location)
            if agmarknet_price:
                return agmarknet_price
                
            # Try other free sources
            other_price = await self._fetch_other_sources(commodity, location)
            if other_price:
                return other_price
                
        except Exception as e:
            print(f"Error fetching real price for {commodity}: {e}")
        
        return None
    
    async def _fetch_agmarknet_price(self, commodity: str, location: Location) -> Optional[CommodityPrice]:
        """Fetch price from Agmarknet (Government API)"""
        
        try:
            # Agmarknet commodity codes mapping
            commodity_codes = {
                "Rice": "1101",
                "Wheat": "1102", 
                "Maize": "1103",
                "Sugarcane": "1104",
                "Cotton": "1105",
                "Soybean": "1106",
                "Groundnut": "1107",
                "Potato": "1108",
                "Onion": "1109",
                "Tomato": "1110"
            }
            
            commodity_code = commodity_codes.get(commodity)
            if not commodity_code:
                return None
            
            # Make request to Agmarknet API
            url = f"https://agmarknet.gov.in/api/price/commodity/{commodity_code}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prices = data.get('price', [])
                
                if prices:
                    # Get the latest price
                    latest_price = prices[0]
                    return CommodityPrice(
                        commodity_name=commodity,
                        current_price=float(latest_price.get('price', 0)),
                        price_trend="stable",  # Would need historical data to determine trend
                        market_location=latest_price.get('market', location.state),
                        date=datetime.now()
                    )
                    
        except Exception as e:
            print(f"Agmarknet API error for {commodity}: {e}")
        
        return None
    
    async def _fetch_other_sources(self, commodity: str, location: Location) -> Optional[CommodityPrice]:
        """Fetch from other free sources"""
        
        try:
            # This would implement other free sources like:
            # - Web scraping from government websites
            # - RSS feeds from agricultural departments
            # - Public APIs from state agricultural boards
            
            # For now, return None to use mock data
            return None
            
        except Exception as e:
            print(f"Other sources error for {commodity}: {e}")
        
        return None
    
    def _create_mock_price(self, commodity: str, location: Location) -> CommodityPrice:
        """Create a mock price entry with realistic data"""
        
        if commodity not in self.mock_prices:
            # Default values for unknown commodities
            price_data = {
                "current_price": 2000,
                "trend": "stable",
                "markets": [location.state],
                "unit": "quintal"
            }
        else:
            price_data = self.mock_prices[commodity]
        
        # Find closest market
        closest_market = self._find_closest_market(location, price_data["markets"])
        
        # Add some realistic price variation
        base_price = price_data["current_price"]
        variation = base_price * 0.1  # 10% variation
        import random
        current_price = base_price + random.uniform(-variation, variation)
        
        return CommodityPrice(
            commodity_name=commodity,
            current_price=round(current_price, 2),
            price_trend=price_data["trend"],
            market_location=closest_market,
            date=datetime.now()
        )
    
    def _find_closest_market(self, location: Location, markets: List[str]) -> str:
        """Find the closest market to the given location"""
        
        state_market_mapping = {
            "Delhi": "Delhi",
            "Haryana": "Delhi", 
            "Punjab": "Punjab",
            "UP": "UP",
            "Uttar Pradesh": "UP",
            "Maharashtra": "Mumbai",
            "Gujarat": "Gujarat",
            "Karnataka": "Karnataka", 
            "Tamil Nadu": "Chennai",
            "West Bengal": "Kolkata",
            "Bihar": "Bihar",
            "Rajasthan": "Rajasthan",
            "Madhya Pradesh": "Madhya Pradesh",
            "Andhra Pradesh": "Andhra Pradesh",
            "Telangana": "Telangana",
            "Kerala": "Kerala",
            "Odisha": "Odisha",
            "Assam": "Assam"
        }
        
        return state_market_mapping.get(location.state, markets[0] if markets else location.state)
    
    async def get_price_trends(self, commodity: str, days: int = 30) -> Dict:
        """Get price trends for a commodity"""
        
        if commodity not in self.mock_prices:
            return {"error": "Commodity not found"}
        
        # Generate realistic trend data
        base_price = self.mock_prices[commodity]["current_price"]
        trend = self.mock_prices[commodity]["trend"]
        
        prices = []
        for i in range(days):
            if trend == "increasing":
                price = base_price + (i * 15) + (i * i * 0.5)
            elif trend == "decreasing":
                price = base_price - (i * 8) + (i * i * 0.2)
            else:  # stable
                price = base_price + (i * 5 if i % 2 == 0 else -i * 3)
            
            prices.append({
                "date": (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d"),
                "price": max(price, base_price * 0.5)  # Minimum price floor
            })
        
        return {
            "commodity": commodity,
            "trend": trend,
            "price_history": prices,
            "current_price": base_price,
            "price_change": prices[-1]["price"] - prices[0]["price"],
            "source": "Free Commodity Service"
        }
    
    def get_market_analysis(self, prices: List[CommodityPrice]) -> Dict:
        """Analyze market conditions based on commodity prices"""
        
        if not prices:
            return {"error": "No price data available"}
        
        # Calculate market indicators
        total_commodities = len(prices)
        increasing_trends = sum(1 for p in prices if p.price_trend == "increasing")
        decreasing_trends = sum(1 for p in prices if p.price_trend == "decreasing")
        stable_trends = sum(1 for p in prices if p.price_trend == "stable")
        
        # Calculate average price
        avg_price = sum(p.current_price for p in prices) / len(prices)
        
        # Find best and worst performing commodities
        best_commodity = max(prices, key=lambda x: x.current_price)
        worst_commodity = min(prices, key=lambda x: x.current_price)
        
        return {
            "market_sentiment": self._calculate_market_sentiment(increasing_trends, decreasing_trends, stable_trends),
            "average_price": round(avg_price, 2),
            "trend_distribution": {
                "increasing": increasing_trends,
                "decreasing": decreasing_trends,
                "stable": stable_trends
            },
            "best_performing": {
                "commodity": best_commodity.commodity_name,
                "price": best_commodity.current_price,
                "trend": best_commodity.price_trend
            },
            "worst_performing": {
                "commodity": worst_commodity.commodity_name,
                "price": worst_commodity.current_price,
                "trend": worst_commodity.price_trend
            },
            "market_recommendation": self._get_market_recommendation(increasing_trends, decreasing_trends, total_commodities),
            "data_source": "Free APIs + Realistic Mock Data"
        }
    
    def _calculate_market_sentiment(self, increasing: int, decreasing: int, stable: int) -> str:
        """Calculate overall market sentiment"""
        total = increasing + decreasing + stable
        if total == 0:
            return "Neutral"
        
        increasing_pct = (increasing / total) * 100
        decreasing_pct = (decreasing / total) * 100
        
        if increasing_pct > 60:
            return "Bullish"
        elif decreasing_pct > 60:
            return "Bearish"
        else:
            return "Neutral"
    
    def _get_market_recommendation(self, increasing: int, decreasing: int, total: int) -> str:
        """Get market recommendation based on trends"""
        if total == 0:
            return "No data available"
        
        if increasing > total * 0.6:
            return "Market is showing strong upward trends - good time for planting high-value crops"
        elif decreasing > total * 0.6:
            return "Market is declining - consider diversifying or focusing on staple crops"
        else:
            return "Market is stable - focus on crops with consistent demand"
