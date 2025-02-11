from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.urls import reverse
import uuid

def validate_title_length(value):
  if len(value) < 10:
    raise ValidationError('El título debe tener al menos 10 caracteres.')


# Articulos de Articulo
class ArticuloModel (models.Model):
  STATUS_CHOICES = [
    (True, 'Activo'),
    (False, 'Inactivo'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=100, validators=[validate_title_length], help_text="Título del artículo")
  slug = models.SlugField(unique=True, blank=True)
  author = models.CharField(max_length=100)
  written = models.TextField()
  status = models.BooleanField(choices=STATUS_CHOICES, default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  document = models.CharField(max_length=5000, blank=True)
  image = models.CharField(max_length=5000, blank=True)

#  Campos document y Image ; cuando se use almacenamiento habilitar

#  document = models.FileField(upload_to='documents/', blank=True, null=True)
#  image = models.ImageField(upload_to='images/', blank=True, null=True)

  class Meta:
    db_table = 'articulos'
    verbose_name = 'Artículo'
    verbose_name_plural = 'Artículos'
    ordering = ['-created_at']

  def __str__(self) -> str:
    return str(self.id)

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.title)
    super().save(*args, **kwargs)

  def get_absolute_url(self):
    return reverse('articulo-detail', kwargs={'slug': self.slug})

  def get_related_tags(self):
        """Obtiene los tags relacionados con el artículo."""
        return self.tag_details.filter(status_saved=True).select_related('tag')

# Verificador de File, de momento no usar (solo cuando se use mas campo,
# de momento usaremos links para docs e imagenes)

# class FileUpload(models.Model):
#     file = models.FileField(upload_to='uploads/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = 'Archivo Subido'
#         verbose_name_plural = 'Archivos Subidos'
#         ordering = ['-uploaded_at']

#     def __str__(self) -> str:
#         return self.file.name


# Tag/Etiquetas de los Articulos
class TagModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=20)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name

class TagDetailModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey('ArticuloModel', on_delete=models.CASCADE, related_name='tag_details')
    tag = models.ForeignKey(TagModel, on_delete=models.CASCADE, related_name='tag_details')  # related_name='tag_details'
    status_saved = models.BooleanField(default=True)

    class Meta:
        db_table = 'tags_detail'
        verbose_name = 'Detalle de Tag'
        verbose_name_plural = 'Detalles de Tags'
        unique_together = ('article', 'tag')  # Evita duplicados

    def __str__(self):
        return f"{self.article.title} - {self.tag.name}"