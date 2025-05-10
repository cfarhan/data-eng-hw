# this program loads Census ACS data using basic, slow INSERTs 
# run it with -h to see the command line options

import time
import psycopg2
import argparse
import re
import csv

DBname = "postgres"
DBuser = "postgres"
DBpwd = "password"   # insert your postgres db password here
TableName = 'censusdata'
Datafile = "filedoesnotexist"  # name of the data file to be loaded
CreateDB = False  # indicates whether the DB table should be (re)-created

def initialize():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", required=True)
    parser.add_argument("-c", "--createtable", action="store_true")
    args = parser.parse_args()

    global Datafile
    Datafile = args.datafile
    global CreateDB
    CreateDB = args.createtable


# read the input data file into a list of row strings
def readdata(fname):
    print(f"readdata: reading from File: {fname}")
    with open(fname, mode="r") as fil:
        dr = csv.DictReader(fil)

        rowlist = []
        for row in dr:
            rowlist.append(row)

    return rowlist


# connect to the database
def dbconnect():
    connection = psycopg2.connect(
        host="localhost",
        database=DBname,
        user=DBuser,
        password=DBpwd,
    )
    connection.autocommit = True
    return connection


# create the target table without primary key and index initially
def createTable(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
                DROP TABLE IF EXISTS {TableName};
                CREATE TABLE {TableName} (
                        TractId             NUMERIC,
                        State               TEXT,
                        County              TEXT,
                        TotalPop            INTEGER,
                        Men                 INTEGER,
                        Women               INTEGER,
                        Hispanic            DECIMAL,
                        White               DECIMAL,
                        Black               DECIMAL,
                        Native              DECIMAL,
                        Asian               DECIMAL,
                        Pacific             DECIMAL,
                        VotingAgeCitizen    DECIMAL,
                        Income              DECIMAL,
                        IncomeErr           DECIMAL,
                        IncomePerCap        DECIMAL,
                        IncomePerCapErr     DECIMAL,
                        Poverty             DECIMAL,
                        ChildPoverty        DECIMAL,
                        Professional        DECIMAL,
                        Service             DECIMAL,
                        Office              DECIMAL,
                        Construction        DECIMAL,
                        Production          DECIMAL,
                        Drive               DECIMAL,
                        Carpool             DECIMAL,
                        Transit             DECIMAL,
                        Walk                DECIMAL,
                        OtherTransp         DECIMAL,
                        WorkAtHome          DECIMAL,
                        MeanCommute         DECIMAL,
                        Employed            INTEGER,
                        PrivateWork         DECIMAL,
                        PublicWork          DECIMAL,
                        SelfEmployed        DECIMAL,
                        FamilyWork          DECIMAL,
                        Unemployment        DECIMAL
                );
                -- Do not add primary key and index yet
        """)
        print(f"Created {TableName} (without constraints and indexes)")


# function to add primary key and index after data is loaded
def add_constraints_and_indexes(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
                ALTER TABLE {TableName} ADD PRIMARY KEY (TractId);
                CREATE INDEX idx_{TableName}_State ON {TableName}(State);
        """)
        print(f"Added PRIMARY KEY and INDEX on {TableName}")

def load_with_copy(conn, fname):
    print(f"Loading data from {fname} using COPY")
    with conn.cursor() as cursor:
        with open(fname, 'r') as f:
            start = time.perf_counter()

            sql = f"""
                COPY "{TableName}" FROM STDIN WITH (
                    FORMAT csv,
                    HEADER true,
                    NULL ''
                )
            """
            cursor.copy_expert(sql, f)

            elapsed = time.perf_counter() - start
            print(f"Finished Loading. Elapsed Time: {elapsed:0.4f} seconds")


# function to verify data in the database
def verify_data(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(DISTINCT state) FROM censusdata;")
        result = cursor.fetchone()
        print(f"Number of distinct states: {result[0]}")

        cursor.execute("SELECT COUNT(DISTINCT county) FROM censusdata WHERE state = 'Oregon';")
        result = cursor.fetchone()
        print(f"Number of distinct counties in Oregon: {result[0]}")

        cursor.execute("SELECT COUNT(DISTINCT county) FROM censusdata WHERE state = 'Iowa';")
        result = cursor.fetchone()
        print(f"Number of distinct counties in Iowa: {result[0]}")


# main function
def main():
    initialize()
    conn = dbconnect()

    if CreateDB:
        createTable(conn)

    load_with_copy(conn, Datafile)

    if CreateDB:
        add_constraints_and_indexes(conn)

    verify_data(conn)


if __name__ == "__main__":
    main()
