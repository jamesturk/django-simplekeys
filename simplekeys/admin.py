from django.contrib import admin

from .models import Tier, Zone, Limit, Key


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'email', 'name', 'tier', 'status', 'created_at')
    list_filter = ('tier', 'status')
    search_fields = ('email', 'name', 'key')
    list_select_related = ('tier',)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}


class LimitInline(admin.TabularInline):
    model = Limit
    extra = 1


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [
        LimitInline,
    ]
