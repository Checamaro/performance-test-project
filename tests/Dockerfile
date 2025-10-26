FROM python:3.9-slim

WORKDIR /tests

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements первыми для лучшего кэширования
COPY requirements.txt .

# Устанавливаем Python зависимости с ретраями и зеркалом
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt || \
    pip install --no-cache-dir -i https://pypi.douban.com/simple/ --trusted-host pypi.douban.com -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Install Allure commandline (опционально, можно закомментировать если не нужно)
# RUN apt-get update && apt-get install -y default-jre curl && \
#     curl -o allure-2.24.0.tgz -Ls https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz && \
#     tar -zxvf allure-2.24.0.tgz -C /opt/ && \
#     ln -s /opt/allure-2.24.0/bin/allure /usr/bin/allure

CMD ["python", "-m", "pytest", "api/", "-v"]
