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
- Caso seja desejado executar o step 2 para uma data anterior a data atual, criar no Airflow em Admin > Variables a variável _execution_date_ com a data desejada no formato _YYYY-MM-DD_.

### Pré-requisitos para execução do pipeline:
- Ter instalado docker e meltano.
- Ter as pastas airflow_docker e meltano-lighthouse conforme disponível neste repositório.
- Estar com os containers dos bancos de dados fonte e destino ativos.

## Detalhamento técnico

### Escolha das ferramentas
Para construir o pipeline escolhi o Meltano devido minha afinidade com Python. Para utilização do Airflow, devido ao conflito de depências, preferi executá-lo através do docker-compose. Para o Postgresql, também o executei com o docker devido ao benefício de isolar os bancos de dados fonte e destino e da praticidade em destruir e subir os containers. Para armazenamento no sistema local, escolhi o tipo de arquivo .csv devido sua manipulação ser mais fácil para inserir os dados no banco de dados posteriormente.

### Fontes de dados
O arquivo .csv foi baixado do repositório e consumido através da própria pasta de Dowloads. Já para a fonte PostgreSQL foi baixado o arquivo northwind.sql e utilizado para criar o banco de dados fonte com o docker através do comando:

```bash
docker run --name fonte -e POSTGRES_DB=dbfonte -e POSTGRES_USER=gpb -e POSTGRES_PASSWORD=5577 -d -p 5577:5432 -v "$(pwd)"/northwind.sql:/docker-entrypoint-initdb.d/northwind.sql postgres
```
Obs.: devido a um erro que estava ocorrendo no meltano foi necessário alterar o arquivo northwind.sql mudando do tipo de dado _real_ para o tipo _character varying(5)_.

### Banco de dados de destino
Para o banco de dados de destino foi criado o arquivo destino.sql e executado o seguinte comando:
```bash
docker run --name destino -e POSTGRES_DB=dbdestino -e POSTGRES_USER=gpb -e POSTGRES_PASSWORD=5588 -d -p 5588:5432 -v "$(pwd)"/destino.sql:/docker-entrypoint-initdb.d/destino.sql postgres
```
Como o Airflow está sendo executado em um container e o banco de dados em outro, para realizar a conexão foi estabelecido o _postgres_conn_id='postgres_destino'_ no arquivo da dag csv_to_postgres.py. Para tal é necessário configurar no Airflow uma conexão com postgres_destino como Connection Id. Sua única particularidade é que o host deve ser o endereço IP da máquina que hospeda os containers (localhost não funciona, pois iria redirecionar para o localhost do container que hospeda o Airflow).

### Estrutura do pipeline
Como um dos requisitos do desafio é ter uma separação nos caminhos dos arquivos que serão criados para cada fonte, foram criados dois projetos Meltano, a fim de direcionar o target-postgres para caminhos de pastas diferentes. Assim o pipeline ficou estruturado da seguinte maneira:

![estrutura_pipeline](https://github.com/Gabriela-Pereira-Barros/code-challenge-lighthouse/assets/161372019/15476957-b11b-4019-80ae-aa17b1e0a198)

Apesar das dags estarem em seções diferentes do Airflow, a dag que corresponde ao Step 2, só poderá ser executada com sucesso caso o Step 1 seja executado, pois depende dos arquivos gerados por ele. Uma mensagem de aviso foi adionada ao arquivo csv_to_postgres para auxiliar na identificação desta situação no log de erro.

### Agendamento
Para as três dags do pipeline foi utilizado _schedule_interval_ como _"* * * * 1-5"_ que determinada que elas serão executadas diariamente de segunda a sexta, sendo que essa configuração pode ser alterada de acordo com as regras de negócio do cliente.

### Resultado 
Para obeter o resultado executei a seguinte query no banco de dados de destino:
```sql
SELECT
    o.order_id,
    customer_id,
    employee_id,
    order_date,
    required_date,
    shipped_date,
    ship_via,
    freight,
    ship_name,
    ship_address,
    ship_city,
    ship_region,
    ship_postal_code,
    ship_country,
    product_id,
    unit_price,
    quantity,
    discount
FROM public.orders AS o
JOIN public.order_details AS od ON o.order_id = od.order_id
```
O arquivo resultado.csv traz os dados obtidos com essa query.
