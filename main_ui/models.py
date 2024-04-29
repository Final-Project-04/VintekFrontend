from django.db import models


class HeroImage(models.Model):
    image = models.ImageField(upload_to='static/hero_images/')
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

