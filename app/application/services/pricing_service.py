from decimal import Decimal
from math import atan2, cos, radians, sin, sqrt

from app.core.config import Settings


class OrderPricingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def calculate_delivery_distance_km(self, latitude: float, longitude: float) -> Decimal:
        earth_radius_km = 6371
        lat1 = radians(self.settings.restaurant_latitude)
        lon1 = radians(self.settings.restaurant_longitude)
        lat2 = radians(latitude)
        lon2 = radians(longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return Decimal(str(round(earth_radius_km * c, 2)))

    def calculate_delivery_fee(self, distance_km: Decimal) -> Decimal:
        base = Decimal(str(self.settings.delivery_base_fee))
        per_km = Decimal(str(self.settings.delivery_fee_per_km))
        return (base + (distance_km * per_km)).quantize(Decimal("0.01"))
