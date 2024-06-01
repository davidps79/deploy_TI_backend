from supabaseConfig import get_supabase_client

supabase = get_supabase_client()


def get_user_sessions(user_id):
    response = supabase.table('sessions').select('*').eq('user_id', user_id).execute()
    return response.data
