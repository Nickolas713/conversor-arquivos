
# Use uma imagem base Python
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY app.py .

# Expõe a porta que a aplicação Flask vai usar
EXPOSE 5000

# Define a variável de ambiente para o Flask
ENV FLASK_APP=app.py

# Comando para rodar a aplicação
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]


