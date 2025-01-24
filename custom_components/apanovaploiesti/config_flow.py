import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN  # Ensure this matches your domain name

@config_entries.HANDLERS.register(DOMAIN)
class ApanovaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Apanova Ploiesti."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the user input and attempt connection
            email = user_input["email"]
            password = user_input["password"]
            cod_client = user_input["cod_client"]

            try:
                # Perform initial validation here (e.g., log in and fetch basic data)
                valid = await self.hass.async_add_executor_job(
                    self._validate_credentials, email, password, cod_client
                )
                if valid:
                    return self.async_create_entry(title="Apanova Ploiesti", data=user_input)
            except Exception as e:
                errors["base"] = "connection_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("email"): str,
                    vol.Required("password"): str,
                    vol.Required("cod_client"): str,
                }
            ),
            errors=errors,
        )

    def _validate_credentials(self, email, password, cod_client):
        """Validate credentials by attempting a login."""
        import requests
        from bs4 import BeautifulSoup

        session = requests.Session()

        # Fetch CSRF token
        login_url = "https://www.apanova-ploiesti.ro/login"
        response = session.get(login_url)
        if response.status_code != 200:
            raise Exception("Failed to fetch login page.")

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrf_anb_token"})["value"][:32]

        # Attempt login
        login_data = {
            "email": email,
            "parola": password,
            "csrf_anb_token": csrf_token,
        }
        login_post_url = "https://www.apanova-ploiesti.ro/cont-nou/login"
        login_response = session.post(login_post_url, data=login_data)
        if login_response.status_code != 200:
            raise Exception("Login failed.")

        # Validate cod_client
        cod_client_url = "https://www.apanova-ploiesti.ro/user/getCoduriClient"
        cod_client_response = session.post(cod_client_url, data={"cod": cod_client})
        if cod_client_response.status_code != 200:
            raise Exception("Invalid client code.")

        return True
