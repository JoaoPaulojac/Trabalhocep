📈 Calculadora de Controle Estatístico de Processo (CEP)
Esta é uma aplicação web simples desenvolvida em Python (Flask) que lê dados de um arquivo JSON (dados_simulado_prova_1.json) para resolver um conjunto de problemas de Controle Estatístico de Processo (CEP) baseados no Simulado_prova_1.pdf.

O backend realiza todos os cálculos estatísticos (limites de controle, capacidade do processo, etc.) e gera os gráficos de controle usando Matplotlib. O frontend exibe todos os resultados em uma interface web limpa e organizada.

📊 Funcionalidades
Leitura de Dados: Carrega automaticamente os dados das amostras do arquivo dados_simulado_prova_1.json.

Gráficos X-R: Calcula e exibe os gráficos de controle X-barra (Médias) e R (Amplitudes), incluindo Linha Central (LC), Limite Superior de Controle (LSC) e Limite Inferior de Controle (LIC).

Geração de Imagens: Utiliza Matplotlib no backend para gerar e exibir os gráficos como imagens estáticas na página web.

Análise de Controle: Verifica se o processo está sob controle estatístico, listando quaisquer pontos fora dos limites.

Regras de Western Electric: Analisa os dados do gráfico X-barra em busca de violações das 4 principais regras de sensibilidade.

Análise de Capacidade (Q2): Calcula e exibe o desvio padrão estimado (σ̂), o índice de Capacidade do Processo (Cp) e o índice de Desempenho do Processo (Cpk).

Cálculos de Probabilidade (Q2 & Q3): Resolve problemas de probabilidade normal (yield, chance de valores acima de um limite) e binomial.

Interface Limpa: Apresenta todos os resultados em uma página web única, organizada e com CSS externo.

📁 Estrutura do Projeto
O projeto deve seguir esta estrutura de pastas para funcionar corretamente:

CEP/
|
|-- app.py                       # Servidor backend (Flask)
|-- dados_simulado_prova_1.json  # Fonte de dados das amostras
|-- requirements.txt             # Dependências do Python
|-- README.md                    # Este arquivo
|
+-- static/                      # Pasta para arquivos estáticos
|   |-- style.css                # Folha de estilo
|
+-- templates/                   # Pasta para templates HTML
    |-- index.html               # Página web principal
Importante: O arquivo dados_simulado_prova_1.json deve estar na mesma pasta que o app.py.

🚀 Tecnologias Utilizadas
Backend
Python 3

Flask: Micro-framework web para servir a aplicação.

Numpy: Para cálculos numéricos e estatísticos (médias, max, min).

Scipy: Para funções estatísticas avançadas (distribuição normal, binomial).

Matplotlib: Para a geração dos gráficos de controle.

Frontend
HTML5

CSS3: Para estilização (via static/style.css).

⚙️ Instalação e Configuração
Pré-requisito: Certifique-se de ter o Python 3 instalado.

Crie a Estrutura: Crie os arquivos e pastas conforme a Estrutura do Projeto descrita acima.

Crie um Ambiente Virtual (Recomendado): Abra um terminal na pasta projeto_cep e execute:

Bash

# Criar o ambiente
python -m venv venv

# Ativar o ambiente
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
Instale as Dependências: Com o ambiente virtual ativado, instale as bibliotecas necessárias:

Bash

pip install -r requirements.txt
⚡ Como Executar
Inicie o Servidor: Ainda no terminal, na pasta raiz do projeto (projeto_cep/), execute o script principal:

Bash

python app.py
Acesse no Navegador: Abra seu navegador e acesse a seguinte URL:

http://127.0.0.1:5000
A página carregará automaticamente, buscará os dados do JSON, realizará todos os cálculos e exibirá os resultados e gráficos.