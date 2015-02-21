from rest_framework import serializers
from authentication.models import Account

class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Account
        fields = ('id', 'email','username','teaching_institution','first_name','last_name','password','confirm_password')
        read_only_fields = ('created_at','updated_at')

        def create(self, validated_data):
            return Account.objects.create(**validated_data)

        def update(self, instance, validated_data):
            instance.email = validated_data.get('email', instance.email)
            instance.username = validated_data.get('username', instance.username)
            instance.teaching_institution = validated_data.get('teaching_institution', instance.teaching_institution)
            instance.first_name = validated_data.get('first_name', instance.first_name)
            instance.last_name = validated_data.get('last_name', instance.last_name)

            instance.save()

            password = validated_data.get('password', None)
            confirm_password = validated_data.get('confirm_password', None)

            if password and confirm_password and password == confirm_password:
                instance.set_password(password)
                instance.save()

            return instance

