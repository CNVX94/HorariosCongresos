from django.contrib import admin
from .models import Congress, Day, Slot, Talk, Room, Reservation, ActivityType, SLOT_MINS

class SlotInline(admin.TabularInline):
    model = Slot
    extra = 0
    readonly_fields = ('start_time', 'duration_mins')
    can_delete = False

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
        total, occupied = obj.get_occupancy_stats()
        return f"{occupied} / {total}"
    get_occupancy.short_description = 'Ocupación'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'duration_mins')
    list_filter = ('day__congress', 'day')

@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'email', 'created_at')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('talk', 'slot', 'room')
    list_filter = ('room', 'slot__day')

@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')