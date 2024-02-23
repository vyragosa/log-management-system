import datetime
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Log, Base


class LogManager:
    def __init__(self, db_name='logs.db'):
        self.engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    def add_log(self, user_id, log_level, message, timestamp=None):
        with self.session() as session:
            try:
                if timestamp is None:
                    timestamp = datetime.datetime.now()
                log = Log(user_id=user_id, log_level=log_level, message=message, timestamp=timestamp)
                session.add(log)
                session.commit()

                # if log_level == 'error' and user_id:
                #     error_count = session.query(Log).filter(Log.user_id == user_id, Log.log_level == 'error').count()
                #     if error_count % 10 == 0:
                #         self.__send_notification(user_id, message)

            except Exception as e:
                session.rollback()
                raise e

    def get_logs(self, user_id=None, log_level=None, start_time=None, end_time=None):
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

    def export_logs(self, filename):
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        if not filename.endswith('.json'):
            filename += '.json'

        filepath = os.path.join(reports_dir, filename)
        logs = self.get_logs()
        logs_data = [{'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                      'user_id': log.user_id,
                      'log_level': log.log_level,
                      'message': log.message} for log in logs]
        with open(filepath, 'w') as file:
            json.dump(logs_data, file, indent=4)

    def clear_logs(self):
        with self.session() as session:
            session.query(Log).delete()
            session.commit()

    def __get_errors_logs(self, user_id):
        with self.session() as session:
            try:
                query = session.query(Log).filter(Log.user_id == user_id, Log.log_level == 'error')
                logs = query.all()
                return [logs[i] for i in range(len(logs)) if (i + 1) % 10 == 0]
            except Exception as e:
                raise e

    def print_error_logs(self, user_id):
        tenth_error_logs = self.__get_errors_logs(user_id)
        if tenth_error_logs:
            for log in tenth_error_logs:
                print(f"Timestamp: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, "
                      f"Message: {log.message}")
        else:
            print(f"Ошибок по {user_id} не найдено.")

    @staticmethod
    def __send_notification(user_id, message):
        print(f"Уведомление пользователя с {user_id} о 10 по счету ошибке: {message}")
