from django.db import models

class Sequence(models.Model):
    name = models.CharField("Название последовательности", max_length=100)
    is_active = models.BooleanField("Активная", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Последовательность"
        verbose_name_plural = "Последовательности"

    def __str__(self):
        return f"{self.name} ({'активна' if self.is_active else 'неактивна'})"
    
    def save(self, *args, **kwargs):
        # Если эта последовательность становится активной, деактивируем остальные
        if self.is_active:
            Sequence.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class Number(models.Model):
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name='numbers', verbose_name="Последовательность")
    value = models.IntegerField("Число")
    position = models.PositiveIntegerField("Позиция", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']
        verbose_name = "Число"
        verbose_name_plural = "Числа"

    def __str__(self):
        return f"{self.value} (позиция: {self.position})"
