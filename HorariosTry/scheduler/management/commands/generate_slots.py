from django.core.management.base import BaseCommand
from django.utils import timezone
from scheduler.models import Day, Slot
from datetime import datetime, timedelta

# Definir SLOT_MINS localmente (o importar desde models)
SLOT_MINS = 25

class Command(BaseCommand):
    help = 'Regenera los slots para uno o todos los días (borra y crea de nuevo)'

    def add_arguments(self, parser):
        parser.add_argument('--day_id', type=int, help='ID de un día específico')

    def handle(self, *args, **options):
        if options['day_id']:
            days = Day.objects.filter(id=options['day_id'])
        else:
            days = Day.objects.all()

        if not days.exists():
            self.stdout.write(self.style.ERROR('No se encontraron días.'))
            return

        for day in days:
            # Borrar slots existentes
            deleted_count, _ = day.slots.all().delete()
            total_minutes = day.hours_budget * 60
            num_slots = total_minutes // SLOT_MINS
            # Hora de inicio fija: 9:00 AM
            start_time = datetime.combine(day.date, datetime.min.time()) + timedelta(hours=9)
            created = 0
            for i in range(num_slots):
                Slot.objects.create(
                    day=day,
                    start_time=start_time + timedelta(minutes=i * SLOT_MINS),
                    duration_mins=SLOT_MINS
                )
                created += 1
            self.stdout.write(self.style.SUCCESS(
                f'Día {day.date}: eliminados {deleted_count} slots, creados {created} nuevos.'
            ))