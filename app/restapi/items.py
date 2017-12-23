# Items RESTful endpoints
from flask_restful import Resource, marshal_with
from app.sql import runSQL
from app import app
from app.models import item_fields, item_post_parser


class Items(Resource):
    # format response as defined in place_fields
    @marshal_with(item_fields, envelope='items')
    # GET method
    def get(self, id=None, start_date=None, end_date=None):
        if id:
            return runSQL('''
                SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
                FROM items, users, places, item_type
                WHERE items.user_id = users.id
                    AND items.place_id = places.id
                    AND items.itemtype_id = item_type.id
                    AND items.id={id}
                ORDER BY start_date, place_id;
                '''.format(id=id, fields=app.config['SQL_DEFAULT_FIELDS'])), 200 # HTTP status code 200 OK

        elif start_date:
            return runSQL('''
                SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
                FROM items, users, places, item_type
                WHERE items.user_id = users.id
                    AND items.place_id = places.id
                    AND items.itemtype_id = item_type.id
                    AND date(start_date) >= '{start_date}'
                    AND date(end_date) <= '{end_date}'
                ORDER BY start_date, place_id;
                '''.format(start_date=start_date, end_date=end_date or start_date, fields=app.config['SQL_DEFAULT_FIELDS'])), 200
        else:
            return runSQL('''
                SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
                FROM items, users, places, item_type
                WHERE items.user_id = users.id
                    AND items.place_id = places.id
                    AND items.itemtype_id = item_type.id
                ORDER BY start_date, place_id;
                '''.format(fields=app.config['SQL_DEFAULT_FIELDS'])), 200

    #@marshal_with(item_fields, envelope='item')
    # POST method
    def post(self, id=None):
        item = item_post_parser.parse_args()
        start_date = item['start_date'].strftime('%Y-%m-%d %H:%M:%S')
        end_date = item['end_date'].strftime('%Y-%m-%d %H:%M:%S')

        # items overlaping check
        overlap = runSQL('''
            SELECT * FROM items
            WHERE place_id = {place_id}
                AND (((start_date <= '{start_date}' AND '{start_date}' < end_date) OR (start_date < '{end_date}' AND '{end_date}' <= end_date))
                    OR ('{start_date}' < start_date AND end_date < '{end_date}'));
            '''.format(start_date=start_date, end_date=end_date, place_id=item['place_id']))
        if overlap and item['item_type'] == 1:
            return {'message': 'Insert failed. Item overlaps existing items'}, 409 # Conflict

        # proceed with insert
        item_id = runSQL('''
                INSERT INTO items (name, description, start_date, end_date, user_id, place_id, itemtype_id)
                VALUES ('{name}','{description}','{start_date}','{end_date}', {user_id}, {place_id}, {item_type});
                '''.format(name=item['name'], description=item['description'], start_date=start_date, end_date=end_date,
                user_id=item['user_id'], place_id=item['place_id'], item_type=item['item_type']))

        # return runSQL('''
        #     SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
        #     FROM items, users, places, item_type
        #     WHERE items.user_id = users.id
        #         AND items.place_id = places.id
        #         AND items.itemtype_id = item_type.id
        #         AND items.id = {item_id};
        #     '''.format(fields=app.config['SQL_DEFAULT_FIELDS'], item_id=item_id)), 201 # Created
        return {'message': 'item id={id} has been created'.format(id=item_id)}, 201 # Created


    # PUT method
    def put(self, id=None):
        if id:
            return {'message': 'update item id={}'.format(id)}, 200
        else:
            return {'message': 'Update failed. Missed ID'}, 400 # Bad Request

    # DELETE method
    def delete(self, id=None):
        if id:
            if runSQL('''
                DELETE FROM items where id = {id};
                '''.format(id=id)):
                return {'message': 'item id={} has been deleted'.format(id)}, 200
            else:
                return {'message': 'item id={} not found'.format(id)}, 404
        else:
            return {'message': 'fake delete all items'}, 200


class ItemsNow(Resource):
    # format response as defined in place_fields
    @marshal_with(item_fields, envelope='items')
    # GET method
    def get(self):
        return runSQL('''
            SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
            FROM items, users, places, item_type
            WHERE items.user_id = users.id
                AND items.place_id = places.id
                AND items.itemtype_id = item_type.id
                AND start_date <= datetime('now')
                AND datetime('now') <= end_date
            ORDER BY start_date, place_id;
            '''.format(fields=app.config['SQL_DEFAULT_FIELDS'])), 200 # HTTP status code 200 OK
