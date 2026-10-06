import psycopg2


class Database:

    def __init__(self):

        self.connection = psycopg2.connect(
            host="localhost",
            database="robot_agricola",
            user="robot",
            password="robot123",
            port="5432"
        )

        self.cursor = self.connection.cursor()

        print("Conexión con PostgreSQL realizada.")

    def execute(self, consulta, datos=None):

        self.cursor.execute(consulta, datos)

        self.connection.commit()

    def fetch_one(self, consulta, valores=None):

        self.cursor.execute(consulta, valores)

        return self.cursor.fetchone()


    def fetchall(self, consulta, datos=None):

        self.cursor.execute(consulta, datos)

        return self.cursor.fetchall()