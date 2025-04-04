import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing required environment variables")

try:
    supabase: Client = create_client(url, key)
    
    # First test the connection with a select query
    test_response = (
        supabase.table("tasks")
        .select("*")
        .execute()
    )
    print("Connection successful!")

    select_response = (
        supabase.table("tasks")
        .select("*")
        .execute()
    )
    print("Select successful:", select_response)
    
    # # Then try the insert
    # insert_response = (
    #     supabase.table("tasks")
    #     .insert({
    #         "title": "Run",
    #         "completed": False,
    #         "user_id": "abb6bcb5-436d-4a2d-90be-da08e2c6cfcb"
    #     })
    #     .execute()
    # )
    # print("Insert successful:", insert_response)

    # update_response = (
    #     supabase.table("tasks")
    #     .update({"title": "run-fast"})
    #     .eq("id", 'ec8ea5ec-75a1-4044-8f36-115666f3e0e4')
    #     .execute()
    # )
    # print("Update successful:", update_response)

    # delete_response = (
    #     supabase.table("tasks")
    #     .delete()
    #     .eq("id", 'ec8ea5ec-75a1-4044-8f36-115666f3e0e4')
    #     .execute()
    # )
    # print("Delete successful:", delete_response)
    
except Exception as e:
    print(f"An error occurred: {e}")
