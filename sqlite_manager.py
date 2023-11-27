import sqlite3 as sql

# TODO select功能 多条件查询

con = sql.connect('test.db')
cur = con.cursor()

class select:
    def __init__(self, table, column, condition):
        self.table = table
        self.column = column
        self.condition = condition

    def select(self):
        if self.condition == None:
            cur.execute('SELECT %s FROM %s' % (self.column, self.table))
        else:
            cur.execute('SELECT %s FROM %s WHERE %s' % (self.column, self.table, self.condition))
        data = cur.fetchall()
        return data


class DB_manager:

    operate_num = 0

    def __init__(self, db_name):
        try:
            self.con = sql.connect(db_name)
            self.cur = con.cursor()
        except Exception as e:
            print('Error: DB connection failed:%s' % e)


    # def create_table(self):
    #     self.cur.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)')
    #     self.con.commit()

    def insert_data(self, args: tuple):
        try:
            self.cur.execute('INSERT INTO test VALUES %s'% str(args))
        except Exception as e:
            print('Error: DB insert failed:%s' % e)


    def fetch_data(self):
        self.cur.execute('SELECT * FROM test')
        data = self.cur.fetchall()
        return data

    def remove_data(self, id):
        self.cur.execute('DELETE FROM test WHERE id=?', (id,))


    def update_data(self, id, name, age):
        self.cur.execute('UPDATE test SET name=?, age=? WHERE id=?', (name, age, id))

    def commit(self):
        self.con.commit()

    def rollback(self):
        self.con.rollback()

    def __del__(self):
        self.con.close()

