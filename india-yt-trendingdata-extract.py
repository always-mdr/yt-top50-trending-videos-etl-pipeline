import json
import boto3
import requests
from datetime import datetime

# --- Configurations ---
API_KEY = 'YOUR_API_KEY_HERE'
BUCKET_NAME = 'youtube-ecommerce-datalake-mdr-2026' # Replace with your S3 bucket name
REGION_CODE = 'IN' # You can change this to 'IN', 'GB', etc.

# Initialize AWS S3 client (Ensure you have run `aws configure` locally with your IAM user)
s3 = boto3.client('s3')

def get_trending_videos():
    """Fetches the top 50 trending videos from YouTube."""
    url = "https://www.googleapis.com/youtube/v3/videos"
    
    # The 'part' parameter tells YouTube exactly what metadata we want
    params = {
        'part': 'snippet,statistics', 
        'chart': 'mostPopular',
        'regionCode': REGION_CODE,
        'maxResults': 50,
        'key': API_KEY
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status() # Fails the script if the API call fails
    return response.json()

def upload_to_datalake(data):
    """Saves the raw JSON to the S3 Bronze layer."""
    # We use a timestamp to ensure we never overwrite older data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_key = f"india-yt-mdr-bronze/trending_videos_{timestamp}.json"
    
    # Upload directly to S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=json.dumps(data)
    )
    print(f"Success! Uploaded {len(data.get('items', []))} videos to s3://{BUCKET_NAME}/{file_key}")

if __name__ == "__main__":
    print("Fetching data from YouTube API...")
    raw_data = get_trending_videos()
    upload_to_datalake(raw_data)