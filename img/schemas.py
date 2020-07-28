from app import ma
from marshmallow import ValidationError
from marshmallow.decorators import post_load
from marshmallow.fields import String, Integer, DateTime
from marshmallow.validate import Length
from models import Image


def validate_user_id(user_id):
    if user_id < 1:
        raise ValidationError(f'user_id must be > 0, got {user_id}')


class ImageSchema(ma.Schema):
    id = Integer(dump_only=True)
    user_id = Integer(validate=validate_user_id, load_only=True)
    title = String(validate=Length(min=1, max=254))
    image = String()

    uploaded_at = DateTime(dump_only=True)

    @post_load
    def create_image(self, data, **kwargs):
        data['image'] = data['image'].encode('utf-8')

        return Image(**data)

    class Meta:
        fields = ('id', 'user_id', 'title', 'image', 'uploaded_at')
