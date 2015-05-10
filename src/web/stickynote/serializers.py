from rest_framework import serializers
from .models import StickyNote
from rest_framework.validators import ValidationError


class StickyNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = StickyNote
        fields = ('identifier', 'active', 'time', 'note', 'created_at', 'updated_at')
        read_only_fields = ('identifier', 'active', 'created_at', 'updated_at')


class StickyNoteToggleSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        identifier = data.get('identifier')

        if not identifier:
            raise ValidationError({
                'identifier': 'This field is required.'
            })

        return {
            'identifier': identifier
        }
