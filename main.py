import datetime
import random
import string
from log_manager import LogManager
from random import randint


def generate_random_log():
    user_id = randint(0, 9)
    log_level = random.choice(['info', 'warning', 'error'])
    message = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    return user_id, log_level, message


def generate_logs(log_manager, num_logs):
    for _ in range(num_logs):
        user_id, log_level, message = generate_random_log()
        log_manager.add_log(user_id=user_id, log_level=log_level, message=message)


def main():
    log_manager = LogManager()
    log_manager.clear_logs()
    generate_logs(log_manager, 1000)
    print(f"Успешно добавлены логи")
    log_manager.export_logs("logs")
<<<<<<< HEAD
    log_manager.print_error_logs(user_id=1)
=======
    print(log_manager.output_logs(user_id=1))
>>>>>>> 17edef3418f33fb7a996b755038da9bc5f93d14f


if __name__ == "__main__":
    main()
