- Sistema de Gestão de Dados Mestres (MDM + DEM)
- O Problema e a Solução
Sistemas corporativos frequentemente lidam com dados inconsistentes, duplicados ou desatualizados espalhados por diversas aplicações. O Master Data Management (MDM) resolve isso criando uma "fonte única de verdade" (Golden Record) para os dados críticos de uma organização.

Neste projeto, o desafio é consumir dados sobre países de uma fonte externa (API restcountries.com), tratar essas informações e centralizá-las de forma confiável. Para garantir a qualidade e a separação de responsabilidades, a solução foi dividida em dois microsserviços: o DEM lida com o "trabalho sujo" de extração e limpeza (ETL), garantindo que apenas dados validados e padronizados cheguem ao MDM, que por sua vez os disponibiliza para consumo seguro por outras aplicações.

🧱 Arquitetura
DEM (Data Extraction & Management): Responsável por coletar os dados brutos da API externa, salvar os arquivos originais em disco (preservando o histórico), aplicar as regras de processamento e disponibilizar a versão limpa.

MDM (Master Data Management): Consome os dados já processados pelo DEM, armazena no banco de dados principal da aplicação e os disponibiliza via endpoints de CRUD.

Comunicação: Os dois microsserviços são totalmente independentes e se comunicam de forma síncrona via HTTP.

🚀 Como Executar Localmente
1. Clone o repositório e acesse a pasta do projeto:

Bash
git clone https://github.com/lucasvolkweis04/mdm_api_es2.git
cd mdm_api_es2
2. Crie e ative o ambiente virtual:

Bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
3. Instale as dependências:

Bash
pip install -r requirements.txt
4. Inicie os serviços (recomenda-se abrir dois terminais separados):

Bash
# Terminal 1 - Serviço MDM
uvicorn mdm_service.main:app --reload --port 8001

# Terminal 2 - Serviço DEM
uvicorn dem_service.main:app --reload --port 8002
5. Acesse as documentações interativas no navegador:

MDM API: http://localhost:8001/docs

DEM API: http://localhost:8002/docs

🧪 Fluxo ETL
Extração: POST /providers (DEM) - Faz o download dos dados da API externa e salva o arquivo JSON na pasta de dados brutos.

Transformação: GET /countries/processed-latest (DEM) - Lê os arquivos brutos, processa os dados e retorna as informações padronizadas.

Carga (Load): POST /sync-from-dem (MDM) - Consome os dados da API do DEM e os persiste definitivamente no banco de dados do MDM.

📂 Estrutura do Projeto
Plaintext
.
├── dem_service/        # Microsserviço de extração e transformação (DEM)
├── mdm_service/        # Microsserviço de armazenamento e CRUD (MDM)
├── storage/            # Sistema de arquivos local
│   ├── raw/            # Arquivos JSON brutos originais
│   └── processed/      # Arquivos JSON após limpeza e tratamento
├── docker-compose.yml  # Orquestração de containers Docker
├── requirements.txt    # Dependências do projeto
└── README.md           # Documentação

✅ Requisitos Atendidos - Arquitetura de microsserviços RESTful.

Processamento e pipeline ETL completos (Extract, Transform, Load).

Operações de CRUD completas no microsserviço MDM.

Estratégia de armazenamento em disco separando dados originais e processados (raw/processed).

Comunicação HTTP eficiente entre os microsserviços.

Compatibilidade nativa para execução local ou conteinerizada via Docker.

👨🏻‍💻 Autoria
Desenvolvido por Lucas Volkweis para a disciplina de Engenharia de Software II (PUCRS).
