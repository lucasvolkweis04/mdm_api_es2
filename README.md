Sistema de Gestão de Dados Mestres (MDM + DEM)

Este projeto implementa um sistema de Master Data Management composto por dois microsserviços RESTful: DEM (Extração e transformação de dados) e MDM (armazenamento e CRUD de dados tratados).

⸻

🧱 Arquitetura
	•	DEM: Responsável por coletar dados brutos da API externa, nesse caso a restcountries.com, salvar os arquivos em disco e processá-los.
	•	MDM: Responsável por importar os dados tratados do DEM e disponibilizá-los via CRUD.
	•	Microsserviços independentes, comunicando-se via HTTP.

⸻

🚀 Como executar com Docker

1. Clonar o repositório e acessar a pasta do projeto

git clone <url>
cd mdm_api_es2

2. Criar a estrutura de pastas de armazenamento

mkdir -p storage/raw
mkdir -p storage/processed

3. Subir os microsserviços com Docker Compose

docker-compose up --build

	•	MDM: http://localhost:8001/docs
	•	DEM: http://localhost:8002/docs

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

📌 Variáveis de Ambiente

No MDM:

DEM_URL=http://dem:8002


⸻

✅ Requisitos atendidos
	•	Arquitetura de microsserviços RESTful
	•	Processamento ETL completo
	•	CRUD completo no MDM
	•	Armazenamento de arquivos em disco (raw/processed)
	•	Comunicação HTTP entre microsserviços
	•	Compatível com execução local ou Docker

⸻

👨🏻‍💻 Equipe & Licença

Desenvolvido por lucas volkweis para a disciplina de Engenharia de Software II (PUCRS).