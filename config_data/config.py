import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены, т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ("get_reservation", "Записаться на прием"),
    ("my_advices", "Мои записи"),
    ("get_often_questions", "Частые вопросы"),
    ("send_data", "Отправить данные"),
)

ADMIN_COMMANDS = (
    ("admin_panel", "Админка"),
    ("get_report", "Запросить отчет"),
    ("run_generating", "Сгенерировать расписание"),
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_TO_PYTHON = os.path.normpath(os.path.join(BASE_DIR, "venv/Scripts/python.exe"))
ADMIN_ID = os.getenv('ADMIN_ID')
ALLOWED_USERS = [int(ADMIN_ID),
                 5999316078  # ID владельца бота
                 ]
