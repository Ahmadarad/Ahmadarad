import sqlite3

def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect("fabrics.db")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    """
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS fabrics (
                id integer PRIMARY KEY,
                name text NOT NULL,
                color text
            );
        """)
    except sqlite3.Error as e:
        print(e)

def add_fabric(conn, fabric):
    """
    Create a new fabric into the fabrics table
    :param conn:
    :param fabric:
    :return: fabric id
    """
    sql = ''' INSERT INTO fabrics(name,color)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, fabric)
    conn.commit()
    return cur.lastrowid

def get_all_fabrics(conn):
    """
    Query all rows in the fabrics table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM fabrics")
    rows = cur.fetchall()
    return rows

def main():
    conn = create_connection()
    if conn is not None:
        create_table(conn)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
