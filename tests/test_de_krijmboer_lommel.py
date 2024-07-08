import pytest
from custom_components.ice_cream_benelux.sensor import DeKrijmboerLommelSensor

class MockDeKrijmboerLommelSensor(DeKrijmboerLommelSensor):
    async def get_vans(self):
        return {
            "data": [
                {
                    "title": "#1 Pistache",
                    "latitude": 51.2328,
                    "longitude": 5.3286117,
                },
                {
                    "title": "#5 Mokka",
                    "latitude": 51.221215,
                    "longitude": 5.4153667,
                }
            ]
        }

mock_sensor = MockDeKrijmboerLommelSensor(
    config={},
    company="De Krijmboer Lommel",
    user_lat=51.221215,
    user_lon=5.4153667
)

@pytest.mark.asyncio
async def test_get_nearest_van():
    nearest_van = await mock_sensor.get_nearest_van()
    assert nearest_van is not None
    assert nearest_van["label"] == "#5 Mokka"
    assert nearest_van["latitude"] == 51.221215
    assert nearest_van["longitude"] == 5.4153667
    assert nearest_van["distance"] == 0.0
