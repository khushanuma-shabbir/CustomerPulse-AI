from app.supabase_client import supabase

response = supabase.table("tickets").select("*").limit(5).execute()

print("DATA:")
for row in response.data:
    print(row)

print("\nNumber of rows fetched:", len(response.data))