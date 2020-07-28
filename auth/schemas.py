from models import User
from app import ma
from marshmallow import fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Length, Equal


class ProfileSchema(ma.Schema):
    first_name = fields.Str(validate=Length(min=1, max=50))
    last_name = fields.Str(validate=Length(min=1, max=50))


class UserSchema(ma.Schema):
    email = fields.Email(required=True, validate=Length(min=3, max=254))
    password = fields.Str(load_only=True, required=True, validate=Length(min=4))
    confirm_password = fields.Str(load_only=True, required=True)
    joined_at = fields.DateTime(dump_only=True)

    profile = fields.Nested(ProfileSchema, dump_only=True)

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
        return User(**data)

    class Meta:
        fields = ('id', 'email', 'profile', 'password', 'confirm_password', 'joined_at')


class LoginSchema(ma.Schema):
    email = fields.Email(required=True, validate=Length(min=3, max=254))
    password = fields.Str(required=True, validate=Length(min=4))
