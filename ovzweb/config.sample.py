import os
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# WTF Settings
CSRF_ENABLED = True
SECRET_KEY = 'something_awful'

# Database Settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'database.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_PATH, 'db_repository')

# Server Settings
HARDWARE_NODES = (
    '172.16.254.154',
#    'vz1.cugnet.net',
#    'vz2.cugnet.net',
)

# Paypal Settings
PAYPAL_USERNAME = 'test_api1.cugnet.net'
PAYPAL_PASSWORD = '74GFQ6XM8UX6GXY3'
PAYPAL_SIGNATURE = 'AiPC9BjkCyDFQXbSkoZcgqH3hpacAzE-V.bPtLpShq9v0bGC6jeWxG0f'

# VPS Naming Conventions
HOSTNAME_PREFIX = 'vps'
HOSTNAME_SUFFIX = 'cugnet.net'


# VPS Network Settings
VPS_NETWORKS = (
    '172.16.254.154/27',
)

VPS_NETWORK_EXCLUDE_BROADCAST = True

VPS_NETWORK_EXCLUDE_NETWORK = True

VPS_NETWORK_EXCLUDE_HOSTS = (
    '172.16.254.154',
)