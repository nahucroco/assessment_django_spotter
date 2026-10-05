from django.db import models


class FuelStation(models.Model):
    opis_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=10)
    city_location = models.ForeignKey(
        "USCity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fuel_stations",
    )
    rack_id = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=3)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    geocoding_source = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    geocoding_attempted = models.BooleanField(default=False)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"

class USCity(models.Model):
    city = models.CharField(max_length=100)
    state_id = models.CharField(max_length=2)
    state_name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["city", "state_id"],
                name="unique_city_state",
            )
        ]

    def __str__(self):
        return f"{self.city}, {self.state_id}"