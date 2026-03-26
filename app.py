import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

# ==========================================
# 1. BANCO DE DADOS VIP
# ==========================================
BANCO_DE_DADOS_VIP = """
--- BANCO DE DADOS VIP ---
- Claudio Sanches Neto | Mat: F8036002 | Setor: CEO | GSM: +5521981135404
- Gustavo Darzi De Lemos | Mat: F8027975 | Setor: Devices to the Customer | GSM: +5521981131430
- CHRISTIANE MORAES POSTIGLIONI DE OLIVEIRA | Mat: F8084637 | Setor: Sales Consumer & SMB | GSM: +5521981132871
- Anderson Monteiro De Oliveira | Mat: F8079844 | Setor: Office Automation | GSM: +5521981132799
- Karla De Paula Pinto | Mat: F8033593 | Setor: Regional Sales Support SE | GSM: +5521981133351
- Michele Craveiro Freitas | Mat: F8009869 | Setor: Legal | GSM: +5521981130021
- Patricia Carla do Couto Gomes | Mat: 8031734 | Setor: Chief Financial Officer | GSM: 21981130880
- BRUNA TROTTA | Mat: 8074953 | Setor: Customer Relations | GSM: 2141126685
- THIAGO LUIZ SILVEIRA FERREIRA | Mat: 8073946 | Setor: Residential Marketing | GSM: 21981130816
- Virgínia Carvalho Ferreira | Mat: 8006297 | Setor: Audit | GSM: 21981133085
- SILVANA DOS SANTOS MORAES | Mat: 8033607 | Setor: Chief Technology Information Officer | GSM: 21981136161
- LORENA GONCALVES NEVES | Mat: 8079113 | Setor: ADMINISTRATIVE & TAX SERVICES | GSM: 21981134023
- Tuany Cristine Sena De Melo | Mat: 8079070 | Setor: SALES CONSUMER & SMB | GSM: 981133938
- REJANE OLIVEIRA LOUREIRO | Mat: 8014727 | Setor: REGULATORY, INSTITUT. AND PRESS RELATIONS | GSM: 2181130137
- ANA CLAUDIA REBOUCAS | Mat: 8048855 | Setor: NETWORK DEVELOPMENT | GSM: 2141094731
- ISABELA FERREIRA DE SOUZA | Mat: 8042531 | Setor: Human Resources & Organization | GSM: 2181130880
- SAMUEL DE SOUZA | Mat: 8042035 | Setor: Marketing Consumer & SMB | GSM: 2181134187
- PATRICIA PEREIRA GARCIA | Mat: 8005961 | Setor: PRESIDÊNCIA | GSM: 21981133030
- THAIS PESTANA DE ALMEIDA | Mat: 8079907 | Setor: Regulatory Affairs | GSM: 21981131025
- FABRICIA GONCALVES PIMENTEL | Mat: 8079471 | Setor: INFORMATION TECHNOLOGY | GSM: 21981131958
- ELIO FERREIRA DE FREITAS | Mat: 8068213 | Setor: Business Support Officer | GSM: 21981135055
- ELAINE CAMPOS MANHAES | Mat: 8024299 | Setor: Customer Relations | GSM: 81131622
- RAVINE NAIRA BASTOS DE CASTRO | Mat: 8080858 | Setor: Business Support Officer | GSM: 21981136174
- Barbara Silva Guimarães | Mat: 8010938 | Setor: Compliance | GSM: 21981130380
- CARLOS JORGE NASCIMENTO SANTOS | Mat: 8019545 | Setor: PRESIDÊNCIA | GSM: 2181131403
- RENATA EVANGELISTA DE CASTRO | Mat: 8008372 | Setor: CHIEF TECHNOLOGY INFORMATION OFFICER | GSM: 2181130215
- CRISTINA LOPES CARRETTI | Mat: 8016707 | Setor: RESIDENTIAL SOLUTIONS | GSM: 005521981130326
- LUCIANA LUCENA VALENTE DE LIMA | Mat: 8055439 | Setor: ADVERTISING, MEDIA & BRAND MANAGEMENT | GSM: 021981132588
- RACHEL DA ROCHA AMARAL | Mat: 8075667 | Setor: STRATEGY & TRANSFORMATION | GSM: 21981130635
- CHAELLY GRANJA FONSECA | Mat: 8027251 | Setor: CTIO Operations | GSM: 21981131015
- MARCELA PINTO FROES | Mat: 8009659 | Setor: VIP | GSM: Não informado
- ALINE NOGUEIRA BORGES | Mat: 8033374 | Setor: RH | GSM: 21981136088
- INGRID REBELO CAROBA DA SILVA | Mat: 8075024 | Setor: Investor Relations | GSM: 21981131008
- ROSANA ZELIA DOS SANTOS XAVIER | Mat: 8017605 | Setor: Wholesale | GSM: +5521981131176
- ANA CRISTINA MENEZES OLIVEIRA | Mat: 8079097 | Setor: PRESIDÊNCIA | GSM: 11999999999
- Milena Da Silva Cristiane | Mat: 8082013 | Setor: Regional Sales Support SP | GSM: +5511981131477
- FABIANA BARROS DA SILVA | Mat: 8081123 | Setor: THD - MKT | GSM: 21981130458
- Natsha Silveira Asfora | Mat: F8030499 | Setor: Residential Solutions | GSM: +5521981131552
- Thayane Alves De Mesquita | Mat: F8085326 | Setor: Investor Relations | GSM: +5521981132987
- BRUNO EZEQUIEL MORAES DE VASCONCELLOS | Mat: 8070775 | Setor: Sales Consumer & SMB SP | GSM: 21981130008
- Marcos Andre Dos Santos Simoes | Mat: F8082942 | Setor: VIP | GSM: 9811305400
- Jane Donadio | Mat: F8009732 | Setor: Corporate Solutions | GSM: +5511981131870
- TAMIRES SOUSA MARTINS | Mat: F8086557 | Setor: Regional Sales Support SP | GSM: +5511981134142
"""

# ==========================================
# 2. REGRA CORPORATIVA SIMPLIFICADA
# ==========================================
REGRA_CORPORATIVO = """Você é um analista de Service Desk N2.
Gere SEMPRE a ABERTURA e o FECHAMENTO usando estritamente o template abaixo:

*** NOTA DE ABERTURA ***
Descrição: [TÍTULO CURTO EM MAIÚSCULAS]
Qtde usuários afetados: 1
Testes efetuados: Sim
Equipamento TIM ou Empresa terceira: Equipamento TIM
Usuário: [NOME DA ENTRADA]
Matrícula: [MATRÍCULA DA ENTRADA]
GSM: Não informado
Site: CEO
Localidade: RIO DE JANEIRO

*** NOTA DE FECHAMENTO ***
Sintomas: [Sintoma da falha relatado pelo usuário]
Análise / Diagnóstico: [Diagnóstico técnico resumido]
Ação (es) executada (s): [Solução corretiva aplicada resumida]
Resultado Obtido: [resultado obtido após a ação]

REGRA DE MÚLTIPLOS CHAMADOS E PROBLEMAS:
1. Se houver dados de múltiplos usuários na mesma requisição, gere combos separados para cada pessoa.
2. SEPARADORES DE CHAMADOS: Preste MUITA atenção ao texto. Problemas listados separados por VÍRGULA (",") ou pela letra "e" indicam chamados COMPLETAMENTE DIFERENTES. 
(Exemplo: "impressora, wifi e sap" = 3 problemas = 3 combos independentes).
3. ATENÇÃO MÁXIMA: Você é OBRIGADO a gerar 1 combo (Abertura + Fechamento) exclusivo para CADA problema identificado. NUNCA misture dois problemas no mesmo ticket e NUNCA omita nenhuma solicitação.
4. Separe TODOS os combos gerados com a linha exata abaixo:
--------------------------------------------------
"""

# ==========================================
# 3. REGRA VIP SIMPLIFICADA
# ==========================================
REGRA_VIP = f"""Você é Service Desk N2 atendendo DIRETORIA/VIP.
Busque os dados do usuário no BANCO DE DADOS abaixo. Se não achar, use os da entrada.
{BANCO_DE_DADOS_VIP}

Gere SEMPRE a ABERTURA e o FECHAMENTO usando estritamente o template abaixo:

*** NOTA DE ABERTURA VIP ***
Descrição: USUÁRIO SOLICITA AUXÍLIO PARA [RESUMO DA FALHA EM MAIÚSCULAS]
Qtde usuários afetados: 1
Testes efetuados: Sim
Equipamento TIM ou Empresa terceira: Equipamento TIM 
Usuário: [NOME DO BANCO DE DADOS]
Matrícula: [MATRÍCULA DO BANCO DE DADOS]
GSM: [GSM DO BANCO DE DADOS]
Ramal: Não tem no XTTS
Setor: [SETOR DO BANCO DE DADOS]
Site: CEO
Localidade: RIO DE JANEIRO

*** FECHAMENTO VIP / DIRETORIA ***
Sintomas: [Sintoma da falha relatado pelo usuário]
Análise / Diagnóstico: [Diagnóstico técnico resumido]
Ação (es) executada (s): [Solução corretiva aplicada resumida]
Resultado Obtido: [resultado obtido após a ação]

REGRA DE MÚLTIPLOS CHAMADOS E PROBLEMAS:
1. Se houver dados de múltiplos usuários na mesma requisição, gere combos separados para cada pessoa.
2. SEPARADORES DE CHAMADOS: Preste MUITA atenção ao texto. Problemas listados separados por VÍRGULA (",") ou pela letra "e" indicam chamados COMPLETAMENTE DIFERENTES. 
(Exemplo: "outlook, mfa e calendário" = 3 problemas = 3 combos independentes).
3. ATENÇÃO MÁXIMA: Você é OBRIGADO a gerar 1 combo (Abertura + Fechamento) exclusivo para CADA problema identificado. NUNCA misture dois problemas no mesmo ticket e NUNCA omita nenhuma solicitação.
4. Separe TODOS os combos gerados com a linha exata abaixo:
--------------------------------------------------
"""

# ==========================================
# 4. CONFIGURAÇÃO DA API FASTAPI
# ==========================================
app = FastAPI(title="CS Desk AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"status": "Online"}

class ChamadoUnico(BaseModel):
    nome: str
    matricula: str
    falhas: str

class LoteChamados(BaseModel):
    tipo: str 
    chamados: List[ChamadoUnico]

@app.post("/gerar-ticket")
def gerar_ticket_api(lote: LoteChamados):
    try:
        if lote.tipo == "vip":
            regra_escolhida = REGRA_VIP
        else:
            regra_escolhida = REGRA_CORPORATIVO

        configuracao = types.GenerateContentConfig(
            system_instruction=regra_escolhida,
            temperature=0.1
        )

        input_ia = "Processe o texto abaixo gerando o Combo (Abertura + Fechamento):\n"
        for item in lote.chamados:
            input_ia += f"- Nome: {item.nome}, Matrícula: {item.matricula}, Contexto (Falhas/Problemas): {item.falhas}\n"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=input_ia,
            config=configuracao
        )
        
        texto_limpo = response.text.replace("```text\n", "").replace("```text", "").replace("```", "").strip()
        return {"sucesso": True, "ticket": texto_limpo}
    
    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        return {"sucesso": False, "erro": str(e)}