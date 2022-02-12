import os

string_date_format = '%Y-%m-%d'

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']

TAGS_METADATA = [
    {
        "name": "Auth",
        "description": "OAuth2 token operations."
    },
    {
        "name": "User",
        "description": "Operations with users.",
    },
    {
        "name": "Teacher",
        "description": "Operations with teachers",
    },
    {
        "name": "Student",
        "description": "Operations with students and absents",
    },
    {
        "name": "School",
        "description": "Operations with schools",
    }
]

DESCRIPTION = """
IaAbsent API helps you plan and mark your absents. 🚀
"""
VERSION = "1.0.0"
TITLE = 'IsAbsent'
APP_SETTINGS = {
    'title': TITLE,
    'version': VERSION,
    'description': DESCRIPTION,
    'contact': {
        "name": "IsAbsent",
        "url": "https://isabsent.tk/contact/",
        "email": "isAbsent@gmail.com",
    },
    'openapi_tags': TAGS_METADATA
}
