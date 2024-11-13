import datetime
from sqlalchemy import create_engine, text


username = "okurkowski"
password = ""
host = "192.168.120.253"
port = "5432"
cowcross = "cowcross"
import_files = "import_files"


def db_create_engine(database_name):
    connection_string = (
        f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
    )
    return create_engine(connection_string)


def getIDs():
    engine = db_create_engine(cowcross)
    with engine.connect() as connection:
        query = text(
            f"""
            select kod_klauzuli,wierzytelnosc from  edw.do_pobrania_agio_axfina
order by saldo desc
            """
        )
        query_result = connection.execute(query)
        kodyKlauzuli = [row[0] for row in query_result]
        # Pobieram listę ID zinsertowanych
        insertedIds = set(getInserted())

        # Filtruje tylko ID, które nie są w insertedIds
        uninsertedIds = [id_epu for id_epu in kodyKlauzuli if id_epu not in insertedIds]

        return uninsertedIds


def getInserted():
    engine = db_create_engine(import_files)
    with engine.connect() as connection:
        query = text(
            f"""
            select kod_kluzuli from scrap.klauzula_epu
            """
        )
        query_result = connection.execute(query)
        return [row[0] for row in query_result]


def insertXmlInfo(id, xml, pdfPath):
    engine = db_create_engine(import_files)
    with engine.connect() as connection:
        query = text(
            """
            INSERT INTO scrap.klauzula_epu
            VALUES (:id, :xmlInfo, :pdfPath, :todayDate);"""
        )
        parametry = {
            "id": id,
            "xmlInfo": xml,
            "pdfPath": pdfPath,
            "todayDate": datetime.datetime.now(),
        }
        try:
            connection.execute(query, parametry)
            connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
