from supabaseConfig import get_supabase_client

supabase = get_supabase_client()


def register_user(email, password):
    response = supabase.auth.sign_up({
        'email': email,
        'password': password,
        'email_confirm': False,
    })
    return response


def login_user(email, password):
    response = supabase.auth.sign_in_with_password({
        'email': email,
        'password': password,
    })
    return response
