from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
import uvicorn

app = FastAPI()

security = HTTPBasic()

# Данные о сотрудниках
employees = {
    'john': {'password': 'password123', 'salary': 5000, 'promotion_date': '2023-07-01'},
    'jane': {'password': 'password456', 'salary': 6000, 'promotion_date': '2023-08-01'}
}

# Словарь, содержащий выданные токены
tokens = {}


# Функция для проверки валидности токена
def is_token_valid(token):
    if token in tokens:
        expiry_time = tokens[token]['expiry_time']
        if datetime.now() < expiry_time:
            return True
        else:
            del tokens[token]
    return False


# Маршрут для аутентификации и получения токена
@app.post('/login')
def login(credentials: HTTPBasicCredentials):
    username = credentials.username
    password = credentials.password

    if username in employees and employees[username]['password'] == password:
        token = str(datetime.now().timestamp())
        expiry_time = datetime.now() + timedelta(minutes=30)  # Токен действует 30 минут
        tokens[token] = {'username': username, 'expiry_time': expiry_time}
        return {'token': token}

    raise HTTPException(status_code=401, detail='Invalid credentials')


# Маршрут для получения данных о зарплате
@app.get('/salary')
def get_salary(token: str = Depends(security)):
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail='Invalid token')

    username = tokens[token]['username']
    salary = employees[username]['salary']
    promotion_date = employees[username]['promotion_date']

    return {'salary': salary, 'promotion_date': promotion_date}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)