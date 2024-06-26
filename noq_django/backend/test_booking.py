from django.test import TestCase
from django.core.exceptions import ValidationError

# Generated by CodiumAI
from backend.models import Booking
from datetime import datetime
from backend.models import Product
from backend.models import BookingStatus
from backend.models import Available
from datetime import timedelta
from backend.models import Region, Client, User, Host


class test_Booking(TestCase):

    def setUp(self):

        region = Region(name="City")
        region.save()

        Host.objects.create(name="Host", city="City", region=region),

        user = User()
        user.save()

        male_client = Client.objects.create(
            first_name="John",
            last_name="Doe",
            gender="M",
            street="123 Main St",
            postcode="12345",
            city="New York",
            country="USA",
            phone="123-456-7890",
            email="john.doe@example.com",
            unokod="ABC123",
            day_of_birth=datetime.now().date(),
            personnr_lastnr="1234",
            region=Region.objects.get(name="City"),
            requirements=None,
            last_edit=datetime.now().date(),
            user=user,
        )

        female_client = Client.objects.create(
            first_name="Mary",
            last_name="Doe",
            gender="K",
            street="123 Main St",
            postcode="12345",
            city="New York",
            country="USA",
            phone="123-456-7890",
            email="john.doe@example.com",
            unokod="ABC123",
            day_of_birth=datetime.now().date(),
            personnr_lastnr="1234",
            region=Region.objects.get(name="City"),
            requirements=None,
            last_edit=datetime.now().date(),
            user=user,
        )

        # Create a woman-only product
        product = Product.objects.create(
            name="Product",
            description="Description",
            total_places=10,
            host=Host.objects.get(city="City"),
            type="woman-only",
            requirements=None,
        )

        status = BookingStatus.objects.create(id=1, description="pending")

    # Booking a product with valid data saves the booking and updates availability
    def test_booking_with_valid_data(self):

        # Initialize a Booking object
        booking = Booking()

        # Set the attributes of the Booking object
        booking.start_date = datetime.now() + timedelta(days=1)
        booking.product = Product.objects.first()
        booking.user = Client.objects.get(gender="K")
        booking.status = BookingStatus.objects.get(id=1)

        # Save the Booking object
        booking.save()

        # Assert that the booking is saved
        assert Booking.objects.filter(id=booking.id).exists()

        # Assert that availability is updated
        availability = Available.objects.filter(
            product=booking.product, available_date=booking.start_date
        ).first()
        assert availability is not None
        assert availability.places_left == booking.product.total_places - 1

    # Booking a product with an invalid date raises ValidationError
    def test_booking_with_invalid_date(self):

        product = Product.objects.get(id=1)
        client = Client.objects.get(gender="K")
        status = BookingStatus.objects.first()

        # Initialize a Booking object
        booking = Booking()

        # Set the attributes of the Booking object with an invalid date
        booking.start_date = datetime.now() - timedelta(days=1)
        booking.product = product
        booking.user = client
        booking.status = status

        # Assert that a ValidationError is raised when trying to save the booking
        with self.assertRaises(ValidationError):
            booking.save()

    # Booking a product with a male user and woman-only type raises ValidationError
    def test_booking_with_male_user_and_woman_only_type_raises_validation_error(
        self,
    ):
        # Create a male user
        client = Client.objects.get(gender="M")

        # Create a woman-only product
        product = Product.objects.create(
            name="Product",
            description="Description",
            total_places=10,
            host=Host.objects.get(city="City"),
            type="woman-only",
            requirements=None,
        )

        # Try to book the product with the male user
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                start_date=datetime.now().date(),
                product=product,
                user=client,
                status=BookingStatus.objects.create(description="pending"),
            )

    # Booking a product with the same user and date as the current booking does not raise ValidationError
    def test_booking_with_same_user_and_date(self):
        # Create a booking with valid data
        booking = Booking()
        booking.start_date = datetime.now()
        booking.product = Product.objects.get(id=1)
        booking.user = Client.objects.get(gender="K")
        booking.status = BookingStatus.objects.get(id=1)
        booking.save()

        # Try to create another booking with the same user and date
        duplicate_booking = Booking()
        duplicate_booking.start_date = booking.start_date
        duplicate_booking.product = booking.product
        duplicate_booking.user = Client.objects.get(gender="K")
        duplicate_booking.status = booking.status

        # Assert that a ValidationError is raised
        with self.assertRaises(ValidationError):
            duplicate_booking.save()

        # Assert that the original booking still exists
        assert Booking.objects.filter(id=booking.id).exists()

        # Assert that availability is not updated
        availability = Available.objects.filter(
            product=booking.product, available_date=booking.start_date
        ).first()
        assert availability is not None
        assert availability.places_left == booking.product.total_places - 1
