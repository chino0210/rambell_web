from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth import authenticate
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
import uuid
import logging

from .permissions import IsSuperUser
from django.shortcuts import get_object_or_404
from .serializers import (
    ArticuloSerializer, ArticuloUpdateSerializer, ArticuloProfileSerializer, TagDetailSerializer,
    TagSerializer, TagCreateSerializer, TagDetailUpdateSerializer, TagUpdateSerializer
)
from .models import ArticuloModel, TagModel, TagDetailModel
from .filters import ArticuloFilter

logger = logging.getLogger(__name__)


# Vistas para Artículos
class ArticuloView(generics.ListAPIView):
  queryset = ArticuloModel.objects.all().prefetch_related('tag_details__tag')
  serializer_class = ArticuloSerializer
  filter_backends = [DjangoFilterBackend]
  filterset_class = ArticuloFilter
  ordering_fields = ['title', 'author', 'created_at']


@permission_classes([IsSuperUser])
class ArticuloCreateView(generics.CreateAPIView):
  queryset = ArticuloModel.objects.all()
  serializer_class = ArticuloSerializer

  def perform_create(self, serializer):
    serializer.save(author=self.request.user)
    # Asignar el usuario autenticado como autor


@permission_classes([IsSuperUser])
class ArticuloUpdateView(generics.UpdateAPIView):
  queryset = ArticuloModel.objects.all()
  serializer_class = ArticuloUpdateSerializer

  def update(self, request, *args, **kwargs):
    try:
      instance = self.get_object()
      serializer = self.get_serializer(instance, data=request.data, partial=True)
      serializer.is_valid(raise_exception=True)
      self.perform_update(serializer)
      return Response(serializer.data, status=status.HTTP_200_OK)
    except ValidationError as e:
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      logger.error(f"Error actualizando articulo: {e}")
      return Response({"error": "Ocurrió un error inesperado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@permission_classes([IsSuperUser])
class ArticuloDeleteView(generics.DestroyAPIView):
  queryset = ArticuloModel.objects.all()
  serializer_class = ArticuloSerializer

  def destroy(self, request, *args, **kwargs):
    try:
      instance = self.get_object()
      instance.status = False
      instance.save()
      return Response({"message": "Articulo desactivado correctamente"}, status=status.HTTP_200_OK)
    except NotFound:
      return Response({"error": "Articulo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      logger.error(f"Error desactivando el articulo: {e}")
      return Response({"error": "Ocurrió un error inesperado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArticuloFilterID(generics.RetrieveAPIView):
  queryset = ArticuloModel.objects.all()
  serializer_class = ArticuloSerializer


# Vistas para Tags
class TagView(generics.ListAPIView):
  queryset = TagModel.objects.all()
  serializer_class = TagSerializer


@permission_classes([IsSuperUser])
class TagCreateView(generics.CreateAPIView):
  queryset = TagModel.objects.all()
  serializer_class = TagCreateSerializer

  @transaction.atomic
  def create(self, request, *args, **kwargs):
    try:
      serializer = self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)

      name = serializer.validated_data.get('name')
      if TagModel.objects.filter(name=name).exists():
        return Response({"error": "Tag existente"}, status=status.HTTP_400_BAD_REQUEST)

      serializer.save()
      return Response({"message": "Tag creado correctamente"}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      logger.error(f"Error al crear el tag: {e}")
      return Response({"error": "Ocurrió un error inesperado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@permission_classes([IsSuperUser])
class TagDetailUpdateView(generics.UpdateAPIView):
    serializer_class = TagDetailUpdateSerializer
    queryset = TagDetailModel.objects.all()

    def get_object(self):
        article_id = self.kwargs['article_id']
        tag_id = self.kwargs['tag_id']

        # Intentamos obtener el detalle del artículo para un tag dado
        try:
            return TagDetailModel.objects.get(tag_id=tag_id, article_id=article_id)
        except TagDetailModel.DoesNotExist:
            # Si no existe, lo creamos
            tag = TagModel.objects.get(id=tag_id)  # Asumimos que el tag existe
            # Creamos un nuevo detalle con el artículo y el tag
            return TagDetailModel.objects.create(tag=tag, article_id=article_id, status_saved=False)

    def patch(self, request, *args, **kwargs):
        # Llamamos a la actualización del objeto, esto creará o actualizará
        return self.update(request, *args, **kwargs)

class TagUpdateView(generics.UpdateAPIView):
    queryset = TagModel.objects.all()
    serializer_class = TagUpdateSerializer


@permission_classes([IsSuperUser])
class TagDeleteView(generics.DestroyAPIView):
  queryset = TagModel.objects.all()
  serializer_class = TagSerializer

  def destroy(self, request, *args, **kwargs):
    try:
      instance = self.get_object()
      instance.status = False
      instance.save()
      return Response({"message": "Tag desactivado correctamente"}, status=status.HTTP_200_OK)
    except NotFound:
      return Response({"error": "Tag no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      logger.error(f"Error desactivando el tag: {e}")
      return Response({"error": "Ocurrió un error inesperado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vista de Login
class LoginView(APIView):
  def post(self, request):
    logger.debug(f"Request data: {request.data}")

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user is not None and user.is_superuser:
      refresh = RefreshToken.for_user(user)
      return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
      })
    return Response({"detail": "No autorizado"}, status=status.HTTP_401_UNAUTHORIZED)