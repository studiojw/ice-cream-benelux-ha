import pytest
from custom_components.ice_cream_benelux.sensor import GlaceDeBockBeverenSensor

class GlaceDeBockBeverenSensor(GlaceDeBockBeverenSensor):
    async def get_vans(self):
        return [
            {
                "truck_ref": "db1",
                "company_ref": "de-bock",
                "name": "Glacé De Bock #1",
                "status": "online",
                "location": {"lat": 51.1784796, "lon": 4.2148736},
            },
            {
                "truck_ref": "db2",
                "company_ref": "de-bock",
                "name": "Glacé De Bock #2",
                "status": "online",
                "location": {"lat": 51.1984796, "lon": 4.2168736},
            }
        ]


mock_sensor = GlaceDeBockBeverenSensor(
    config={},
    company="Foubert Sint-Niklaas",
    user_lat=51.1658,
    user_lon=4.4251,
)


@pytest.mark.asyncio
async def test_get_nearest_van_1():
    nearest_van = await mock_sensor.get_nearest_van()
    assert nearest_van is not None
    assert nearest_van["label"] == "Glacé De Bock #1"
    assert nearest_van["latitude"] == 51.1784796
    assert nearest_van["longitude"] == 4.2148736
    assert nearest_van["distance"] == 14.72

class GlaceDeBockBeverenSensor2(GlaceDeBockBeverenSensor):
    async def get_vans(self):
        return [
            {
                "truck_ref": "db1",
                "company_ref": "de-bock",
                "name": "Glacé De Bock #1",
                "status": "offline",
                "location": {"lat": 51.1784796, "lon": 4.2148736},
            },
            {
                "truck_ref": "db2",
                "company_ref": "de-bock",
                "name": "Glacé De Bock #2",
                "status": "offline",
                "location": {"lat": 51.1984796, "lon": 4.2168736},
            }
        ]


mock_sensor2 = GlaceDeBockBeverenSensor2(
    config={},
    company="Foubert Sint-Niklaas",
    user_lat=51.1658,
    user_lon=4.4251,
)


@pytest.mark.asyncio
async def test_get_nearest_van_all_vans_offline():
    nearest_van = await mock_sensor2.get_nearest_van()
    assert nearest_van is None
