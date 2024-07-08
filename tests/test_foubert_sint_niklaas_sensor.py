import pytest
from custom_components.ice_cream_benelux.sensor import FoubertSintNiklaasSensor

class MockFoubertSintNiklaasSensor(FoubertSintNiklaasSensor):
    async def get_vans(self):
        return {
            "data": [
                {
                    "title": "#1 Vanille",
                    "latitude": 51.1657,
                    "longitude": 4.4250,
                },
                {
                    "title": "#5 Limoncello",
                    "latitude": 51.1658,
                    "longitude": 4.4251,
                }
            ]
        }

mock_sensor = MockFoubertSintNiklaasSensor(
    config={},
    company="Foubert Sint-Niklaas",
    user_lat=51.1658,
    user_lon=4.4251
)

@pytest.mark.asyncio
async def test_get_nearest_van():
    nearest_van = await mock_sensor.get_nearest_van()
    assert nearest_van is not None
    assert nearest_van["label"] == "#5 Limoncello"
    assert nearest_van["latitude"] == 51.1658
    assert nearest_van["longitude"] == 4.4251
    assert nearest_van["distance"] == 0.0
