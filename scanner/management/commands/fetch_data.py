from django.core.management.base import BaseCommand
from scanner.models import Seller, Item, Listing
from scanner.api_clients import CSFloatAPI, SteamAPI
from datetime import datetime
import time
import logging
from django.utils import timezone
import pytz

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetches and continuously updates CSFloat listings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run in continuous mode'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Seconds between checks (default: 60)'
        )
        parser.add_argument(
            '--target-listings',
            type=int,
            default=50,
            help='Target number of unique seller listings to process per run (default: 50, max 50 due to CSFloat API limit)'
        )

    def handle(self, *args, **options):
        csfloat = CSFloatAPI()
        steam = SteamAPI() 
        
        target_listings_count = options['target_listings']
        csfloat_actual_limit = 50 

        try:
            while True:
                start_time = time.time()
                
                self.stdout.write(f"Fetching up to {csfloat_actual_limit} raw CSFloat listings (max allowed) to find up to {target_listings_count} unique sellers...")
                
                response = csfloat.get_listings(limit=csfloat_actual_limit, sort_by='most_recent', min_price=10000) 
                
                if not response:
                    self.stdout.write(self.style.ERROR("CSFloat API returned no response or encountered an error."))
                    if not options['continuous']:
                        break
                    self._wait_interval(start_time, options['interval'])
                    continue
                
                all_raw_listings = response.get('data', [])
                
                if not all_raw_listings:
                    self.stdout.write(self.style.WARNING("No raw listings found in this interval from CSFloat API."))
                    if not options['continuous']:
                        break
                    self._wait_interval(start_time, options['interval'])
                    continue
                
                unique_seller_listings_to_process = []
                seen_steam_ids_in_batch = set() 

                for listing_data in all_raw_listings:
                    seller_data = listing_data.get('seller', {})
                    steam_id = seller_data.get('steam_id')

                    if steam_id and steam_id not in seen_steam_ids_in_batch:
                        unique_seller_listings_to_process.append(listing_data)
                        seen_steam_ids_in_batch.add(steam_id)
                        
                        if len(unique_seller_listings_to_process) >= target_listings_count:
                            break 
                
                if not unique_seller_listings_to_process:
                    self.stdout.write(self.style.WARNING(f"Could not find any listings with unique sellers and valid Steam IDs from the {len(all_raw_listings)} raw listings fetched."))
                    if not options['continuous']:
                        break
                    self._wait_interval(start_time, options['interval'])
                    continue

                self.stdout.write(self.style.SUCCESS(f"Proceeding with {len(unique_seller_listings_to_process)} unique seller listings for processing."))
                
                success_count = self._process_listings(unique_seller_listings_to_process, steam)
                
                self.stdout.write(self.style.SUCCESS(f"Successfully processed {success_count}/{len(unique_seller_listings_to_process)} selected listings."))
                
                if not options['continuous']:
                    break
                    
                self._wait_interval(start_time, options['interval'])
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("\nScanning stopped by user"))
        except Exception as e:
            logger.exception(f"Fatal error in fetch_data command: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Fatal error: {str(e)}"))
    
    def _process_listings(self, listings, steam):
        """
        Process listings, fetching Steam data for each seller only once per run.
        Returns success count.
        """
        success_count = 0
        processed_seller_steam_ids = set() 

        for listing_data in listings:
            try:
                if not isinstance(listing_data, dict):
                    logger.warning(f"Skipping non-dict listing data: {listing_data}")
                    continue

                seller_data_from_listing = listing_data.get('seller', {})
                steam_id = seller_data_from_listing.get('steam_id')
                if not steam_id:
                    logger.warning(f"Skipping listing with no steam_id (filtered out earlier in most cases): {listing_data.get('id')}")
                    continue

                seller_obj = None

                if steam_id not in processed_seller_steam_ids:
                    steam_data = steam.get_player_data(steam_id)
                    
                    seller_statistics = seller_data_from_listing.get('statistics', {})
                    total_trades_value = seller_statistics.get('total_trades')
                    if total_trades_value is None:
                        total_trades_value = 0

                    if steam_data:
                        player_profile_data = steam_data.get('profile', {})
                        time_created = player_profile_data.get('timecreated')
                        
                        account_age_years = None
                        account_age_days = None
                        if time_created:
                            creation_datetime = datetime.fromtimestamp(time_created, tz=pytz.utc)
                            now = timezone.now()
                            delta = now - creation_datetime
                            account_age_days = delta.days
                            account_age_years = delta.days // 365

                        personastate = player_profile_data.get('personastate', 0)
                        is_online = (personastate != 0) 
                        
                        seller_obj, _ = Seller.objects.update_or_create(
                            steam_id=steam_id,
                            defaults={
                                'username': player_profile_data.get('personaname', ''),
                                'avatar': player_profile_data.get('avatarfull', ''),
                                'country': player_profile_data.get('loccountrycode'),
                                'account_age_years': account_age_years,
                                'account_age_days': account_age_days,
                                'cs2_hours': self.get_cs2_hours(steam_data),
                                'steam_level': steam_data.get('level', {}).get('player_level', 0),
                                'personastate': personastate,
                                'is_online': is_online,
                                'last_steam_fetch': timezone.now(),
                                'total_trades': total_trades_value,
                            }
                        )
                        processed_seller_steam_ids.add(steam_id)
                    else:
                        logger.warning(f"Failed to fetch Steam data for {steam_id}. Attempting to use existing Seller object.")
                        try:
                            seller_obj = Seller.objects.get(steam_id=steam_id)
                            if seller_obj.total_trades != total_trades_value:
                                seller_obj.total_trades = total_trades_value
                                seller_obj.save(update_fields=['total_trades'])
                        except Seller.DoesNotExist:
                            logger.error(f"Seller {steam_id} not found and Steam data fetch failed. Cannot process listing.")
                            continue
                else:
                    seller_obj = Seller.objects.get(steam_id=steam_id)
                    
                    seller_statistics = seller_data_from_listing.get('statistics', {})
                    total_trades_value = seller_statistics.get('total_trades')
                    if total_trades_value is None:
                        total_trades_value = 0

                    if seller_obj.total_trades != total_trades_value:
                        seller_obj.total_trades = total_trades_value
                        seller_obj.save(update_fields=['total_trades']) 
                
                item_data = listing_data.get('item', {})

                image_url = item_data.get('image_url', '')
                icon_url = item_data.get('icon_url', '')

                if not image_url and not icon_url:
                    logger.warning(f"Missing image and icon URL for item {item_data.get('market_hash_name')}")

                item, _ = Item.objects.update_or_create(
                    asset_id=item_data.get('asset_id', ''),
                    defaults={
                        'market_hash_name': item_data.get('market_hash_name', ''),
                        'float_value': item_data.get('float_value', 0),
                        'icon_url': icon_url,
                        'image_url': image_url,
                        'is_stattrak': item_data.get('is_stattrak', False),
                        'is_souvenir': item_data.get('is_souvenir', False),
                    }
                )

                Listing.objects.update_or_create(
                    listing_id=listing_data.get('id', ''),
                    defaults={
                        'seller': seller_obj,
                        'item': item,
                        'price': listing_data.get('price', 0) / 100,
                        'created_at': datetime.fromisoformat(listing_data.get('created_at').replace('Z', '+00:00')) if listing_data.get('created_at') else None,
                        'inspect_link': item_data.get('inspect_link', ''),
                    }
                )

                success_count += 1
                time.sleep(0.5)
            
            except Exception as e:
                logger.error(f"Error processing listing {listing_data.get('id', 'N/A')}: {e}", exc_info=True)
                continue

        return success_count
    
    def _wait_interval(self, start_time, interval):
        """Wait for remaining interval time"""
        elapsed = time.time() - start_time
        remaining = max(0, interval - elapsed)
        if remaining > 0:
            self.stdout.write(f"Waiting {remaining:.1f} seconds...")
            time.sleep(remaining)
    
    def get_cs2_hours(self, steam_data):
        for game in steam_data.get('games', {}).get('games', []):
            if game.get('appid') == 730:
                return game.get('playtime_forever', 0) / 60
        return 0