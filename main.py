import psycopg2

def create_db(conn):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client(
        client_id SERIAL PRIMARY KEY,
        name VARCHAR(40), 
        surname VARCHAR(40),
        email VARCHAR(40) UNIQUE
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS telephone(
        tele_id SERIAL PRIMARY KEY,
        client_id INTEGER REFERENCES client(client_id),
        number VARCHAR(12) UNIQUE
    );
    """)
    conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    cur.execute("""
    INSERT INTO client(name, surname, email) VALUES(%s, %s, %s) RETURNING client_id;
    """, (first_name, last_name, email))
    print(cur.fetchone())

    if phones != None:
        cur.execute("""
        SELECT client_id FROM client
        WHERE email = %s;
        """, (email, ))
        id = cur.fetchone()

        cur.execute("""
        INSERT INTO telephone(client_id, number) VALUES(%s, %s);
        """, (id, phones))
        conn.commit()  # фиксируем в БД

def add_phone(conn, client_id, phone):
    cur.execute("""
    INSERT INTO telephone(client_id, number) VALUES(%s, %s) RETURNING tele_id;
    """, (client_id, phone))
    print(cur.fetchone())

def change_client(conn, id, first_name=None, last_name=None, email=None, phones=None):
    if first_name != None:
        cur.execute("""
        UPDATE client SET  name=%s WHERE client_id = %s RETURNING client_id;
        """, (first_name, id))
        print(cur.fetchone())

    if last_name != None:
        cur.execute("""
        UPDATE client SET surname=%s WHERE client_id = %s  RETURNING client_id;
        """, (last_name, id))
        print(cur.fetchone())

    if email != None:
        cur.execute("""
        UPDATE client SET email=%s WHERE client_id = %s  RETURNING client_id;
        """, (email, id))
        print(cur.fetchone())

    if phones != None:
        cur.execute("""
        UPDATE telephone SET number=%s WHERE client_id = %s AND number = %s  RETURNING tele_id;
        """, (phones[1], id, phones[0]))
        print(cur.fetchone())

def delete_phone(conn, client_id, phone):
    cur.execute("""
    DELETE FROM telephone WHERE client_id = %s AND number = %s;
    """, (client_id, phone))
    conn.commit()
    print(f'Delete phone {phone} completed')

def delete_client(conn, client_id):
    cur.execute("""
    DELETE FROM client WHERE client_id = %s;
    """, (client_id, ))
    conn.commit()
    print(f'Delete client {client_id} completed')

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    if first_name != None:
        cur.execute("""
        SELECT client.surname, client.email, telephone.number FROM client
        JOIN telephone ON telephone.client_id = client.client_id
        WHERE client.name = %s
        """, (first_name, ))
        print(f'by name: {cur.fetchone()}')

    if last_name != None:
        cur.execute("""
        SELECT client.name, client.email, telephone.number FROM client 
        JOIN telephone ON telephone.client_id = client.client_id
        WHERE client.surname = %s
        """, (last_name, ))
        print(f'by lastname: {cur.fetchone()}')

    if email != None:
        cur.execute("""
        SELECT client.name, client.surname, telephone.number FROM client
        JOIN telephone ON telephone.client_id = client.client_id
        WHERE email = %s
        """, (email, ))
        print(f'by email: {cur.fetchone()}')

    if phone != None:
        cur.execute("""
        SELECT name, surname, email FROM client
        WHERE client_id = (SELECT client_id FROM telephone WHERE number=%s);
        """, (phone, ))
        print(f'by telephone: {cur.fetchone()}')


with psycopg2.connect(database="clients_db", user="postgres", password="387987") as conn:
    with conn.cursor() as cur:
        create_db(conn)
        add_client(conn, 'John', 'Sergeev', 'm1@mg.com', '+79990000005')
        add_client(conn, 'Vlad', 'Petrov', 'm77@mg.com')
        add_phone(conn, 11, '+79990000006') # 11 - номер John на момент тестирования
        change_client(conn, 11, first_name='Mike', last_name='Ivanov', email='m4@mg.com', phones=['+79990000006', '+79990000666'])
        delete_phone(conn, 5, '+79990000666')
        delete_client(conn, 12)
        find_client(conn, 'Mike', 'Ivanov', 'm4@mg.com', '+79990000666')

conn.close()
