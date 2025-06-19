from django import forms
from django.db.models import F
from .models import Seller

ALL_COUNTRIES = [
    ('AF', 'Afghanistan'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'),
    ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'),
    ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'),
    ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'),
    ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'),
    ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'),
    ('BT', 'Bhutan'), ('BO', 'Bolivia (Plurinational State of)'), ('BQ', 'Bonaire, Sint Eustatius and Saba'),
    ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'),
    ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'),
    ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('CV', 'Cabo Verde'),
    ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('KY', 'Cayman Islands'),
    ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'),
    ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'),
    ('KM', 'Comoros'), ('CD', 'Congo (Democratic Republic of the)'), ('CG', 'Congo'),
    ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('CI', 'Côte d\'Ivoire'), ('HR', 'Croatia'),
    ('CU', 'Cuba'), ('CW', 'Curaçao'), ('CY', 'Cyprus'), ('CZ', 'Czechia'),
    ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'),
    ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'),
    ('ER', 'Eritrea'), ('EE', 'Estonia'), ('SZ', 'Eswatini'), ('ET', 'Ethiopia'),
    ('FK', 'Falkland Islands (Malvinas)'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'),
    ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'),
    ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'),
    ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'),
    ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'),
    ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'),
    ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'),
    ('VA', 'Holy See'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'),
    ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran (Islamic Republic of)'),
    ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'),
    ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'),
    ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'),
    ('KP', 'Korea (Democratic People\'s Republic of)'), ('KR', 'Korea (Republic of)'),
    ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', 'Lao People\'s Democratic Republic'),
    ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'),
    ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'),
    ('MO', 'Macao'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'),
    ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'),
    ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'),
    ('MX', 'Mexico'), ('FM', 'Micronesia (Federated States of)'), ('MD', 'Moldova (Republic of)'),
    ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'),
    ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'),
    ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('NC', 'New Caledonia'),
    ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'),
    ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MK', 'North Macedonia'),
    ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'),
    ('PW', 'Palau'), ('PS', 'Palestine, State of'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'),
    ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'),
    ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'),
    ('RE', 'Réunion'), ('RO', 'Romania'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'),
    ('BL', 'Saint Barthélemy'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'),
    ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin (French part)'),
    ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'),
    ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'),
    ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten (Dutch part)'),
    ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'),
    ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'),
    ('SS', 'South Sudan'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'),
    ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SE', 'Sweden'),
    ('CH', 'Switzerland'), ('SY', 'Syrian Arab Republic'), ('TW', 'Taiwan, Province of China'),
    ('TJ', 'Tajikistan'), ('TZ', 'Tanzania, United Republic of'), ('TH', 'Thailand'),
    ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'),
    ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'),
    ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'),
    ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom of Great Britain and Northern Ireland'),
    ('US', 'United States of America'), ('UM', 'United States Minor Outlying Islands'),
    ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela (Bolivarian Republic of)'),
    ('VN', 'Viet Nam'), ('VG', 'Virgin Islands (British)'), ('VI', 'Virgin Islands (U.S.)'),
    ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe')
]


class ListingFilterForm(forms.Form):
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Min Price",
        widget=forms.NumberInput(attrs={'placeholder': 'Min Price'})
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Max Price",
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price'})
    )
    min_steam_level = forms.IntegerField(
        required=False,
        min_value=0,
        label="Min Level",
        widget=forms.NumberInput(attrs={'placeholder': 'Min Level'})
    )
    max_steam_level = forms.IntegerField(
        required=False,
        min_value=0,
        label="Max Level",
        widget=forms.NumberInput(attrs={'placeholder': 'Max Level'})
    )
    min_cs2_hours = forms.FloatField(
        required=False,
        min_value=0,
        label="Min CS2 Hrs",
        widget=forms.NumberInput(attrs={'placeholder': 'Min CS2 Hrs'})
    )
    max_cs2_hours = forms.FloatField(
        required=False,
        min_value=0,
        label="Max CS2 Hrs",
        widget=forms.NumberInput(attrs={'placeholder': 'Max CS2 Hrs'})
    )
    min_total_trades = forms.IntegerField(
        required=False,
        min_value=0,
        label="Min Trades",
        widget=forms.NumberInput(attrs={'placeholder': 'Min Trades'})
    )
    max_total_trades = forms.IntegerField(
        required=False,
        min_value=0,
        label="Max Trades",
        widget=forms.NumberInput(attrs={'placeholder': 'Max Trades'})
    )

    username = forms.CharField(required=False, label="Seller Username")
    
    country = forms.ChoiceField(
        choices=[('', 'All Countries')] + ALL_COUNTRIES,
        required=False,
        label="Country",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        min_level = cleaned_data.get('min_steam_level')
        max_level = cleaned_data.get('max_steam_level')
        min_hours = cleaned_data.get('min_cs2_hours')
        max_hours = cleaned_data.get('max_cs2_hours')
        min_total_trades = cleaned_data.get('min_total_trades')
        max_total_trades = cleaned_data.get('max_total_trades')
        
        if min_price is not None and max_price is not None and max_price < min_price:
            self.add_error('max_price', 'Max price cannot be less than min price.')
        
        if min_level is not None and max_level is not None and max_level < min_level:
            self.add_error('max_steam_level', 'Max level cannot be less than min level.')
        
        if min_hours is not None and max_hours is not None and max_hours < min_hours:
            self.add_error('max_cs2_hours', 'Max CS2 Hours cannot be less than min CS2 Hours.')
        
        if min_total_trades is not None and max_total_trades is not None and max_total_trades < min_total_trades:
            self.add_error('max_total_trades', 'Max Trades cannot be less than min Trades.')

        return cleaned_data