import requests
import os
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class CSFloatAPI:
    BASE_URL = "https://csfloat.com/api/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.api_key = os.getenv("CSFLOAT_API_KEY", "").strip()
        
        if not self.api_key:
            logger.warning("CSFLOAT_API_KEY is not set or is empty. API calls may fail.")
        else:
            logger.info("CSFLOAT_API_KEY loaded successfully. (Using raw key in Authorization header)")
            
        self.headers = {
            "User-Agent": "FloatScanner/1.0",
            "Accept": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = self.api_key
            
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def get_listings(self, page=1, limit=50, **kwargs):
        params = {
            'limit': limit,
            'page': page,
            **kwargs 
        }

        try:
            url = f"{self.BASE_URL}/listings"
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            print(f"CSFloat API Response: {response.status_code}")
            if response.status_code != 200:
                print(f"Response content: {response.text[:200]}...")

            response.raise_for_status() 
            data = response.json()
            
            return {'data': data} if isinstance(data, list) else data 
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error fetching CSFloat listings: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching CSFloat listings: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in CSFloatAPI.get_listings: {str(e)}", exc_info=True)
            return None

class SteamAPI:
    BASE_URL = "https://api.steampowered.com"
    
    def __init__(self):
        self.api_key = os.getenv("STEAM_API_KEY")
        if not self.api_key:
            raise ValueError("STEAM_API_KEY not found in .env")
        
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_player_data(self, steam_id):
        """Get all Steam data in one call"""
        try:
            summary_response = self.session.get(
                f"{self.BASE_URL}/ISteamUser/GetPlayerSummaries/v2/",
                params={"key": self.api_key, "steamids": steam_id},
                timeout=10
            )
            summary_response.raise_for_status()
            summary = summary_response.json()
            
            games_response = self.session.get(
                f"{self.BASE_URL}/IPlayerService/GetOwnedGames/v1/",
                params={
                    "key": self.api_key,
                    "steamid": steam_id,
                    "include_appinfo": 0,
                    "include_played_free_games": 1
                },
                timeout=10
            )
            games_response.raise_for_status()
            games = games_response.json()
            
            level_response = self.session.get(
                f"{self.BASE_URL}/IPlayerService/GetSteamLevel/v1/",
                params={"key": self.api_key, "steamid": steam_id},
                timeout=10
            )
            level_response.raise_for_status()
            level = level_response.json()
            
            return {
                "profile": summary.get("response", {}).get("players", [{}])[0],
                "games": games.get("response", {}),
                "level": level.get("response", {})
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Steam HTTP Error for {steam_id}: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Steam Network Error for {steam_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in SteamAPI.get_player_data for {steam_id}: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def get_profile_url(steam_id):
        return f"https://steamcommunity.com/profiles/{steam_id}"