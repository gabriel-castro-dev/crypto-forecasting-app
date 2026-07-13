from config import settings
from supabase import Client, create_client


def get_supabase_client() -> Client:
    """
    Inicializa e retorna a conexão bruta com o Supabase.

    Returns:
        Client: Uma instância do cliente do Supabase.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
