"""The ice_cream_benelux integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup(hass, config):
    """Set up the sensor platform."""

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up entry."""

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
