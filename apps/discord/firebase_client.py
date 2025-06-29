import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Try to get the service account JSON from the environment variable
service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
service_account_path = os.getenv('FIREBASE_CREDENTIALS', 'serviceAccountKey.json')

if service_account_json:
    # Write the JSON to a temp file
    temp_path = 'serviceAccountKey.temp.json'
    with open(temp_path, 'w') as f:
        f.write(service_account_json)
    service_account_path = temp_path

cred = credentials.Certificate(service_account_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client() 