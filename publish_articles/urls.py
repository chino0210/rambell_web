from django.urls import path
from .views import (
    ArticuloView, ArticuloCreateView, ArticuloUpdateView, ArticuloDeleteView,
    TagView, TagCreateView, TagDetailUpdateView, TagDeleteView, TagUpdateView,
    ArticuloFilterID, LoginView,
)

urlpatterns = [
    # Rutas para Artículos
    path('articulos/', ArticuloView.as_view(), name='articulo_list'),  # Listar todos los artículos
    path('articulos/crear/', ArticuloCreateView.as_view(), name='articulo_create'),  # Crear un artículo
    path('articulos/actualizar/<uuid:pk>/', ArticuloUpdateView.as_view(), name='articulo_update'),  # Actualizar un artículo
    path('articulos/eliminar/<uuid:pk>/', ArticuloDeleteView.as_view(), name='articulo_delete'),  # Eliminar (desactivar) un artículo
    path('articulos/<uuid:pk>/', ArticuloFilterID.as_view(), name='articulo_detail'),  # Detalle de un artículo

    # Rutas para Tags
    path('tags/', TagView.as_view(), name='tag_list'),  # Listar todos los tags
    path('tags/crear/', TagCreateView.as_view(), name='tag_create'),  # Crear un tag
    path('tags/<uuid:pk>/', TagUpdateView.as_view(), name='update_tag'),
    path('tags/<uuid:tag_id>/details/<uuid:article_id>/', TagDetailUpdateView.as_view(), name='update_tag_detail'),  # Actualizar un tag
    path('tags/eliminar/<uuid:pk>/', TagDeleteView.as_view(), name='tag_delete'),  # Eliminar (desactivar) un tag

    # Ruta para Login
    path('login/', LoginView.as_view(), name='login'),  # Iniciar sesión
]