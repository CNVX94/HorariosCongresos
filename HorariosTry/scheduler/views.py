from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Talk, Slot, Day, SLOT_MINS

class TalkCreate(CreateView):
    model = Talk
    fields = ["title", "author_name", "email"]
    template_name = "scheduler/talk_form.html"
    success_url = reverse_lazy('talk_success')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                talk = form.save()
                self.assign_slot(talk)
                self.object = talk
                return HttpResponseRedirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def assign_slot(self, talk):
        # Fetch available slots chronologically
        free_slots = Slot.objects.select_related('day').filter(talk__isnull=True).order_by('day__date', 'start_time')
        
        for slot in free_slots:
            cupo = (slot.day.hours_budget * 60) // SLOT_MINS
            # Check capacity constraint per rule #1
            if slot.day.slots.filter(talk__isnull=False).count() < cupo:
                # Lock slot for atomic assignment
                assignable_slot = Slot.objects.select_for_update().get(pk=slot.pk)
                if not assignable_slot.talk:
                    assignable_slot.talk = talk
                    assignable_slot.save()
                    return
                    
        raise ValidationError("No free slots on the selected day")

class DayPrintView(DetailView):
    model = Day
    template_name = "scheduler/day_print.html"
    context_object_name = "day"
