# Resposta Desafio

## Como executar o pipeline

### Para executar o Step 1:
**Obter os dados do csv:**
- Acessar o terminal e entrar na pasta meltano-lighthouse/fonte-csv
- Executar o comando:
```bash
meltano invoke airflow scheduler -D
```
- Em seguida, executar o comando:
```bash
meltano invoke airflow webserver
```
- Acessar o Airflow em: http://localhost:8080
- Verificar a execução da dag csv-to-csv, conferindo nos logs caso a execução falhe.

**Obter os dados do PostgreSQL:**
- Acessar o terminal e entrar na pasta meltano-lighthouse/fonte-postgres
- Executar o comando:
```bash
meltano invoke airflow scheduler -D
```
- Em seguida, executar o comando:
```bash
meltano invoke airflow webserver
```
- Acessar o Airflow em: http://localhost:8080
- Verificar a execução da dag postgres_to_csv, conferindo nos logs caso a execução falhe.
 
### Para executar o Step 2:
- Acessar o terminal e entrar na pasta airflow-docker
- Executar o comando:
```bash
docker-compose up
```
- Acessar o Airflow em: http://localhost:8080
- Verificar a execução da dag csv_to_postgres, conferindo nos logs caso a execução falhe.
- Caso seja desejado executar o step 2 para uma data anterior a data atual, criar no airflow em Admin > Variables a variável _execution_date_ com a data desejada no formato _YYYY-MM-DD_.

### Pré-requisitos para execução do pipeline:
- Ter instalado docker e meltano.
- Ter as pastas airflow_docker e meltano-lighthouse conforme disponível neste repositório.
- Estar com os containers dos bancos de dados fonte e destino ativos.

## Detalhamento técnico

### Escolha das ferramentas
Para construir o pipeline escolhi o Meltano devido minha afinidade com Python. Para utilização do Airflow, devido ao conflito de depências, preferi executá-lo através do docker-compose. E para o Postgresql, também o executei com o docker devido ao benefício de isolar os bancos de dados fonte e destino e da praticidade em destruir e subir os containers.

### Fontes de dados
O arquivo .csv foi baixado do repositório e consumido através da própria pasta de Dowloads. Já para a fonte PostgreSQL foi baixado o arquivo northwind.sql e utilizado para criar o banco de dados fonte com o docker através do comando:

```bash
docker run --name fonte -e POSTGRES_DB=dbfonte -e POSTGRES_USER=gpb -e POSTGRES_PASSWORD=5577 -d -p 5577:5432 -v "$(pwd)"/northwind.sql:/docker-entrypoint-initdb.d/northwind.sql postgres
```
Obs.: devido a um erro que estava ocorrendo no meltano foi necessário alterar o arquivo northwind.sql mudando do tipo de dado _real_ para o tipo _character varying(5)_.

### Banco de dados de destino
```bash

```


### Estrutura do pipeline
Como um dos requisitos do desafio é ter uma separação nos caminhos dos arquivos que serão criados para cada fonte, foram criados dois projetos Meltano, a fim de direcionar o target-postgres para caminhos de pastas diferentes.
