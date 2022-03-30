from rest_framework import serializers
from .models import *


class ContactSerializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Contact
        fields = "__all__"