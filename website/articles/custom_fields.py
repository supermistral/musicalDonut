from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files import File
from io import BytesIO
from PIL import Image, ImageOps
import os


class CompressedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        image = Image.open(content).convert('RGB')
        image = ImageOps.exif_transpose(image)
        image_io = BytesIO()

        image.save(image_io, "JPEG", optimize=True, quality=self.field.quality)

        image_filename = f"{os.path.splitext(name)[0]}.jpeg"
        image_file = File(image_io, name=image_filename)

        return super().save(image_filename, image_file, save)

    
class CompressedImageField(ImageField):
    attr_class = CompressedImageFieldFile

    def __init__(self, verbose_name=None, name=None, width_field=None, 
                 height_field=None, quality=85, **kwargs):
        self.quality = quality
        super().__init__(verbose_name, name, width_field, height_field, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.quality:
            kwargs['quality'] = self.quality
        
        return name, path, args, kwargs