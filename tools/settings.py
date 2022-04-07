import os
from dotenv import load_dotenv
from pathlib import Path


dotenv_path = os.path.join(Path(__file__).parent.parent, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

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
        # "url": "https://isabsent.tk/contact/",
        "email": "isAbsent@gmail.com",
    },
    'openapi_tags': TAGS_METADATA
}
