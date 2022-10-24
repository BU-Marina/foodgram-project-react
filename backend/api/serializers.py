import base64

# from django.contrib.auth import authenticate
# from django.db.models import Avg
# from django.shortcuts import get_object_or_404
from rest_framework import serializers
# from rest_framework.exceptions import NotFound
# from rest_framework.validators import UniqueTogetherValidator
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.tokens import AccessToken
from recipes.models import Recipe
from django.core.files.base import ContentFile

...

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка 
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')  
            # И извлечь расширение файла.
            ext = format.split('/')[-1]  
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    ...
    image = Base64ImageField(required=True)
    
    class Meta:
        model = Recipe
        fields = '__all__'
        # fields = (
        #     'id', 'name', 'text', 'cooking_time', 'tags', 'author',
        #     'image'
        # )
        # read_only_fields = ('author',)
