🌎 Sistema de Gestão de Dados Mestres (MDM + DEM)

Este projeto implementa um sistema de Master Data Management composto por dois microsserviços RESTful: DEM (Extração e transformação de dados) e MDM (armazenamento e CRUD de dados tratados).

⸻

🧱 Arquitetura
	•	DEM: Responsável por coletar dados brutos da API externa, nesse caso a restcountries.com, salvar os arquivos em disco e processá-los, depois envia ao banco próprio;
	•	MDM: Responsável por importar os dados tratados do DEM e disponibilizá-los via CRUD.
	•	Microsserviços independentes, comunicando-se via HTTP.

⸻

🚀 Como executar o programa:

1. Clonar o repositório e acessar a pasta do projeto

git clone <https://github.com/lucasvolkweis04/mdm_api_es2.git>
cd mdm_api_es2


2. Crie um ambiente virtual e instale as dependências:

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Inicie os serviços:
uvicorn mdm_service.main:app --reload --port 8001
uvicorn dem_service.main:app --reload --port 8002

4. No navegador acesse:
http://localhost:8001/docs#/  - MDM
http://localhost:8002/docs#/  - DEM
⸻

🧪 Fluxo ETL
	1.	POST /providers (DEM): faz download e salva os dados da API externa.
	2.	GET /countries/processed-latest (DEM): retorna os dados tratados.
	3.	POST /sync-from-dem (MDM): consome os dados da API do DEM e armazena no banco.

⸻

📂 Estrutura

.
├── dem_service/          # Microsserviço DEM
├── mdm_service/          # Microsserviço MDM
├── storage/
│   ├── raw/              # JSON bruto
│   └── processed/        # JSON processado
├── docker-compose.yml
├── requirements.txt
└── README.md


⸻

✅ Requisitos atendidos
	•	Arquitetura de microsserviços RESTful
	•	Processamento ETL completo
	•	CRUD completo no MDM
	•	Armazenamento em storage(raw/processed)
	•	Comunicação HTTP entre microsserviços
	•	Compatível com execução local ou Docker

⸻

👨🏻‍💻 Desenvolvido por Lucas Volkweis para a disciplina de Engenharia de Software II (PUCRS).
