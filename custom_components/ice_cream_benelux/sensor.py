"""Sensor platform for ice_cream_benelux."""

import logging

import voluptuous as vol

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import COMPANIES
from .http_client import HTTPClient
from .utils_location import haversine
from .utils_string import snake_to_pascal_case

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Ice Cream Benelux"

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_LATITUDE): cv.latitude,
        vol.Required(CONF_LONGITUDE): cv.longitude,
        vol.Required("companies", default=[]): vol.All(
            cv.ensure_list, [vol.In(COMPANIES.keys())]
        ),
    }
)


def setup_platform(
    hass: HomeAssistant | None, config, add_entities, discovery_info=None
):
    """Set up the sensor platform."""
    lat = config.get(CONF_LATITUDE)
    lon = config.get(CONF_LONGITUDE)
    selected_companies = config.get("companies")

    sensors = []
    for company in selected_companies:
        sensor_class_name = snake_to_pascal_case(company) + "Sensor"
        sensor_class = globals().get(sensor_class_name)
        if sensor_class:
            sensors.append(sensor_class(config, COMPANIES.get(company), lat, lon))
        else:
            _LOGGER.error("No sensor class found for %s", company)

    add_entities(sensors, True)


class IceCreamVanSensor(SensorEntity):
    """Sensor class for ice_cream_benelux."""

    def __init__(self, config, company, user_lat, user_lon) -> None:
        """Initialize the sensor."""
        self._name = f"{config.get(CONF_NAME)} {company}"
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

    def update(self):
        """Update sensor."""
        self.set_van_state()

    def set_van_state(self):
        """Get nearest van and set state."""
        try:
            van = self.get_nearest_van()
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

    def get_nearest_van(self):
        """Get the nearest van. To be implemented by subclasses."""
        raise NotImplementedError


class DeKremkerreMelleSensor(IceCreamVanSensor):
    """Sensor class for De Kremkerre Melle."""

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry("https://ijsjesradar.be/status.php")

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = self.get_vans()
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


class FoubertSintNiklaasSensor(IceCreamVanSensor):
    """Sensor class for Foubert Sint-Niklaas."""

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=2&has_working_day=1"
        )

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = self.get_vans()
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

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry("https://ijsjesradar.be/status.php")

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = self.get_vans()
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


class HetDroomijsjeBreskensSensor(IceCreamVanSensor):
    """Sensor class for Het Droomijsje Breskens."""

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry("https://ijsjesradar.be/status.php")

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = self.get_vans()
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

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=4&has_working_day=1"
        )

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = self.get_vans()
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

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry(
            "https://map-pitz-ijs.vercel.app/api/?purge=false"
        )

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = self.get_vans()
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

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry(
            "https://api.icecorp.be/v1/icecreamvanmarkerdata?company_id=8&has_working_day=1"
        )

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        json_data = self.get_vans()
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

    def get_vans(self):
        """Get vans."""
        return self._http.request_with_retry(
            "https://www.ijsvandewalle.be/map/result.json"
        )

    def get_nearest_van(self) -> dict | None:
        """Get nearest van."""
        vans = self.get_vans()
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
