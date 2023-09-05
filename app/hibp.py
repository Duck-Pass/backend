import pyhibp
import os

HIBP_API_KEY = os.environ.get("HIBP_API_KEY")


async def get_breach_for_user(email, domain):
    """
    Check if there is an existing breach for a given email on a given domain
    :param str domain: Domain to check
    :param str email: Email to check
    :return: List of breaches
    """

    # Set the API key prior to using the functions which require it
    pyhibp.set_api_key(key=HIBP_API_KEY)
    pyhibp.set_user_agent(ua="DuckPass.ch")

    # Get breaches that affect a given account
    breach_data = pyhibp.get_account_breaches(account=email, truncate_response=False)

    reduced_data = [{'Name': breach['Name']} for breach in breach_data if breach.get("Domain", "") in domain.lower()]

    return reduced_data
