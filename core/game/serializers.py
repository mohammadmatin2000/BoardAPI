from rest_framework import serializers
from .models import Game, Move
# ======================================================================================================================
# Serializer برای مدل Game
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
# ======================================================================================================================
# Serializer برای مدل Move
class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = '__all__'
# ======================================================================================================================