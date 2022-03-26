from rest_framework import serializers
from .models import *


class EmailSerializer(serializers.ModelSerializer):
    receivers = serializers.StringRelatedField(many=True)
    label = serializers.StringRelatedField(many=True)
    cc = serializers.StringRelatedField(many=True)
    bcc = serializers.StringRelatedField(many=True)
    signature = serializers.StringRelatedField()
    sender = serializers.StringRelatedField()

    class Meta:
        model = Email
        fields = "__all__"
