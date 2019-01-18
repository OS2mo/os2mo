import sqlite3

defaults = {'show_roles': 'True',
            'show_user_key': 'True',
            'show_locaion': 'True'}

conn = sqlite3.connect('/tmp/usersettings.db')
cur = conn.cursor()

#for row in cur.execute('select * from orgunit_settings;'):
#    print(row)

#1/0

create_query = ('CREATE TABLE orgunit_settings(id INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                'object UUID, setting varchar(255) NOT NULL, '
                'value varchar(255) NOT NULL);')
cur.execute(create_query)

query = ('INSERT INTO orgunit_settings (object, setting, value) values ' +
         '(Null, "{}", "{}");')

for setting, value in defaults.items():
    cur.execute(query.format(setting, value))
    conn.commit()
