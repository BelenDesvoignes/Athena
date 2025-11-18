from marshmallow import Schema, fields, validate


class Review_Create_Schema(Schema):
    rating = fields.Integer(required=True , validate=validate.Range(min=1, max=5))
    site_id = fields.Integer(required=True)
    comment = fields.String(required=False, validate=validate.Length(min= 20, max=1000))

class Review_Schema(Schema):
    id = fields.Int(dump_only=True)
    site_id = fields.Int()
    user_id = fields.Int()
    rating = fields.Int()
    comment = fields.Str()
    status = fields.Str()
    rejection_reason = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()