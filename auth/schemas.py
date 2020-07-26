from auth import models
from auth.app import ma
from marshmallow import fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Length, Equal


class UserSchema(ma.Schema):
    email = fields.Email(required=True, validate=Length(min=3, max=254))
    password = fields.Str(load_only=True, required=True, validate=Length(min=4))
    confirm_password = fields.Str(load_only=True, required=True)
    joined_at = fields.DateTime(dump_only=True)

    @validates_schema
    def ensure_equal_to_password(self, data, **kwargs):
        errors = {}

        if data['password'] != data['confirm_password']:
            errors["confirm_password"] = ['Confirm password did not match password!']
            raise ValidationError(errors)
        else:
            data.pop('confirm_password', None)

    @post_load
    def create_user(self, data, **kwargs):
        return models.User(**data)

    class Meta:
        fields = ('email', 'password', "confirm_password", 'joined_at')
