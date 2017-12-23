from flask_restful import fields, reqparse
import datetime

# define Items output fields
item_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'start_date': fields.String,
    'end_date': fields.String,
    'user': {
        'id': fields.Integer(attribute='user_id'),
        'name': fields.String(attribute='user_name')
    },
    'place': {
        'id': fields.Integer(attribute='place_id'),
        'name': fields.String(attribute='place_name')
    },
    'item_type': {
        'id': fields.Integer(attribute='itemtype_id'),
        'name': fields.String(attribute='itemtype_name')
    }

}

# define Places output fields
place_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}

def utc_from_str(value):
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')

    try:
        d = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
        return d
    except ValueError as err:
        print('error')
        raise ValueError("The parameter '{0}' is not ISO8601 datetime".format(value))

# parser definition for Item POST request
item_post_parser = reqparse.RequestParser()
item_post_parser.add_argument('name', type=str, required=True)
item_post_parser.add_argument('description', type=str, required=True)
item_post_parser.add_argument('start_date', type=utc_from_str, required=True)
item_post_parser.add_argument('end_date', type=utc_from_str, required=True)
item_post_parser.add_argument('user_id', type=int, required=True)
item_post_parser.add_argument('place_id', type=int, required=True)
item_post_parser.add_argument('item_type', type=int, required=True)
