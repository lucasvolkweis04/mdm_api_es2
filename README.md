🌍 DEM Service - ETL API
Bem-vindo ao DEM Service, uma API FastAPI para gerenciar processos ETL (Extract, Transform, Load). Este serviço permite executar e monitorar transações ETL de forma simples e eficiente. 🎉

Este projeto é composto por dois serviços principais:
DEM Service: Gerencia processos ETL (Extract, Transform, Load) para manipulação de dados.
MDM Service: Gerencia informações de países, como nomes, regiões e códigos.

📋 Funcionalidades
DEM Service
Extract: Extração de dados com execução de scripts externos.
Transform: Transformação de dados com lógica personalizada.
Load: Carregamento de dados para o destino final.
Monitoramento: Listagem e consulta de transações ETL.
MDM Service
CRUD de Países: Criação, leitura, atualização e exclusão de informações de países.
Filtros Avançados: Busca por região, nome ou código do país.

🛠️ Tecnologias Utilizadas
Python 🐍
FastAPI ⚡
SQLAlchemy 🗄️
SQLite para persistência de dados.
Subprocess para execução de scripts externos (DEM Service).

🚀 Como Executar o Projeto:
1. Clone o Repositório 
git clone https://github.com/seu-usuario/volks-project.git
cd volks-project

2. Instale as Dependências
Crie um ambiente virtual e instale as dependências:
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Execute os Serviços
DEM Service
Inicie o servidor do DEM Service:
uvicorn dem_service.main:app --reload

Acesse a documentação interativa da API em http://127.0.0.1:8000/docs 📚.

MDM Service
Inicie o servidor do MDM Service:
uvicorn mdm_service.main:app --reload

Acesse a documentação interativa da API em http://127.0.0.1:8001/docs 📚.

📚 Endpoints
DEM Service:
POST /etl/extract: Executa o processo de extração de dados.
POST /etl/transform: Executa o processo de transformação de dados.
POST /etl/load: Executa o processo de carregamento de dados.
GET /etl/transactions: Lista todas as transações ETL realizadas.
GET /etl/transactions/{tx_id}: Consulta os detalhes de uma transação ETL específica.
MDM Service:
POST /countries: Cria um novo país.
GET /countries: Lista países com suporte a filtros (região, nome, etc.).
GET /countries/{cca3}: Consulta informações de um país específico.
PUT /countries/{cca3}: Atualiza informações de um país.
DELETE /countries/{cca3}: Remove um país.

📂 Estrutura do Projeto
volks/
├── dem_service/
│   ├── main.py          # Serviço DEM (ETL)
│   ├── models.py        # Modelos do banco de dados (DEM)
│   ├── database.py      # Configuração do banco de dados (DEM)
│   ├── schemas.py       # Schemas para validação de dados (DEM)
│   ├── crud.py          # Operações CRUD (DEM)
│   └── load_countries.py # Script de extração de dados
├── mdm_service/
│   ├── main.py          # Serviço MDM (CRUD de países)
│   ├── models.py        # Modelos do banco de dados (MDM)
│   ├── database.py      # Configuração do banco de dados (MDM)
│   ├── schemas.py       # Schemas para validação de dados (MDM)
│   └── crud.py          # Operações CRUD (MDM)
├── shared/
│   ├── database.py      # Configuração compartilhada do banco de dados
│   └── utils.py         # Funções utilitárias (se necessário)
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação do projeto

🧪 Testes
Para rodar os testes, utilize:
pytest

💡 Autor
Desenvolvido por Lucas Volkweis. 😊

Se tiver dúvidas ou sugestões, sinta-se à vontade para entrar em contato no email: lucas.volkweis@edu.pucrs.br 📬
