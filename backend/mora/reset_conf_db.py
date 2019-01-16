import psycopg2
#import settings


# conn = psycopg2.connect(user=settings.USER_SETTINGS_DB_USER,
#                        dbname=settings.USER_SETTINGS_DB_NAME,
#                        host=settings.USER_SETTINGS_DB_HOST,
#                        password=settings.USER_SETTINGS_DB_PASSWORD)

conn = psycopg2.connect(user='mora',
                        dbname='mora',
                        host='localhost',
                        password='mora')
conn.set_isolation_level(0)

cur = conn.cursor()

cur.execute('DELETE FROM orgunit_settings')

cur.execute("INSERT INTO orgunit_settings (object, setting, value) values (Null, 'show_roles', 'True')")
cur.execute("INSERT INTO orgunit_settings (object, setting, value) values (Null, 'show_user_key', 'True')")
cur.execute("INSERT INTO orgunit_settings (object, setting, value) values (Null, 'show_location', 'True')")
