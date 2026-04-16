from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Talk, Day, Room, Reservation, Slot, ActivityType
from .form import TalkForm

class DayListView(ListView):
    model = Day
    template_name = "scheduler/day_list.html"
    context_object_name = "days"
    ordering = ['date']

class DayPrintView(DetailView):
    model = Day
    template_name = "scheduler/day_print.html"
    context_object_name = "day"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        day = self.get_object()
        # Obtener todas las reservas de este día, ordenadas por hora y salón
        reservations = Reservation.objects.filter(slot__day=day).select_related(
            'slot', 'talk', 'room', 'talk__activity_type'
        ).order_by('slot__start_time', 'room__name')
        
        # Crear una lista de diccionarios con los datos necesarios
        reservations_data = []
        for res in reservations:
            reservations_data.append({
                'start_time': res.slot.start_time,
                'end_time': res.slot.end_time,
                'title': res.talk.title,
                'author': res.talk.author_name,
                'activity_type': res.talk.activity_type.name,
                'room_name': res.room.name,
                'capacity': res.room.capacity if res.room.capacity else 'N/A'
            })
        context['reservations'] = reservations_data
        return context

class TalkCreate(CreateView):
    model = Talk
    form_class = TalkForm
    template_name = "scheduler/talk_form.html"
    success_url = reverse_lazy('talk_success')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                day = form.cleaned_data.get('day')
                activity_type = form.cleaned_data.get('activity_type')
                room = form.cleaned_data.get('room')
                slot = form.cleaned_data.get('slot')
                
                # Validaciones básicas
                if not all([day, activity_type, room, slot]):
                    form.add_error(None, "Todos los campos son obligatorios.")
                    return self.form_invalid(form)
                
                # Validar que el slot pertenezca al día
                if slot.day != day:
                    form.add_error('slot', "El horario no corresponde al día seleccionado.")
                    return self.form_invalid(form)
                
                # Reglas según tipo de actividad
                if activity_type.name in ['conferencia', 'ponencia']:
                    if slot.reservations.exists():
                        form.add_error('slot', "Este horario ya está ocupado por otra actividad.")
                        return self.form_invalid(form)
                elif activity_type.name == 'taller':
                    if Reservation.objects.filter(slot=slot, room=room).exists():
                        form.add_error('room', "Este salón ya está ocupado en ese horario.")
                        return self.form_invalid(form)
                else:
                    form.add_error('activity_type', "Tipo de actividad no válido.")
                    return self.form_invalid(form)
                
                # Crear la charla (sin guardar aún la reserva)
                talk = form.save(commit=False)
                talk.activity_type = activity_type
                talk.save()
                
                # ASIGNAR self.object ANTES DE REDIRIGIR
                self.object = talk
                
                # Crear la reserva
                Reservation.objects.create(talk=talk, slot=slot, room=room)
                
                return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            # Registrar el error para depuración (puedes usar logging)
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Error inesperado: {str(e)}")
            return self.form_invalid(form)

# ... resto de imports y vistas existentes ...

def available_rooms_api(request):
    day_id = request.GET.get('day_id')
    if day_id:
        try:
            day = Day.objects.get(pk=day_id)
            # Si el día tiene al menos un slot sin reserva, mostramos todos los salones
            if day.slots.filter(reservations__isnull=True).exists():
                rooms = Room.objects.all()
                data = {'rooms': [{'id': r.id, 'name': r.name} for r in rooms]}
            else:
                data = {'rooms': []}
        except Day.DoesNotExist:
            data = {'rooms': []}
    else:
        data = {'rooms': []}
    return JsonResponse(data)

def available_slots_api(request):
    day_id = request.GET.get('day_id')
    activity_type_id = request.GET.get('activity_type_id')
    room_id = request.GET.get('room_id')
    if day_id and activity_type_id and room_id:
        try:
            day = Day.objects.get(pk=day_id)
            activity_type = ActivityType.objects.get(pk=activity_type_id)
            room = Room.objects.get(pk=room_id)
            slots = day.slots.order_by('start_time')
            available = []
            for slot in slots:
                if activity_type.name in ['conferencia', 'ponencia']:
                    # Slot disponible si no tiene ninguna reserva
                    if not slot.reservations.exists():   # porque ahora es un manager
                        available.append({
                            'id': slot.id,
                            'label': f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
                        })
                elif activity_type.name == 'taller':
                    # Slot disponible si no existe reserva con el mismo salón
                    if not Reservation.objects.filter(slot=slot, room=room).exists():
                        available.append({
                            'id': slot.id,
                            'label': f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
                        })
            return JsonResponse({'slots': available})
        except (Day.DoesNotExist, ActivityType.DoesNotExist, Room.DoesNotExist):
            pass
    return JsonResponse({'slots': []})