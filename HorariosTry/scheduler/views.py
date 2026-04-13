from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Talk, Day, Room, Reservation, Slot
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
        slots = day.slots.order_by('start_time')
        rooms = Room.objects.all()
        # Construir una lista de slots, cada uno con una lista de talks por room
        slot_data = []
        for slot in slots:
            talks_by_room = []
            for room in rooms:
                reservation = Reservation.objects.filter(slot=slot, room=room).select_related('talk').first()
                talks_by_room.append(reservation.talk if reservation else None)
            slot_data.append({
                'slot': slot,
                'talks': talks_by_room
            })
        context['slot_data'] = slot_data
        context['rooms'] = rooms
        return context

class TalkCreate(CreateView):
    model = Talk
    form_class = TalkForm
    template_name = "scheduler/talk_form.html"
    success_url = reverse_lazy('talk_success')  # sin placeholders, pero por seguridad asignamos self.object

    def form_valid(self, form):
        try:
            with transaction.atomic():
                day = form.cleaned_data.get('day')
                room = form.cleaned_data.get('room')
                
                if not day or not room:
                    form.add_error(None, "Debe seleccionar un día y un salón.")
                    return self.form_invalid(form)
                
                # Buscar el primer slot del día que NO tenga reserva
                free_slot = Slot.objects.filter(day=day).exclude(reservation__isnull=False).order_by('start_time').first()
                
                if not free_slot:
                    form.add_error(None, f"No hay horarios libres en {day.date}.")
                    return self.form_invalid(form)
                
                talk = form.save(commit=False)
                talk.save()
                self.object = talk
                
                # Crear reserva con el slot libre y el salón elegido
                Reservation.objects.create(talk=talk, slot=free_slot, room=room)
                
                return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            import traceback
            form.add_error(None, f"Error interno: {str(e)}\nTraceback: {traceback.format_exc()}")
            return self.form_invalid(form)

def available_rooms_api(request):
    day_id = request.GET.get('day_id')
    if day_id:
        try:
            day = Day.objects.get(pk=day_id)
            # Verificar si hay al menos un slot libre en el día
            has_free_slots = Slot.objects.filter(day=day, reservation__isnull=True).exists()
            if has_free_slots:
                rooms = Room.objects.all()
                data = {'rooms': [{'id': r.id, 'name': r.name} for r in rooms]}
            else:
                data = {'rooms': []}
        except Day.DoesNotExist:
            data = {'rooms': []}
    else:
        data = {'rooms': []}
    return JsonResponse(data)