from django.db import models

class Seller(models.Model):
    steam_id = models.CharField(max_length=64, primary_key=True)
    username = models.CharField(max_length=100)
    avatar = models.URLField(max_length=500, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    account_age_days = models.IntegerField(null=True, blank=True)
    account_age_years = models.IntegerField(null=True, blank=True)
    cs2_hours = models.FloatField(null=True, blank=True)
    steam_level = models.IntegerField(null=True, blank=True)
    total_trades = models.IntegerField(null=True, blank=True)
    
    
    last_steam_fetch = models.DateTimeField(null=True, blank=True)
    personastate = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)

    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.steam_id

class Item(models.Model):
    asset_id = models.CharField(max_length=64, primary_key=True)
    market_hash_name = models.CharField(max_length=255)
    float_value = models.FloatField(null=True, blank=True)
    icon_url = models.URLField(max_length=500, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    is_stattrak = models.BooleanField(default=False)
    is_souvenir = models.BooleanField(default=False)

    def get_image_url(self):
        """Returns the best available image URL with proper Steam CDN formatting"""
        if self.icon_url:
            return self.fix_steam_url(self.icon_url)

        if self.image_url:
            return self.fix_steam_url(self.image_url)

        return "https://via.placeholder.com/64x48"

    def fix_steam_url(self, url_or_suffix):
        """Ensure the Steam image URL is full and uses correct CDN."""
        url = url_or_suffix

        if not url.startswith(('http', 'https')):
            url = 'https://community.cloudflare.steamstatic.com/economy/image/' + url

        replacements = [
            ('https://steamcommunity-a.akamaihd.net/economy/image/', 'https://community.cloudflare.steamstatic.com/economy/image/'),
            ('https://community.akamai.steamstatic.com/economy/image/', 'https://community.cloudflare.steamstatic.com/economy/image/'),
            ('http://cdn.steamcommunity.com/economy/image/', 'https://community.cloudflare.steamstatic.com/economy/image/')
        ]
        for old, new in replacements:
            url = url.replace(old, new)

        return url

    def __str__(self):
        return self.market_hash_name


class Listing(models.Model):
    listing_id = models.CharField(max_length=64, primary_key=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='listings') 
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='listings')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(null=True, blank=True) 
    inspect_link = models.URLField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.item} - ${self.price}"