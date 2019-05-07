from .models import Skripsi
import django_filters


class SkripsiFilter(django_filters.FilterSet):
    class Meta:
        model = Skripsi
        fields = []