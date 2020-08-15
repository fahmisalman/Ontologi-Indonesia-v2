import mysql.connector

def connect():
    db = mysql.connector.connect(host="127.0.0.1",      # your host, usually localhost
                        user="root",           # your username
                        passwd="",             # your password
                        db="db_scbd")          # name of the data base
    return db
