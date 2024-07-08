import pytest
from custom_components.ice_cream_benelux.sensor import DeKremkerreMelleSensor

class MockDeKremkerreMelleSensor(DeKremkerreMelleSensor):
    async def get_vans(self):
        return [
            {
                "truck_ref": "dk2",
                "company_ref": "de-kremkerre",
                "name": "De Kremvélo #2",
                "status": "online",
                "location": {
                    "lat": 51.0452559,
                    "lon": 3.7526505
               }
            }
        ]

mock_sensor = MockDeKremkerreMelleSensor(
    config={},
    company="De Kremkerre Melle",
    user_lat=51.1658,
    user_lon=4.4251
)

@pytest.mark.asyncio
async def test_get_nearest_van():
    nearest_van = await mock_sensor.get_nearest_van()
    assert nearest_van is not None
    assert nearest_van["label"] == "De Kremvélo #2"
    assert nearest_van["latitude"] == 51.0452559
    assert nearest_van["longitude"] == 3.7526505
    assert nearest_van["distance"] == 48.82

