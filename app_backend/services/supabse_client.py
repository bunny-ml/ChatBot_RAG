from supabase import create_client , client
import os

class SupabaseClient:
    def __init__(self):
            
            self.SUPABASE_URL = os.getenv('SUPABASE_URL')
            self.SUPABASE_KEY = os.getenv('SUPABASE_KEY')

            self.client: client = create_client(supabase_key=self.SUPABASE_KEY , supabase_url=self.SUPABASE_URL)