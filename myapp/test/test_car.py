import pytest

from myapp.models import Car

@pytest.mark.django_db
class TestCar:
    def test_car(self):
        Car.objects.create(
            name="fox",
            price=100,
            age=10,
        )

        assert Car.objects.count() == 1

    def test_car_not_exist(self):
        with pytest.raises(Car.DoesNotExist):
            Car.objects.get(name="fox")
