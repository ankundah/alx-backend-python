import django_filters
from .models import Message
from django.db.models import Q

class MessageFilter(django_filters.FilterSet):
    sender = django_filters.CharFilter(field_name='sender__email')
    before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    conversation = django_filters.UUIDFilter(field_name='conversation__id')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Message
        fields = ['sender', 'before', 'after', 'conversation', 'read']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(message_body__icontains=value) |
            Q(sender__email__icontains=value)
        )