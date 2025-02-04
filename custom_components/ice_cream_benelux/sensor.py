"""Sensor platform for ice_cream_benelux."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import APP_NAME, CONF_APP_NAME, CONF_LATITUDE, CONF_LONGITUDE
from .http_client import HTTPClient
from .utils_location import haversine
from .utils_string import snake_to_pascal_case

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up entry."""
    app_config = {
        CONF_APP_NAME: APP_NAME,
    }
    lat = config_entry.data.get(CONF_LATITUDE)
    lon = config_entry.data.get(CONF_LONGITUDE)
    companies = config_entry.data.get("companies")

    sensors = []
    for company in companies:
        sensor_class_name = snake_to_pascal_case(company) + "Sensor"
        sensor_class = globals().get(sensor_class_name)
        config = {**app_config, **config_entry.data}
        if sensor_class:
            sensors.append(sensor_class(config, company, lat, lon))
        else:
            _LOGGER.error("No sensor class found for %s", company)

    async_add_entities(sensors, True)


class IceCreamVanSensor(SensorEntity):
    """Sensor class for ice_cream_benelux."""

    def __init__(self, config, company, user_lat, user_lon) -> None:
        """Initialize the sensor."""
        self._name = f"{config.get(CONF_APP_NAME)} {company}"
        self._company = company
        self._state = None
        self._user_lat = user_lat
        self._user_lon = user_lon
        self._attributes = {}
        self._http = HTTPClient(logger=_LOGGER)

    @property
    def device_class(self):
        """Return the device class."""
        return SensorDeviceClass.DISTANCE

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return f"{APP_NAME}_{self._company}_{self._user_lat}_{self._user_lon}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    # Unit of measurement
    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "km"

    async def async_update(self):
        """Update sensor."""
        await self.set_van_state()

    async def set_van_state(self):
        """Get nearest van and set state."""
        try:
            van = await self.get_nearest_van()
            if van is not None:
                self._state = van["distance"]
                self._attributes = van
            # TODO: Make the "unknown" state configurable
            # if van is None:
            #     self._state = "unknown"
            #     self._attributes = {}
            # else:
            #     self._state = van["distance"]
            #     self._attributes = van

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error: %s", self.entity_id)

    async def get_nearest_van(self):
        """Get the nearest van. To be implemented by subclasses."""
        raise NotImplementedError


class DeKremkerreMelleSensor(IceCreamVanSensor):
    """Sensor class for De Kremkerre Melle."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry("https://ijsjesradar.be/status.php")

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = await self.get_vans()
        vans = [
            van
            for van in vans
            if van.get("company_ref") == "de-kremkerre"
            and van.get("status") == "online"
        ]
        vans_with_distance = []
        for van in vans:
            lat = van.get("location", {}).get("lat")
            lon = van.get("location", {}).get("lon")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("name"),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status"),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class DeKrijmboerLommelSensor(IceCreamVanSensor):
    """Sensor class for De Krijmboer Lommel."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=10&has_working_day=1"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = await self.get_vans()
        vans = json_data.get("data", [])
        vans_with_distance = []
        for van in vans:
            lat = van.get("latitude")
            lon = van.get("longitude")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("title", ""),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status", "").lower(),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class FoubertSintNiklaasSensor(IceCreamVanSensor):
    """Sensor class for Foubert Sint-Niklaas."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=2&has_working_day=1"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = await self.get_vans()
        vans = json_data.get("data", [])
        vans_with_distance = []
        for van in vans:
            lat = van.get("latitude")
            lon = van.get("longitude")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("title", ""),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status", "").lower(),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class GlaceDeBockBeverenSensor(IceCreamVanSensor):
    """Sensor class for Glace De Bock Beveren."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry("https://ijsjesradar.be/status.php")

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = await self.get_vans()
        vans = [
            van
            for van in vans
            if van.get("company_ref") == "de-bock" and van.get("status") == "online"
        ]
        vans_with_distance = []
        for van in vans:
            lat = van.get("location", {}).get("lat")
            lon = van.get("location", {}).get("lon")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("name"),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status"),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class HetBoerenijsjeLoenhoutSensor(IceCreamVanSensor):
    """Sensor class for Het Boerenijsje Loenhout."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=12&has_working_day=1"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = await self.get_vans()
        vans = json_data.get("data", [])
        vans_with_distance = []
        for van in vans:
            lat = van.get("latitude")
            lon = van.get("longitude")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("title", ""),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status", "").lower(),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class HetDroomijsjeBreskensSensor(IceCreamVanSensor):
    """Sensor class for Het Droomijsje Breskens."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry("https://ijsjesradar.be/status.php")

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = await self.get_vans()
        vans = [
            van
            for van in vans
            if van.get("company_ref") == "het-droomijsje"
            and van.get("status") == "online"
        ]
        vans_with_distance = []
        for van in vans:
            lat = van.get("location", {}).get("lat")
            lon = van.get("location", {}).get("lon")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("name"),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status"),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class JorisBeerseSensor(IceCreamVanSensor):
    """Sensor class for Joris Beerse."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=4&has_working_day=1"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = await self.get_vans()
        vans = json_data.get("data", [])
        vans_with_distance = []
        for van in vans:
            lat = van.get("latitude")
            lon = van.get("longitude")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("title", ""),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status", "").lower(),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class PitzStekeneSensor(IceCreamVanSensor):
    """Sensor class for Pitz Stekene."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://map-pitz-ijs.vercel.app/api/?purge=false"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = await self.get_vans()
        vans = [van for van in vans if van.get("active")]
        vans_with_distance = []
        for van in vans:
            lat = van.get("lat")
            lng = van.get("lng")
            if lat is None or lng is None:
                continue
            distance = haversine(van["lat"], van["lng"], self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("naam"),
                    "latitude": lat,
                    "longitude": lng,
                    "status": "active" if van.get("active") else "inactive",
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class TartisteDeinzeSensor(IceCreamVanSensor):
    """Sensor class for Tartiste Deinze."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=8&has_working_day=1"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = await self.get_vans()
        vans = json_data.get("data", [])
        vans_with_distance = []
        for van in vans:
            lat = van.get("latitude")
            lon = van.get("longitude")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("title", ""),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status", "").lower(),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class VanDeWalleTemseSensor(IceCreamVanSensor):
    """Sensor class for Van De Walle Temse."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://www.ijsvandewalle.be/map/result.json"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = await self.get_vans()
        vans_with_distance = []
        for van in vans:
            lat = van.get("latitude")
            lon = van.get("longitude")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("label", ""),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status"),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)


class VanillaPlusOostendeSensor(IceCreamVanSensor):
    """Sensor class for Vanilla Plus."""

    async def get_vans(self):
        """Get vans."""
        return await self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=11&has_working_day=1"
        )

    async def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = await self.get_vans()
        vans = json_data.get("data", [])
        vans_with_distance = []
        for van in vans:
            lat = van.get("latitude")
            lon = van.get("longitude")
            if lat is None or lon is None:
                continue
            distance = haversine(lat, lon, self._user_lat, self._user_lon)
            vans_with_distance.append(
                {
                    "company": self._company,
                    "label": van.get("title", ""),
                    "latitude": lat,
                    "longitude": lon,
                    "status": van.get("status", "").lower(),
                    "distance": round(distance, 2),
                }
            )
        return min(vans_with_distance, key=lambda x: x["distance"], default=None)
