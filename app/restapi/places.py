# Places RESTful endpoints
from flask_restful import Resource, marshal_with
from app.sql import runSQL
from app.google_calendar import gc_sync_db, gc_synced
from app import app
from app.models import place_fields, item_fields


class Places(Resource):
    # format response as defined in place_fields
    @marshal_with(place_fields, envelope='places')
    # GET method
    def get(self,  place_id=None):
        if place_id:
            return runSQL('''
                SELECT *
                FROM places
                WHERE id={};
                '''.format(place_id)), 200 # HTTP status code 200 OK
        else:
            return runSQL('''
                SELECT *
                FROM places;
                '''), 200

    def post(self, id=None):
        return {'places': 'Add new place'}

    # PUT method
    def put(self, id=None):
        if id:
            return {'places': 'update place id={}'.format(id)}, 200
        else:
            return {'places': 'Update failed'}, 400 # Bad Request


    def delete(self, id=None):
        if id:
            return {'places': 'delete place id={}'.format(id)}, 200
        else:
            return {'places': 'delete all places'}, 200


class PlacesItems(Resource):
    # format response as defined in place_fields
    @marshal_with(item_fields, envelope='items')
    # GET method
    def get(self, place_id, start_datetime=None, end_datetime=None):
        if end_datetime:
            #gc_sync_db(place_id, start_date, end_date)
            return runSQL('''
                SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
                FROM items, users, places, item_type
                WHERE items.user_id = users.id
                    AND items.place_id = places.id
                    AND items.itemtype_id = item_type.id
                    AND place_id = {place_id}
                    AND ((datetime(start_date) < datetime('{start_date}') AND datetime('{start_date}') < datetime(end_date))
                        OR (datetime('{start_date}') <= datetime(start_date) AND datetime(end_date) <= datetime('{end_date}'))
                        OR (datetime(start_date) < datetime('{end_date}') AND datetime('{end_date}') < datetime(end_date)))
                ORDER BY start_date;
                '''.format(place_id=place_id, start_date=start_datetime, end_date=end_datetime, fields=app.config['SQL_DEFAULT_FIELDS'])), 200
        elif start_datetime:
            #gc_sync_db(place_id, start_date)
            return runSQL('''
                SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
                FROM items, users, places, item_type
                WHERE items.user_id = users.id
                    AND items.place_id = places.id
                    AND items.itemtype_id = item_type.id
                    AND place_id = {place_id}
                    AND ((datetime(start_date) < datetime('{start_date}') AND datetime('{start_date}') < datetime(end_date))
                        OR (datetime('{start_date}') <= datetime(start_date) AND datetime(end_date) <= datetime(datetime('{start_date}'),'+24 hours'))
                        OR (datetime(start_date) < datetime(datetime('{start_date}'),'+24 hours') AND datetime(datetime('{start_date}'),'+24 hours') < datetime(end_date)))
                ORDER BY start_date;
                '''.format(place_id=place_id, start_date=start_datetime, fields=app.config['SQL_DEFAULT_FIELDS'])), 200

        else:
            return runSQL('''
                SELECT {fields}, users.name || ' ' || users.surname as user_name, places.name as place_name, item_type.name as itemtype_name
                FROM items, users, places, item_type
                WHERE items.user_id = users.id
                    AND items.place_id = places.id
                    AND items.itemtype_id = item_type.id
                    AND place_id = {place_id}
                ORDER BY start_date;
                '''.format(place_id=place_id, fields=app.config['SQL_DEFAULT_FIELDS'])), 200 # HTTP status code 200 OK


class PlacesItemsNow(Resource):
    def get(self, place_id):
        # if not gc_synced():
        #     gc_sync_db()
        # ongoing event
        a = runSQL('''
            SELECT {fields}
            FROM items
            WHERE place_id={place_id}
                AND itemtype_id=1
                AND datetime(start_date) <= datetime('now')
                AND datetime('now') <= datetime(end_date)
                ORDER BY id_remote DESC, start_date
                LIMIT 1;
                '''.format(place_id=place_id, fields=app.config['SQL_DEFAULT_FIELDS']))

        # upcoming event
        b = runSQL('''
            SELECT {fields}
            FROM items
            WHERE place_id={place_id}
            AND itemtype_id=1
            AND datetime(start_date) > datetime('now')
            AND date(start_date) = date('now')
            ORDER BY id_remote DESC, start_date
            LIMIT 1;
                '''.format(place_id=place_id, fields=app.config['SQL_DEFAULT_FIELDS']))

        c = []
        #if a or b:
        c.append(a)
        c.append(b)

        return c, 200



