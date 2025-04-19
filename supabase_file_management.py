import os
from dotenv import load_dotenv
from supabase import create_client, Client


# Initialize Supabase
url = "https://rrexykfszwdetlvfmuxd.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyZXh5a2ZzendkZXRsdmZtdXhkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0Njc2MjEsImV4cCI6MjA2MDA0MzYyMX0.Dht99OdPBBxyqY-OtT2HFsQR69THOo69PezptRYMk3A"
supabase: Client = create_client(url, key)

# Upload file
bucket_name = "test1"
user_id = "testuser123"
file_path = r"C:\Users\basil\Downloads\smootgh brain.png"
supabase_file_path = f"{user_id}/file.png"

with open(file_path, "rb") as f:
    res = supabase.storage.from_(bucket_name).upload(supabase_file_path, f)

# Get public URL
public_url = supabase.storage.from_(bucket_name).get_public_url(supabase_file_path)
print("Public URL:", public_url)
