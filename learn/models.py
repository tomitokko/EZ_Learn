from django.db import models
import uuid
from django.conf import settings

# Create your models here.
class Profile(models.Model):

    LANGUAGE_CHOICES = [
        ('mandarin', 'Mandarin'),  # The most spoken language in the world
        ('spanish', 'Spanish'),    # Second most spoken language by number of native speakers
        ('english', 'English'),    # The most international and third most spoken language by native speakers
        ('hindi', 'Hindi'),        # One of the most spoken languages in India
        ('bengali', 'Bengali'),    # Widely spoken in Bangladesh and parts of India
        ('portuguese', 'Portuguese'),  # Official language of Portugal, Brazil, and some African countries
        ('russian', 'Russian'),    # Most widely spoken language in Eurasia
        ('japanese', 'Japanese'),  # Official language of Japan
        ('punjabi', 'Punjabi'),    # Widely spoken in Pakistan and India
        ('marathi', 'Marathi'),    # One of the major languages of India
        ('telugu', 'Telugu'),      # One of the major languages in South India
        ('wu', 'Wu (Shanghainese)'),  # Spoken in parts of China
        ('turkish', 'Turkish'),    # Official language of Turkey
        ('korean', 'Korean'),      # Official language of North and South Korea
        ('french', 'French'),      # Official language in France and various other countries
        ('german', 'German'),      # Widely spoken in Germany, Austria, and parts of Switzerland
        ('vietnamese', 'Vietnamese'),  # Official language of Vietnam
        ('tamil', 'Tamil'),        # Spoken in parts of India, Sri Lanka, and Singapore
        ('yue', 'Yue (Cantonese)'),   # Spoken in parts of China, especially Hong Kong and Macau
        ('urdu', 'Urdu')           # One of the official languages of Pakistan and India
    ]

    COUNTRY_CHOICES = [
        ('china', 'China'),
        ('india', 'India'),
        ('united_states', 'United States'),
        ('indonesia', 'Indonesia'),
        ('pakistan', 'Pakistan'),
        ('brazil', 'Brazil'),
        ('nigeria', 'Nigeria'),
        ('bangladesh', 'Bangladesh'),
        ('russia', 'Russia'),
        ('mexico', 'Mexico'),
        ('japan', 'Japan'),
        ('ethiopia', 'Ethiopia'),
        ('philippines', 'Philippines'),
        ('egypt', 'Egypt'),
        ('vietnam', 'Vietnam'),
        ('congo', 'Congo (DRC)'),
        ('turkey', 'Turkey'),
        ('iran', 'Iran'),
        ('germany', 'Germany'),
        ('thailand', 'Thailand')
    ]


    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
    )
    
    country = models.CharField(max_length=1000, choices=LANGUAGE_CHOICES)
    language = models.CharField(max_length=1000, choices=COUNTRY_CHOICES)

class History(models.Model):
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
    )
    
    search_term = models.CharField(max_length=1000)