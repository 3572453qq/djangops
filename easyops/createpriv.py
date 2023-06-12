from models import pagepermission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(pagepermission)
permission = Permission.objects.create(
    codename='hrsqldg ',
    name='Can execute sql in hr proddg',
    content_type=content_type,
)
