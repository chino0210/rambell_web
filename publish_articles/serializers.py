from rest_framework import serializers
from .models import ArticuloModel, TagModel, TagDetailModel
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import uuid
import logging

logger = logging.getLogger(__name__)

# Serializadores para Artículos
class ArticuloSerializer(serializers.ModelSerializer):
  tags = serializers.SerializerMethodField()

  class Meta:
    model = ArticuloModel
    fields = '__all__'
    read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

  def get_tags(self, obj):
    # Usamos el método get_related_tags del modelo para obtener los tags relacionados
    tags = obj.get_related_tags()
    return TagArticuloSerializer([detail.tag for detail in tags], many=True).data

class ArticuloProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = ArticuloModel
    fields = ['id', 'title', 'image']


class TagArticuloSerializer(serializers.ModelSerializer):
  class Meta:
    model = TagModel
    fields = ['id', 'name', 'status', 'color']


class ArticuloUpdateSerializer(serializers.ModelSerializer):
  title = serializers.CharField(required=False)
  written = serializers.CharField(required=False)
  status = serializers.BooleanField(required=False)
  document = serializers.CharField(required=False, allow_blank=True)
  image = serializers.CharField(required=False, allow_blank=True)

  class Meta:
    model = ArticuloModel
    fields = '__all__'
    read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    # Campos que no deben ser editados


# Serializadores para Tags
class TagDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagDetailModel
        fields = ['id', 'article_id', 'tag_id', 'status_saved']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
  details = serializers.SerializerMethodField()

  class Meta:
    model = TagModel
    fields = '__all__'

  def get_details(self, obj):
    # Optimización: Usar prefetch_related en la vista para evitar N+1 queries
    details = obj.tag_details.all()
    return TagDetailSerializer(details, many=True).data


# Serializadores para Crear Tags
class TagCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = TagModel
    fields = '__all__'
    read_only_fields = ['id', 'created_at', 'updated_at']
    # Campos que no deben ser editados


# Serializadores para Actualizar Tags
class TagDetailUpdateSerializer(serializers.ModelSerializer):
    article_id = serializers.CharField(max_length=36)  # Suponiendo que el UUID se pasa como string
    status_saved = serializers.BooleanField()

    class Meta:
        model = TagDetailModel
        fields = ['article_id', 'status_saved']

    def validate_article_id(self, value):
        try:
            # Validamos que el article_id sea un UUID válido
            uuid.UUID(value)
        except ValueError:
            raise serializers.ValidationError(f"El article_id '{value}' no es un UUID válido.")
        return value

    def update(self, instance, validated_data):
        # Actualiza el detalle del artículo con los datos proporcionados
        instance.status_saved = validated_data.get('status_saved', instance.status_saved)
        instance.save()
        return instance

class TagUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    color = serializers.CharField(max_length=7)

    class Meta:
        model = TagModel
        fields = ['name', 'color']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.save()
        return instance