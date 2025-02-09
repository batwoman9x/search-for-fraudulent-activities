import pandas as pd
from geoip2.database import Reader

# Загрузка исходных файлов
transactions = pd.read_csv('dataset.csv')  # Файл с информацией о транзакциях
predictions = pd.read_csv('preds.csv', names=["Prediction"])  # Файл с метками True/False

# Проверка размерности файлов
if len(transactions) != len(predictions):
    raise ValueError("Количество записей в файлах 'dataset.csv' и 'dataset_with_cities.csv' не совпадает.")

# Добавление метки True/False к транзакциям
transactions['Prediction'] = predictions['Prediction']

# Фильтрация записи с меткой True
threats = transactions[transactions['Prediction'] == True].copy()

# Инициализация GeoIP2 для определения местоположения
geoip_db_path = 'GeoLite2-City.mmdb'  # Путь к базе GeoLite2
reader = Reader(geoip_db_path)

def get_location(ip):
    """
    Определяет страну и город по IP-адресу.
    :param ip: IP-адрес.
    :return: Строка формата "Страна, Город" или "Unknown".
    """
    try:
        response = reader.city(ip)
        country = response.country.name or 'Unknown'
        city = response.city.name or 'Unknown'
        return f"{country}, {city}"
    except Exception:
        return "Unknown"

# Создание новыго столбеца с местоположением
threats['Местоположение'] = threats['ip'].apply(get_location)

# Определение способа доступа
def determine_access_method(device_type):
    """
    Определяет способ доступа: Приложение или Банкомат.
    :param device_type: Тип устройства.
    :return: Строка "Приложение" или "Банкомат".
    """
    return "Банкомат" if device_type.lower() in ['atm', 'terminal'] else "Приложение"

threats['Способ доступа'] = threats['device_type'].apply(determine_access_method)

# Отбор только нужных столбцов, включая дату
final_threats = threats[['transaction_id', 'datetime', 'Местоположение', 'mcc', 'sum', 'pin_inc_count', 'Способ доступа']]

# Добавление столбеца с индексами, начиная с 0
final_threats.reset_index(drop=True, inplace=True)
final_threats.index.name = "0"
final_threats.reset_index(inplace=True)

# Сохранение результата в новый CSV-файл
final_threats.to_csv('угрозы_с_датой.csv', index=False, encoding='utf-8-sig')

# Закрытие GeoIP2
reader.close()

print("Файл 'угрозы_с_датой.csv' успешно создан.")
