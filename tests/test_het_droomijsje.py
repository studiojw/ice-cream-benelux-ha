import pytest
from custom_components.ice_cream_benelux.sensor import HetDroomijsjeBreskensSensor

class MockHetDroomijsjeBreskensSensor(HetDroomijsjeBreskensSensor):
    async def get_vans(self):
        return [
            {
                "truck_ref": "di1",
                "company_ref": "het-droomijsje",
                "name": "Het Droomijsje",
                "status": "online",
                "location": {
                    "lat": 51.2718988,
                    "lon": 3.454313
               }
            },
            {
                "truck_ref": "di2",
                "company_ref": "het-droomijsje",
                "name": "Het Droomijsje Camping",
                "status": "online",
                "location": {
                    "lat": 51.380838,
                    "lon": 3.4014555
               }
            }
        ]

mock_sensor = MockHetDroomijsjeBreskensSensor(
    config={},
    company="Het Droomijsje Breskens",
    user_lat=51.380838,
    user_lon=3.4014555
)

@pytest.mark.asyncio
async def test_get_nearest_van():
    nearest_van = await mock_sensor.get_nearest_van()
    assert nearest_van is not None
    assert nearest_van["label"] == "Het Droomijsje Camping"
    assert nearest_van["latitude"] == 51.380838
    assert nearest_van["longitude"] == 3.4014555
    assert nearest_van["distance"] == 0

class MockHetDroomijsjeBreskensSensor2(HetDroomijsjeBreskensSensor):
    async def get_vans(self):
        return []

mock_sensor = MockHetDroomijsjeBreskensSensor2(
    config={},
    company="Het Droom Ijsje Breskens",
    user_lat=51.380838,
    user_lon=3.4014555
)

@pytest.mark.asyncio
async def test_get_nearest_van():
    nearest_van = await mock_sensor.get_nearest_van()
    assert nearest_van is None

