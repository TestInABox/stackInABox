"""
Stack-In-A-Box: Keystone Backend
"""
import random
import sqlite3
import uuid

"""
    - Build a service catalog
    - Add users
    - Add services
    - Add roles
    - Authentication

    PSOT /v2.0/users


    POST /v2.0/tokens/
    DELETE /v2.0/tokens/{token}
    GET /v2.0/tentants{?name}
"""

schema = [
'''
    CREATE TABLE keystone_tenants
    (
        tenantid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        enabled INTEGER DEFAULT 1
    )
''',
'''
    CREATE TABLE keystone_users
    (
        tenantid INTEGER NOT NULL REFERENCES keystone_tenants(tenantid),
        userid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        enabled INTEGER DEFAULT 1
    )
'''
]

SQL_ADD_TENANT = '''
    INSERT INTO keystone_tenants
    (name, description, enabled)
    VALUES(:name, :description, :enabled)
'''

SQL_GET_MAX_TENANT_ID = '''
    SELECT MAX(tenantid)
    FROM keystone_tenants
'''

SQL_GET_TENANT_BY_ID = '''
    SELECT tenantid, name, description, enabled
    FROM keystone_tenants
    WHERE tenantid = :tenantid
'''

SQL_GET_ALL_TENANTS = '''
    SELECT tenantid, name, description, enabled
    FROM keystone_tenants
'''

SQL_GET_TENANT_BY_NAME = '''
    SELECT tenantid, name, description, enabled
    FROM keystone_tenants
    WHERE name = :tenantname
'''

SQL_UPDATE_TENANT_DESCRIPTION = '''
    INSERT INTO keystone_tenants
    (description)
    VALUES(:description)
    WHERE tenantid = :tenantid
'''

SQL_UPDATE_TENANT_STATUS = '''
    INSERT INTO keystone_tenants
    (enabled)
    VALUES(:enabled)
    WHERE tenantid = :tenantid
'''

SQL_ADD_USER = '''
    INSERT INTO keystone_users
    (tenantid, username, email, password, enabled)
    VALUES (:tenantid, :username, :email, :password, :enabled)
'''

SQL_GET_MAX_USER_ID = '''
    SELECT MAX(userid)
    FROM keystone_users
'''

SQL_GET_USER_BY_USERNAME = '''
    SELECT tenantid, userid, username, email, password, enabled
    FROM keystone_users
    WHERE tenantid = :tenantid AND
          username = :username 
'''

SQL_GET_USER_BY_USERID = '''
    SELECT tenantid, userid, username, email, password, enabled
    FROM keystone_users
    WHERE tenantid = :tenantid AND
          userid = :userid
'''


class KeystoneBackend(object):

    def __init__(self):
        self.__admin_token = 'adminstrate_with_this_{0}'.format(uuid.uuid4()) 
        self.database = sqlite3.connect(':memory:')
        self.init_database()

    @staticmethod
    def make_token():
        return uuid.uuid4()

    @staticmethod
    def bool_from_database(value):
        if value:
            return True
        return False

    @staticmethod
    def bool_to_database(value):
        if value:
            return 1
        return 0

    def init_database(self):
        dbcursor = self.database.cursor()
        for table_sql in schema:
            dbcursor.execute(table_sql)
        self.database.commit()

    def get_admin_token(self):
        return self.__admin_token 

    def add_tenant(self, tenantname=None, description=None, enabled=True):
        args = {
            'name': tenantname,
            'description': description,
            'enabled': KeystoneBackend.bool_to_database(enabled)
        }
        dbcursor = self.database.cursor()
        dbcursor.execute(SQL_ADD_TENANT, args)
        self.database.commit()

        dbcursor.execute(SQL_GET_MAX_TENANT_ID)
        tenantid = dbcursor.fetchone()[0]
        return tenantid

    def get_tenants(self):
        dbcursor = self.database.cursor()
        tenant_list = []
        for row in dbcursor.execute(SQL_GET_ALL_TENANTS):
            tenant_list.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'enabled': KeystoneBackend.bool_from_database(row[3])
            })
        return tenant_list

    def get_tenant_by_id(self, tenantid=None):
        dbcursor = self.database.cursor()
        args = {
            'tenantid': tenantid
        }
        dbcursor.execute(SQL_GET_TENANT_BY_ID, args)
        tenant_data = dbcursor.fetchone()
        return {
            'id': tenant_data[0],
            'name': tenant_data[1],
            'description': tenant_data[2],
            'enabled': KeystoneBackend.bool_from_database(tenant_data[3])
        }

    def get_tenant_by_name(self, tenantname=None):
        dbcursor = self.database.cursor()
        args = {
            'tenantname': tenantname
        }
        dbcursor.execute(SQL_GET_TENANT_BY_NAME, args)
        tenant_data = dbcursor.fetchone()
        return {
            'id': tenant_data[0],
            'name': tenant_data[1],
            'description': tenant_data[2],
            'enabled': KeystoneBackend.bool_from_database(tenant_data[3])
        }

    def update_tenant_description(self, tenantid=None, description=None):
        dbcursor = self.database.cursor()
        args = {
            'tenantid': tenantid,
            'description': description
        }
        dbcursor.execute(SQL_UPDATE_TENANT_DESCRIPTION, args)
        self.database.commit()

    def update_tenant_status(self, tenantid=None, enabled=None):
        dbcursor = self.database.cursor()
        args = {
            'tenantid': tenantid,
            'enabled': KeystoneBackend.bool_to_database(enabled)
        }
        dbcursor.execute(SQL_UPDATE_TENANT_STATUS, args)
        self.database.commit()

    def add_user(self, tenantid=None, username=None, email=None, password=None, enabled=True):
        args = {
            'tenantid': tenantid,
            'username': username,
            'email': email,
            'password': password,
            'enabled': KeystoneBackend.bool_to_database(enabled)
        }
        dbcursor = self.database.cursor()
        dbcursor.execute(SQL_ADD_USER, args)
        self.database.commit()

        dbcursor.execute(SQL_GET_MAX_USER_ID)
        userid = dbcursor.fetchone()[0]
        return userid

    def get_user_by_id(self, tenantid=None, userid=None):
        dbcursor = self.database.cursor()
        args = {
            'tenantid': tenantid,
            'userid': userid
        }
        dbcursor.execute(SQL_GET_USER_BY_USERID, args)
        user_data = dbcursor.fetchone()
        return {
            'tenantid': user_data[0],
            'userid': user_data[1],
            'username': user_data[2],
            'email': user_data[3],
            'password': user_data[4],
            'enabled': KeystoneBackend.bool_from_database(user_data[5])
        }

    def get_user_by_name(self, tenantid=None, username=None):
        dbcursor = self.database.cursor()
        args = {
            'tenantid': tenantid,
            'username': username
        }
        dbcursor.execute(SQL_GET_USER_BY_USERNAME, args)
        user_data = dbcursor.fetchone()
        return {
            'tenantid': user_data[0],
            'userid': user_data[1],
            'username': user_data[2],
            'email': user_data[3],
            'password': user_data[4],
            'enabled': KeystoneBackend.bool_from_database(user_data[5])
        }
