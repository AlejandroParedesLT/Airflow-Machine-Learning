import json
from sqlalchemy import text
from api.database.Conexion_SQL_Server import SQLServerConnection
import logging
from datetime import datetime

log_file = './mlapi_logs.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Estado_ATM:
    @staticmethod
    async def process_message(message):
        data = json.loads(message)
        session = None
        try:
            db_connection = SQLServerConnection()
            session = db_connection.get_session()
            
            last_change_time = datetime.fromtimestamp(data['LASTCHANGETIME'] / 1000) if data['LASTCHANGETIME'] else None
            warning_time = datetime.fromtimestamp(data['WARNINGTIME'] / 1000) if data['WARNINGTIME'] else None
            error_time = datetime.fromtimestamp(data['ERRORTIME'] / 1000) if data['ERRORTIME'] else None
            next_refresh_time = datetime.fromtimestamp(data['NEXTREFRESHTIME'] / 1000) if data['NEXTREFRESHTIME'] else None
            escalation_time = datetime.fromtimestamp(data['ESCALATIONTIME'] / 1000) if data['ESCALATIONTIME'] else None

            query = text("""
                INSERT INTO tranzaxis.TERMINDICATORSTATE_TEST  
                (TERMID, KIND, SEVERITY, REASON, LASTCHANGETIME, WARNINGTIME, ERRORTIME, NEXTREFRESHTIME, ESCALATIONTIME) 
                VALUES (:TERMID, :KIND, :SEVERITY, :REASON, :LASTCHANGETIME, :WARNINGTIME, :ERRORTIME, :NEXTREFRESHTIME, :ESCALATIONTIME)
            """)
            
            session.execute(query, {
                "TERMID": data['TERMID'], 
                "KIND": data['KIND'],
                "SEVERITY": data['SEVERITY'], 
                "REASON": data['REASON'],
                "LASTCHANGETIME": last_change_time, 
                "WARNINGTIME": warning_time,
                "ERRORTIME": error_time, 
                "NEXTREFRESHTIME": next_refresh_time,
                "ESCALATIONTIME": escalation_time
            })
            session.commit()
            logging.info("Registro insertado.")
        except Exception as e:
            if session:
                session.rollback()
            logging.error(f"Error al insertar la data en estado_atm: {e}")
        finally:
            if session:
                session.close()
            db_connection.close_engine()