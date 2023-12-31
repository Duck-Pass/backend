import hibpwned
import os

API_KEY = os.environ.get("HIBP_API_KEY")
USER_AGENT = os.environ.get("USER_AGENT")


async def get_breach_for_user(email):
    """
    Function to get the breaches for a user
    :param str email: Email of the user
    """

    hibp = hibpwned.Pwned(email, USER_AGENT, API_KEY)
    all_my_breaches = hibp.search_all_breaches()
    if all_my_breaches == 404:
        return []
    return [{'Name': breach['Name'], 'Domain': breach['Domain'], 'BreachDate': breach['BreachDate'], 'DataClasses': breach['DataClasses']} for breach in all_my_breaches]


async def get_breach_for_password(email, hash_begin):
    """
    Function to get the breaches for a user
    :param str email: Email of the user
    :param str hash_begin: Beginning of the hash of the password
    """

    hibp = hibpwned.Pwned(email, USER_AGENT, API_KEY)
    hashes = hibp.search_hashes(hash_begin)
    return hashes

