from rest_framework import serializers
from .models import StickyNote


class StickyNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = StickyNote
        fields = ('identifier', 'active', 'time', 'note', 'created_at', 'updated_at')
        read_only_fields = ('identifier', 'active', 'created_at', 'updated_at')