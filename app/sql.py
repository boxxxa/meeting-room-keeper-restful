# native SQL statements execution module
from app import app, db
from app.console_log import console_log, sql_log
import re
import sqlalchemy.exc

def runSQL(statement):

    try:
        # log statement
        sql_log(statement, 'note')

        # execute SQL statement
        result = db.engine.execute(statement)

        # SELECT statement handling
        if re.search(r"^\s*SELECT", statement, re.I):
            # transforn result to array of rows
            rows = [dict(row) for row in result.fetchall()]
            sql_log('Selected {} rows'.format(len(rows)), 'info')

            return rows

        # INSERT statement handling
        elif re.search(r"^\s*INSERT", statement, re.I):
            sql_log('Inserted ID: {}'.format(result.lastrowid), 'info')
            return result.lastrowid

        # DELETE statement handling
        elif re.search(r"^\s*DELETE", statement, re.I):
            sql_log('Deleted {} rows'.format(result.rowcount), 'info')
            return result.rowcount

        # UPDATE statement handling
        elif re.search(r"^\s*UPDATE", statement, re.I):
            sql_log('Updated {} rows'.format(result.rowcount), 'info')
            return result.rowcount

    # if constraint violated, return None
    except sqlalchemy.exc.IntegrityError as err:
        console_log('Integrity Error - ' + str(err.orig), 'fail')
        return None


