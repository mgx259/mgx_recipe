from rest_framework import serializers

from core.models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Seraizlizer for TAG object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Seraializer for Ingredient object"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_Fields = ('id',)
