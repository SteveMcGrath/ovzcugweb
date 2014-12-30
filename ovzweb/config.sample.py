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
    'vz1.cugnet.net',
    'vz2.cugnet.net',
)

# Paypal Settings
PAYPAL_USERNAME = 'test_api1.cugnet.net'
PAYPAL_PASSWORD = '74GFQ6XM8UX6GXY3'
PAYPAL_SIGNATURE = 'AiPC9BjkCyDFQXbSkoZcgqH3hpacAzE-V.bPtLpShq9v0bGC6jeWxG0f'