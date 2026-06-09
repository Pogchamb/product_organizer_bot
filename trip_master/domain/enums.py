from enum import Enum


class Category(str, Enum):
    food = "food"
    household = "household"


class TripStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
