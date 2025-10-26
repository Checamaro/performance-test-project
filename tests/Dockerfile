FROM python:3.9-slim

WORKDIR /tests

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    default-jre \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Allure
RUN curl -o allure-2.24.0.tgz -Ls https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz \
    && tar -zxvf allure-2.24.0.tgz -C /opt/ \
    && ln -s /opt/allure-2.24.0/bin/allure /usr/bin/allure

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код тестов
COPY . .

# Команда по умолчанию
CMD ["python", "-m", "pytest", "api/", "-v", "--alluredir=/tmp/allure-results"]