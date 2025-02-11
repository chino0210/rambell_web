import django_filters
from .models import ArticuloModel, TagModel, TagDetailModel

class ArticuloFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Título")
    author = django_filters.CharFilter(lookup_expr='icontains', label="Autor")
    tags = django_filters.CharFilter(method='filter_by_tags', label="Tags")

    class Meta:
        model = ArticuloModel
        fields = ['title', 'author', 'tags']

    def filter_by_tags(self, queryset, name, value):
        # Divide los tags por comas y elimina espacios en blanco
        tag_names = [tag.strip() for tag in value.split(',')]
        # Filtra los tags por nombre
        tags = TagModel.objects.filter(name__in=tag_names)
        # Obtiene los artículos que tienen esos tags
        articulo_ids = TagDetailModel.objects.filter(tag__in=tags).values_list('article_id', flat=True)
        # Retorna los artículos que coinciden con los tags
        return queryset.filter(id__in=articulo_ids)