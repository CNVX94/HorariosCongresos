from django import forms
from .models import Talk, Day, Room, Slot, ActivityType, Reservation

class TalkForm(forms.ModelForm):
    day = forms.ModelChoiceField(
        queryset=Day.objects.none(),
        label="Día preferido",
        required=True,
        help_text="Selecciona el día en el que deseas dar tu charla (solo días con espacio disponible)"
    )
    activity_type = forms.ModelChoiceField(
        queryset=ActivityType.objects.all(),
        label="Tipo de actividad",
        required=True,
        help_text="Conferencia, ponencia o taller"
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        label="Salón preferido",
        required=True,
        help_text="Elige un salón con disponibilidad en ese día"
    )
    slot = forms.ModelChoiceField(
        queryset=Slot.objects.none(),
        label="Horario",
        required=True,
        help_text="Elige el horario disponible"
    )

    class Meta:
        model = Talk
        fields = ['title', 'author_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Días que tienen al menos un slot libre (sin reserva)
        available_days = Day.objects.filter(slots__reservations__isnull=True).distinct()
        self.fields['day'].queryset = available_days

        # Si hay día seleccionado (por POST o GET), ajustamos rooms y slots
        if self.data.get('day'):
            try:
                day_id = int(self.data.get('day'))
                day = Day.objects.get(pk=day_id)
                # Verificar si hay slots libres en el día
                if day.slots.filter(reservations__isnull=True).exists():
                    self.fields['room'].queryset = Room.objects.all()
                else:
                    self.fields['room'].queryset = Room.objects.none()

                # Si también hay tipo y room, filtrar slots
                if self.data.get('activity_type') and self.data.get('room'):
                    act_type_id = int(self.data.get('activity_type'))
                    room_id = int(self.data.get('room'))
                    act_type = ActivityType.objects.get(pk=act_type_id)
                    room = Room.objects.get(pk=room_id)
                    slots = day.slots.order_by('start_time')
                    available_slots = []
                    for slot in slots:
                        if act_type.name in ['conferencia', 'ponencia']:
                            if not slot.reservations.exists():
                                available_slots.append(slot.id)
                        elif act_type.name == 'taller':
                            if not Reservation.objects.filter(slot=slot, room=room).exists():
                                available_slots.append(slot.id)
                    self.fields['slot'].queryset = Slot.objects.filter(id__in=available_slots)
            except (ValueError, Day.DoesNotExist, ActivityType.DoesNotExist, Room.DoesNotExist):
                pass