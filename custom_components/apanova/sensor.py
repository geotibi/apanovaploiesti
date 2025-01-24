from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .const import DOMAIN
import logging
import aiohttp
import json


_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "cod_client": "Cod Client",
    "status_factura": "Status Factură",
    "date_emitere": "Dată Emitere",
    "date_scadenta": "Dată Scadență",
    "numar_factura": "Număr Factură",
    "total": "Total",
    "sold": "Sold",
    "date_plata": "Dată Plată",
    "sector": "Sector",
    "clor": "Clor",
    "ph": "pH",
}

class ApanovaSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Apanova sensor."""

    def __init__(self, coordinator, name, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._sensor_type = sensor_type
        self._icon = self._get_icon(sensor_type)
        #self._extra_data = extra_data  # Used for water quality sensors

    @property
    def name(self):
        """Return the name of the sensor."""
        return {SENSOR_TYPES[self._sensor_type]}

    @property
    def icon(self):
        """Return the icon for the sensor."""
        return self._icon

###    @property
###    def entity_picture(self):
###        """Return the custom logo image as the entity picture."""
###        # Use the custom logo as the entity picture
###        return "https://www.apanova-ploiesti.ro/assets/images/logoANB.png"

    @property
    def state(self):
        """Return the state of the sensor."""
        #_LOGGER.error(f"coordinator.data: {self.coordinator.data}")
        if self._sensor_type == "cod_client":
            return self.coordinator.data.get("cod_client")

        elif self._sensor_type == "status_factura":
            # Accessing data from the nested structure
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary

            #_LOGGER.error(f"Invoices: {invoices}")
            if isinstance(invoices, list) and invoices:
                # Get the status of the first invoice
                first_invoice = invoices[0]  # Extract the first invoice
                #_LOGGER.error(f"First invoice is {first_invoice}")
                sap_status = first_invoice.get("SapStatus", "Unknown")  # Default to "Unknown"
                return sap_status
            else:
                #_LOGGER.error(f"1 - Expected list for 'invoices', got: {type(invoices)} with value: {invoices}")
                return "No invoices available"
        
        elif self._sensor_type == "date_emitere":
            # Handle "Dată Emitere" (returning DateIn)
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary
            if isinstance(invoices, list) and invoices:
                first_invoice = invoices[0]
                date_in = first_invoice.get("DateIn", "Unknown")  # Default to "Unknown"
                return date_in

        elif self._sensor_type == "date_scadenta":
            # Handle "Dată Scadență" (returning DueDate)
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary
            if isinstance(invoices, list) and invoices:
                first_invoice = invoices[0]
                due_date = first_invoice.get("DueDate", "Unknown")  # Default to "Unknown"
                return due_date
        elif self._sensor_type == "numar_factura":
            # Handle "Număr Factură" (returning InvoiceNumber)
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary
            if isinstance(invoices, list) and invoices:
                first_invoice = invoices[0]
                numar_factura = first_invoice.get("InvoiceNumber", "Unknown")  # Default to "Unknown"
                return numar_factura
        elif self._sensor_type == "total":
            # Handle "Total" (returning Total)
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary
            if isinstance(invoices, list) and invoices:
                first_invoice = invoices[0]
                total = first_invoice.get("Total", "Unknown")  # Default to "Unknown"
                return total
        elif self._sensor_type == "sold":
            # Handle "Sold" (returning Sold)
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary
            if isinstance(invoices, list) and invoices:
                first_invoice = invoices[0]
                sold = first_invoice.get("Sold", "Unknown")  # Default to "Unknown"
                return sold
        elif self._sensor_type == "date_plata":
            # Handle "Dată Plată" (returning LastPayDate)
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary
            if isinstance(invoices, list) and invoices:
                first_invoice = invoices[0]
                last_pay = first_invoice.get("LastPayDate", "Unknown")  # Default to "Unknown"
                return last_pay
        return None  # Default return for other sensor types


    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self._sensor_type == "status_factura":
            # Accessing data from the nested structure
            data = self.coordinator.data.get("invoices", {})  # Access the nested 'invoices' dictionary
            invoices = data.get("invoices", [])  # Get the list of invoices from that dictionary

            if isinstance(invoices, list):
                return {"invoices": invoices}
            else:
                _LOGGER.error(f"2 - Expected list for 'invoices', got: {type(invoices)} with value: {invoices}")
        return {}


    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self._sensor_type}"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for the sensor."""
        if self._sensor_type == "total" or self._sensor_type == "sold":
            return "Lei"
        else:
            return None  # Default unit for other sensors

    @property
    def device_info(self):
        """Return device information for the sensor."""
        # Define a unique identifier for the device (e.g., using `cod_client`)
        identifiers = {(DOMAIN, self.coordinator.data.get("cod_client", "unknown_client"))}

        # Add additional attributes for water sensors if applicable
        if self._sensor_type in ["sector", "clor", "ph"]:
            identifiers.add((DOMAIN, f"water_{self._sensor_type}"))

        return {
            "identifiers": identifiers,  # Unique identifiers for the device
            "name": "Apanova Ploiești",
            "manufacturer": "Neagu George (geotibi)",
            "model": "Apanova Ploiești",
            "entry_type": DeviceEntryType.SERVICE,
        }


    def _get_icon(self, sensor_type):
        """Return the appropriate icon for each sensor."""
        if sensor_type == "cod_client":
            return "mdi:account"
        elif sensor_type == "status_factura":
            return "mdi:file-document"
        elif sensor_type == "date_emitere":
            return "mdi:calendar-check"
        elif sensor_type == "date_scadenta":
            return "mdi:calendar-alert"
        elif sensor_type == "numar_factura":
            return "mdi:invoice"
        elif sensor_type == "total":
            return "mdi:credit-card-outline"
        elif sensor_type == "sold":
            return "mdi:cash-multiple"
        elif sensor_type == "date_plata":
            return "mdi:calendar"
        return "mdi:help"  # Default icon if not recognized
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensors for Apanova integration."""
    #_LOGGER.debug("Setting up Apanova sensors...")
    # Add the icon URL to a custom place in hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Fetch data from water info endpoint
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://www.apanova-ploiesti.ro/water/info") as response:
                text_data = await response.text()  # Response is text/html
                _LOGGER.debug(f"Fetched water info: {text_data}")
                extra_data = json.loads(text_data)  # Parse the response as JSON
                _LOGGER.debug(f"Fetched water info: {extra_data}")
    except Exception as e:
        _LOGGER.error(f"Error fetching water info: {e}")
        extra_data = []  # Fallback to an empty list if the request fails

    # Check and extract data from the response
    first_entry = extra_data[0] if extra_data else {}
    sector = first_entry.get("sector", "Unknown")
    clor = first_entry.get("clor", "Unknown")
    ph = first_entry.get("ph", "Unknown")

    _LOGGER.debug(f"First entry from water info: sector={sector}, clor={clor}, ph={ph}")
    # Define sensors
    sensors = [
        ApanovaSensor(coordinator, "Apanova Ploiesti", "cod_client"),
        ApanovaSensor(coordinator, "Apanova Ploiesti", "status_factura"),
        ApanovaSensor(coordinator, "Apanova Ploiesti", "date_emitere"),
        ApanovaSensor(coordinator, "Apanova Ploiesti", "date_scadenta"),
        ApanovaSensor(coordinator, "Apanova Ploiesti", "numar_factura"),
        ApanovaSensor(coordinator, "Apanova Ploiesti", "total"),
        ApanovaSensor(coordinator, "Apanova Ploiesti", "sold"),
        ApanovaSensor(coordinator, "Apanova Ploiesti", "date_plata"),
        ApanovaWaterSensor(coordinator, "Apanova Ploiesti", "sector", sector),
        ApanovaWaterSensor(coordinator, "Apanova Ploiesti", "clor", clor),
        ApanovaWaterSensor(coordinator, "Apanova Ploiesti", "ph", ph),
    ]

    async_add_entities(sensors, update_before_add=True)

class ApanovaWaterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a water quality sensor."""

    def __init__(self, coordinator, name, sensor_type, value):
        """Initialize the water quality sensor."""
        super().__init__(coordinator)
        self._name = name
        self._sensor_type = sensor_type
        self._value = value
        self._icon = self._get_icon(sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        return {SENSOR_TYPES[self._sensor_type]}

    @property
    def icon(self):
        """Return the icon for the sensor."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._value

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self._sensor_type}"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {"type": "water_quality"}

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for the sensor."""
        if self._sensor_type == "clor":
            return "mg/l"  # Clor measurement unit in mg/l
        elif self._sensor_type == "total" or self._sensor_type == "sold":
            return "Lei"
        else:
            return None  # Default unit for other sensors
    
    @property
    def device_info(self):
        """Return device information for the water sensor."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.data.get("cod_client", "unknown_client"))},
            "name": "Apanova Ploiești",
            "manufacturer": "Neagu George (geotibi)",
            "model": "Apanova Ploiești",
            "entry_type": DeviceEntryType.SERVICE,
        }
    @property
    def entity_registry_enabled_default(self) -> bool:
        """Indicate that the entity is enabled by default."""
        return True

    def _get_icon(self, sensor_type):
        """Return an appropriate icon for water sensors."""
        if sensor_type == "sector":
            return "mdi:map"
        elif sensor_type == "clor":
            return "mdi:water-percent"
        elif sensor_type == "ph":
            return "mdi:ph"
        return "mdi:help"
