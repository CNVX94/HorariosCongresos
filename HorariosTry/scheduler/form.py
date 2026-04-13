from django import forms
from .models import Talk, Day, Room, Reservation, Slot, SLOT_MINS

class TalkForm(forms.ModelForm):
    day = forms.ModelChoiceField(
        queryset=Day.objects.none(),  # se llena dinámicamente
        label="Día preferido",
        required=True,
        help_text="Selecciona el día en el que deseas dar tu charla (solo días con espacio disponible)"
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        label="Salón preferido",
        required=True,
        help_text="Elige un salón con disponibilidad en ese día"
    )

    class Meta:
        model = Talk
        fields = ['title', 'author_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo días que tengan al menos un slot sin reserva en algún salón? 
        # Pero la disponibilidad depende del salón elegido, así que cargaremos dinámicamente.
        # Inicialmente, mostramos todos los días (luego se filtrarán por JS)
        self.fields['day'].queryset = Day.objects.all()
        if self.data.get('day'):
            try:
                day_id = int(self.data.get('day'))
                day = Day.objects.get(pk=day_id)
                # Salones que tienen al menos un slot libre en ese día (sin reserva)
                occupied_slots_in_day = Reservation.objects.filter(slot__day=day).values_list('slot_id', flat=True)
                free_slots = day.slots.exclude(id__in=occupied_slots_in_day)
                if free_slots.exists():
                    # Cualquier salón se puede usar mientras haya al menos un slot libre
                    self.fields['room'].queryset = Room.objects.all()
                else:
                    self.fields['room'].queryset = Room.objects.none()
                    self.fields['room'].help_text = "No hay horarios libres en este día."
            except (ValueError, Day.DoesNotExist):
                self.fields['room'].queryset = Room.objects.none()
        else:
            self.fields['room'].queryset = Room.objects.none()