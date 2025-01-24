import logging
import json
from datetime import timedelta

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_COD_CLIENT

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up Apanova Ploiesti integration from a config entry."""
    email = config_entry.data[CONF_EMAIL]
    password = config_entry.data[CONF_PASSWORD]
    cod_client = config_entry.data[CONF_COD_CLIENT]

    # Create the coordinator to fetch data
    coordinator = ApanovaCoordinator(hass, email, password, cod_client)
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator instance to be used by the sensors
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

    # Forward the entry to the sensor platform
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        hass.data[DOMAIN].pop(config_entry.entry_id)
    return unload_ok


class ApanovaCoordinator(DataUpdateCoordinator):
    """Custom coordinator to fetch data from Apanova API."""

    def __init__(self, hass, email, password, cod_client):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),  # Update interval (every 5 minutes)
        )
        self.email = email
        self.password = password
        self.cod_client = cod_client

    async def _async_update_data(self):
        """Fetch data from Apanova APIs."""
        async with ClientSession() as session:
            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            }

            # Login and fetch CSRF token
            csrf_token = await self._fetch_csrf_token(session, headers)
            await self._login(session, headers, csrf_token)

            # Fetch invoice data
            invoices = await self._fetch_invoices(session, headers)

            return {
                "cod_client": self.cod_client,
                "invoices": invoices,
            }

    async def _fetch_csrf_token(self, session, headers):
        """Fetch CSRF token."""
        login_url = "https://www.apanova-ploiesti.ro/login"
        async with session.get(login_url, headers=headers) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, "html.parser")
            csrf_token = soup.find("input", {"name": "csrf_anb_token"})["value"]
            return csrf_token[:32]  # Truncate token

    async def _login(self, session, headers, csrf_token):
        """Login to Apanova."""
        login_url = "https://www.apanova-ploiesti.ro/cont-nou/login"
        login_data = {
            "email": self.email,
            "parola": self.password,
            "csrf_anb_token": csrf_token,
        }
        async with session.post(login_url, headers=headers, data=login_data) as response:
            if response.status != 200:
                raise Exception("Login failed!")

    async def _fetch_invoices(self, session, headers):
        """Fetch invoices."""
        invoices_url = "https://www.apanova-ploiesti.ro/user/getInvoices"
        data = {"cod": self.cod_client}

        async with session.post(invoices_url, headers=headers, data=data) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            raw_response = await response.text()

            #_LOGGER.debug(f"Invoices response status: {status}")
            #_LOGGER.debug(f"Response headers: {response.headers}")
            #_LOGGER.debug(f"Raw response content: {raw_response}")

            # Validate response type and status
            if "html" in content_type.lower() and not raw_response.strip().startswith("["):
                #_LOGGER.error(f"Error fetching invoices: Status: {status}, Content-Type: {content_type}")
                #_LOGGER.error(f"Response content: {raw_response}")  # Log the raw HTML
                return {"invoices": [], "cod_client": self.cod_client}  # Return default structure

            try:
                # Attempt to parse JSON from raw response
                invoices = json.loads(raw_response)  # Use json.loads to parse the string
                if isinstance(invoices, list):
                    #_LOGGER.debug(f"Invoices parsed successfully: {invoices}")
                    return {"invoices": invoices, "cod_client": self.cod_client}
                else:
                    #_LOGGER.error("Unexpected data format: invoices is not a list.")
                    return {"invoices": [], "cod_client": self.cod_client}
            except Exception as e:
                #_LOGGER.error(f"Error parsing JSON response: {e}")
                return {"invoices": [], "cod_client": self.cod_client}

###    async def _fetch_waterinfo(self, session, headers):
###        """Fetch water info."""
###        waterinfo_url = "https://www.apanova-ploiesti.ro/water/info"
###        #data = {"cod": self.cod_client}
###
###        async with session.post(waterinfo_url, headers=headers) as response:
###            status = response.status
###            content_type = response.headers.get("Content-Type", "")
###            raw_response = await response.text()
###
###            _LOGGER.debug(f"Water info response status: {status}")
###            _LOGGER.debug(f"Response headers: {response.headers}")
###            _LOGGER.debug(f"Raw response content: {raw_response}")
###
###            # Validate response type and status
###            if "html" in content_type.lower() and not raw_response.strip().startswith("["):
###                _LOGGER.error(f"Error fetching water info: Status: {status}, Content-Type: {content_type}")
###                _LOGGER.error(f"Response content: {raw_response}")  # Log the raw HTML
###                return {"waterinfo": []}  # Return default structure
###
###            try:
###                # Attempt to parse JSON from raw response
###                waterinfo = json.loads(raw_response)  # Use json.loads to parse the string
###                if isinstance(waterinfo, list):
###                    _LOGGER.debug(f"Invoices parsed successfully: {waterinfo}")
###                    return {"waterinfo": waterinfo}
###                else:
###                    _LOGGER.error("Unexpected data format: invoices is not a list.")
###                    return {"waterinfo": []}
###            except Exception as e:
###                _LOGGER.error(f"Error parsing JSON response: {e}")
###                return {"waterinfo": []}
