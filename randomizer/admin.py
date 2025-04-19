from django.contrib import admin
from .models import Number, Sequence

class NumberInline(admin.TabularInline):
    model = Number
    extra = 1
    fields = ['value']
    
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 1
        return 4

@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'numbers_display')
    list_editable = ('is_active',)
    inlines = [NumberInline]
    
    def numbers_display(self, obj):
        numbers = obj.numbers.order_by('position').values_list('value', flat=True)
        return ', '.join(map(str, numbers))
    numbers_display.short_description = 'Числа'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for i, instance in enumerate(instances):
            instance.position = i
            instance.save()
        formset.save_m2m()
