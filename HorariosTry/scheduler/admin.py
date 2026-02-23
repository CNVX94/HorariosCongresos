from django.contrib import admin
from .models import Congress, Day, Slot, Talk, SLOT_MINS

class SlotInline(admin.TabularInline):
    model = Slot
    extra = 0
    readonly_fields = ('start_time', 'duration_mins', 'talk')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

class DayInline(admin.TabularInline):
    model = Day
    extra = 0
    show_change_link = True

@admin.register(Congress)
class CongressAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    inlines = [DayInline]

@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('congress', 'date', 'hours_budget', 'get_occupancy')
    list_filter = ('congress',)
    inlines = [SlotInline]

    def get_occupancy(self, obj):
        cupo = (obj.hours_budget * 60) // SLOT_MINS
        filled = obj.slots.filter(talk__isnull=False).count()
        return f"{filled} / {cupo}"
    get_occupancy.short_description = 'Occupancy'

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'duration_mins', 'talk_status')
    list_filter = ('day',)

    def talk_status(self, obj):
        return obj.talk.title if obj.talk else "Free"
    talk_status.short_description = 'Talk / Status'

@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'email', 'created_at')
