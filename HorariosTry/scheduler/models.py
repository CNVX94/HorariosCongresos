from datetime import datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

SLOT_MINS = 25

class Congress(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError('La fecha de inicio no puede ser posterior a la de fin.')

    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Day(models.Model):
    congress = models.ForeignKey(Congress, on_delete=models.CASCADE, related_name='days')
    date = models.DateField()
    hours_budget = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('congress', 'date')

    def clean(self):
        # Validar que la fecha esté dentro del rango del congreso
        if self.date < self.congress.start_date or self.date > self.congress.end_date:
            raise ValidationError(f'La fecha debe estar entre {self.congress.start_date} y {self.congress.end_date}.')

    def save(self, *args, **kwargs):
        self.full_clean()  # valida antes de guardar
        if self.pk:
            old = Day.objects.get(pk=self.pk)
            budget_changed = old.hours_budget != self.hours_budget
        else:
            budget_changed = False
        super().save(*args, **kwargs)
        # Regenerar slots solo si es nuevo o cambió el presupuesto
        if budget_changed or not self.slots.exists():
            self.regenerate_slots()

    def regenerate_slots(self):
        """Crea los slots de tiempo (sin salón) basados en hours_budget"""
        # Borrar slots existentes (se perderán reservas, pero eso es coherente con cambio de presupuesto)
        self.slots.all().delete()
        total_minutes = self.hours_budget * 60
        num_slots = total_minutes // SLOT_MINS
        start_time = datetime.combine(self.date, datetime.min.time()) + timedelta(hours=9)  # 9 AM
        slots_to_create = []
        for i in range(num_slots):
            slot_start = start_time + timedelta(minutes=i * SLOT_MINS)
            slots_to_create.append(Slot(day=self, start_time=slot_start, duration_mins=SLOT_MINS))
        Slot.objects.bulk_create(slots_to_create)

    def get_occupancy_stats(self):
        """Devuelve (total_slots, occupied_slots) considerando reservas"""
        total = self.slots.count()
        occupied = Reservation.objects.filter(slot__day=self).values('slot').distinct().count()
        return total, occupied

    def __str__(self):
        return f"{self.date} ({self.congress.name})"

class Slot(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='slots')
    start_time = models.DateTimeField()
    duration_mins = models.IntegerField(default=SLOT_MINS)

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration_mins)

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Talk(models.Model):
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=150)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Reservation(models.Model):
    talk = models.OneToOneField(Talk, on_delete=models.CASCADE, related_name='reservation')
    slot = models.OneToOneField(Slot, on_delete=models.CASCADE, related_name='reservation')  # OneToOne
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')

    class Meta:
        # Ya no necesitamos unique_together porque slot ya es único con OneToOne
        pass

    def __str__(self):
        return f"{self.talk.title} - {self.slot.day.date} {self.slot} - {self.room.name}"
