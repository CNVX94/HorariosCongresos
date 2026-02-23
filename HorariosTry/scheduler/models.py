from django.db import models
from django.core.validators import MinValueValidator

SLOT_MINS = 25

class Congress(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Day(models.Model):
    congress = models.ForeignKey(Congress, on_delete=models.CASCADE, related_name='days')
    date = models.DateField()
    hours_budget = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.date} ({self.congress.name})"

class Talk(models.Model):
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=150)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Slot(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='slots')
    start_time = models.DateTimeField()
    duration_mins = models.IntegerField(default=SLOT_MINS)
    talk = models.OneToOneField(Talk, on_delete=models.SET_NULL, null=True, blank=True, related_name='slot')

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.talk.title if self.talk else 'Free'}"
