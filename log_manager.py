import datetime
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Log, Base
from tabulate import tabulate


class LogManager:
    def __init__(self, db_name='logs.db'):
        self.engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    def add_log(self, user_id: int, log_level: str, message: str, timestamp=None) -> None:
        with self.session() as session:
            try:
                if timestamp is None:
                    timestamp = datetime.datetime.now()
                log = Log(user_id=user_id,
                          log_level=log_level,
                          message=message,
                          timestamp=timestamp)
                session.add(log)
                session.commit()

                if log_level == 'error' and user_id:
                    error_count = session.query(Log).filter(Log.user_id == user_id,
                                                            Log.log_level == 'error').count()
                    if error_count % 10 == 0:
                        self.__send_notification(user_id, message)

            except Exception as e:
                session.rollback()
                raise e

    def __get_logs(self, user_id=None, log_level=None, start_time=None, end_time=None) -> list:
        with self.session() as session:
            try:
                query = session.query(Log)
                if user_id:
                    query = query.filter(Log.user_id == user_id)
                if log_level:
                    query = query.filter(Log.log_level == log_level)
                if start_time:
                    query = query.filter(Log.timestamp >= start_time)
                if end_time:
                    query = query.filter(Log.timestamp <= end_time)
                logs = query.all()
                return logs
            except Exception as e:
                raise e

    def export_logs(self, filename: str) -> None:
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        if not filename.endswith('.json'):
            filename += '.json'

        filepath = os.path.join(reports_dir, filename)
        logs = self.__get_logs()
        logs_data = [{'id': log.id,
                      'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                      'user_id': log.user_id,
                      'log_level': log.log_level,
                      'message': log.message} for log in logs]
        with open(filepath, 'w') as file:
            json.dump(logs_data, file, indent=4)

    def clear_logs(self):
        session = self.session()
        session.query(Log).delete()
        session.commit()
        session.close()

    def output_logs(self, user_id=None, log_level=None, start_time=None, end_time=None) -> str:
        logs = self.__get_logs(user_id=user_id,
                               log_level=log_level,
                               start_time=start_time,
                               end_time=end_time)

        if not logs:
            return "Не найдено логов по входным параметрам"

        log_data = [
            [
                log.id,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user_id,
                log.log_level,
                log.message
            ] for log in logs
        ]
        return tabulate(tabular_data=log_data,
                        headers=["ID", "Timestamp", "User ID", "Log Level", "Message"],
                        tablefmt="simple")

        # return "\n".join([
        #     f"ID: {log.id}\n"
        #     f"Timestamp: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        #     f"User ID: {log.user_id}\n"
        #     f"Log Level: {log.log_level}\n"
        #     f"Message: {log.message}\n"
        #     f"{'-' * 50}" for log in logs
        # ])

    @staticmethod
    def __send_notification(user_id: int, message: str):
        print(f"Уведомление пользователя с {user_id} о 10 по счету ошибке: {message}")

    def __str__(self):
        logs = self.__get_logs()
        log_data = [
            [
                log.id,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user_id,
                log.log_level,
                log.message
            ] for log in logs
        ]
        return tabulate(tabular_data=log_data,
                        headers=["ID", "Timestamp", "User ID", "Log Level", "Message"],
                        tablefmt="simple")
