import fileinput
import json
import os
import psycopg2

coordinate_table = """
CREATE TABLE IF NOT EXISTS coordinate (
    id SERIAL PRIMARY KEY,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
);
"""

person_table = """
CREATE TABLE IF NOT EXISTS person (
    id SERIAL PRIMARY KEY,
    firstName VARCHAR(255) DEFAULT '',
    lastName VARCHAR(255) DEFAULT ''
);
"""

location_table = """
CREATE TABLE IF NOT EXISTS location (
    id SERIAL PRIMARY KEY,
    coordinate INTEGER REFERENCES coordinate(id),
    state VARCHAR(2) NOT NULL,
    city VARCHAR(255) NOT NULL,
    zipcode VARCHAR(255) NOT NULL,
    medianHouseholdIncome REAL NOT NULL,
    population INTEGER NOT NULL
);
"""

customer_table = """
CREATE TABLE IF NOT EXISTS customer (
    id SERIAL PRIMARY KEY,
    person INTEGER REFERENCES person(id),
    location INTEGER REFERENCES location(id)
);
"""

store_table = """
CREATE TABLE IF NOT EXISTS store (
    id SERIAL PRIMARY KEY,
    location INTEGER REFERENCES location(id),
    name VARCHAR(255) NOT NULL
);
"""

transaction_table = """
CREATE TABLE IF NOT EXISTS transaction (
    id SERIAL PRIMARY KEY,
    customer INTEGER REFERENCES customer(id),
    store INTEGER REFERENCES store(id),
    time REAL NOT NULL,
    products VARCHAR(1000) NOT NULL
);
"""


def create_tables(conn):
    cur = conn.cursor()

    cur.execute(coordinate_table)
    cur.execute(person_table)
    cur.execute(location_table)
    cur.execute(customer_table)
    cur.execute(store_table)
    cur.execute(transaction_table)

    conn.commit()
    cur.close()


def insert_coordinate(cur, coordinate):
    coordinate_insert = """
    INSERT INTO coordinate(latitude, longitude) VALUES(%s, %s) RETURNING id;
    """

    cur.execute(coordinate_insert, (coordinate["first"], coordinate["second"]))

    return cur.fetchone()[0]


def insert_person(cur, person):
    person_insert = """
    INSERT INTO person(firstName, lastName) VALUES(%s, %s) RETURNING id;
    """

    cur.execute(person_insert, (person["first"], person["second"]))

    return cur.fetchone()[0]


def insert_location(cur, location):
    location_insert = """
    INSERT INTO location(coordinate, state, city, zipcode, medianHouseholdIncome, population)
        VALUES(%s, %s, %s, %s, %s, %s) RETURNING id;
    """

    coordinate = insert_coordinate(cur, location["coordinates"])
    cur.execute(
        location_insert,
        (
            coordinate,
            location["state"],
            location["city"],
            location["zipcode"],
            location["medianHouseholdIncome"],
            location["population"],
        ),
    )

    return cur.fetchone()[0]


def insert_customer(cur, customer):
    customer_insert = """
    INSERT INTO customer(person, location) VALUES(%s, %s) RETURNING id;
    """

    location = insert_location(cur, customer["location"])
    person = insert_person(cur, customer["name"])
    cur.execute(customer_insert, (person, location))

    return cur.fetchone()[0]


def insert_store(cur, store):
    store_insert = """
    INSERT INTO store(name, location) VALUES(%s, %s) RETURNING id;
    """

    location = insert_location(cur, store["location"])
    cur.execute(store_insert, (store["name"], location))

    return cur.fetchone()[0]


def insert_transaction(conn, transaction):
    transaction_insert = """
    INSERT INTO transaction(customer, store, time, products) VALUES (%s, %s, %s, %s) RETURNING id;
    """

    cur = conn.cursor()
    customer = insert_customer(cur, transaction["customer"])
    store = insert_store(cur, transaction["store"])

    products = ""
    for product_list in transaction["products"]:
        for product in product_list:
            products += product + ","
    products.rstrip(",")

    cur.execute(
        transaction_insert, (customer, store, transaction["dateTime"], products)
    )

    conn.commit()
    cur.close()


def create_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def main():
    conn = create_connection()
    create_tables(conn)

    for line in fileinput.input():
        transaction = json.loads(line)
        insert_transaction(conn, transaction)


if __name__ == "__main__":
    main()
