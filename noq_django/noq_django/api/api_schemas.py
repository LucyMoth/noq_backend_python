from ninja import NinjaAPI, Schema, ModelSchema
from typing import Optional
from backend.models import (
    Client,
    Host,
    Region,
    Product,
    Booking,
    Available,
)

from typing import List, Dict
from django.shortcuts import get_object_or_404
from ninja.security import django_auth, django_auth_superuser, HttpBearer
from datetime import date, timedelta


class RegionSchema(ModelSchema):
    """

    Region

    Exempelvis Stockholm City och Farsta

    Varje Host tillhör en Region
    """

    class Meta:
        model = Region
        fields = "__all__"


class UserSchema(ModelSchema):
    """
    User - för både Brukare och användare i systemet

    Varje user tillhör en Region
    """

    region: RegionSchema

    class Meta:
        model = Client
        fields = "__all__"


class UserPostSchema(Schema):
    """
    User för POST-anrop

    """

    first_name: str
    last_name: str
    gender: str
    phone: str
    email: str
    region_id: int
    unokod: str = None


class HostSchema(ModelSchema):
    """

    Host

    Exempelvis Stadsmissionen, Stockholm

    Varje Host tillhör en Region
    """

    region: RegionSchema

    class Meta:
        model = Host
        exclude = ("blocked_clients","users",)


# Mall för Add dvs POST
class HostPostSchema(ModelSchema):
    """
    Host eller Härbärge för POST

    """

    class Meta:
        model = Host
        exclude = ["id", "region"]
        fields = "__all__"


class HostPatchSchema(Schema):
    """
    Host eller Härbärge för PATCH (update)

    Video to learn: https://www.youtube.com/watch?v=OGUqBay7BP0&t=919s

    """

    name: Optional[str] = None
    street: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    region: Optional[RegionSchema] = None

    class Meta:
        model = Host
        fields = ["id"]  # Note: all these fields are required on model level
        fields_optional = "__all__"


class ProductSchema(Schema):
    """
    Product
    Product är en generalisering istället för exempelvis Room
    som gör det möjligt att Härbärge kan erbjuda många tjänster.
    Exempelvis rum eller luncher
    """

    id: int
    name: str
    description: str
    total_places: int
    host: HostSchema = None
    type: str

class ProductSchemaWithPlacesLeft(ProductSchema):
    places_left: int


class StatusSchema(Schema):
    description: str

class BookingSchema(Schema):
    """
    Booking för att bokningar av en Product

    """
    id: int
    status: StatusSchema
    start_date: date
    product: ProductSchema
    user: UserSchema


class BookingPostSchema(Schema):
    """
    Booking för att boka en Product

    """

    start_date: date
    product_id: int



class AvailableSchema(Schema):
    """
    Available för att kunna se om en Product har tillgängliga platser

    """

    id: int
    available_date: date
    product: ProductSchema
    places_left: int

class AvailableProductsSchema(Schema):
    host: HostSchema
    products: List[ProductSchemaWithPlacesLeft]

class BookingCounterSchema(Schema):
    pending_count: int
    arrivals_count: int
    departures_count: int
    current_guests_count: int
    available_products: Dict[str, int]

class LoginPostSchema(Schema):
    email: str
    password: str
    
class LoginSchema(Schema):
    login_status: bool
    message: str
    groups: Optional[List[str]] = None
