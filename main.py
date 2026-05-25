import streamlit as st

# 1. CLASSE DO BOT COM INTELIGÊNCIA INTEGRADA
class AdsBot:
    def __init__(self):
        self.PRODUTOS = {
            "camisa polo": {
                "previsao": "15/06/2026",
                "specs": "Algodão Pima com elastano, gola estruturada.",
                "estoque_atacado": 150, 
                "qualidade": "Alta durabilidade e toque sedoso premium.", 
                "preco": "R$ 89,90"
            },
            "regata": {
                "previsao": "Disponível",
                "specs": "Tecido Dry Fit esportivo com proteção UV.",
                "estoque_atacado": 200, 
                "qualidade": "Fabricada em tecido Dry Fit esportivo de alta performance com proteção UV integrada. Possui tecnologia avançada de secagem rápida, ideal para atividades físicas intensas.", 
                "preco": "R$ 39,90"
            },
            "camisa linho": {
                "previsao": "05/07/2026",
                "specs": "Linho Puro com corte alfaiataria slim.",
                "estoque_atacado": 20, 
                "qualidade": "Linho premium de origem sustentável.", 
                "preco": "R$ 159,00"
            },
            "camiseta basica": {
                "previsao": "Disponível",
                "specs": "100% Algodão 30.1 penteado.",
                "estoque_atacado": 500, 
                "qualidade": "Não encolhe e possui costuras reforçadas.", 
                "preco": "R$ 45,00"
            }
        }
        
        # Variações para busca robusta
        self.VARIACOES = {
            "camisa polo": ["polo", "gola polo", "camisa polo", "camisaria polo"],
            "regata": ["regata", "regatas", "camisa regata", "camiseta regata", "dry fit"],
            "camisa linho": ["linho", "camisa de linho", "camisa linho", "linhos"],
            "camiseta basica": ["basica", "básica", "camiseta basica", "camiseta básica", "tshirt", "t-shirt", "algodao"]
        }

        self.memoria = None
        self.produtos_sessao = []
        self.erros_seguidos = 0
        # Texto auxiliar para as sugestões
        self.OPCOES_DISPONIVEIS = "\n" + "\n".join([f"• {p.title()}" for p in self.PRODUTOS.keys()])

    def responder(self, mensagem: str) -> str:
        t = mensagem.lower().strip()
        
        if any(s in t for s in ["obrigado", "obg", "tchau", "valeu", "encerrar", "obrigada"]):
            self.resetar_sessao()
            return "😊 De nada! A Adis Camisaria agradece o contato. Tenha um excelente dia!"

        numeros = [int(s) for s in t.split() if s.isdigit()]
        total_solicitado = sum(numeros)

        # Lógica de Atacado (Quantidade/Grade)
        if self.memoria == "aguardando_quantidade" and numeros:
            if total_solicitado < 100:
                return f"⚠️ O total informado ({total_solicitado} peças) é inferior ao mínimo de 100 peças para atacado. Deseja ajustar a quantidade?"
            
            disponiveis, insuficiente = [], []
            for p in self.produtos_sessao:
                if self.PRODUTOS[p]['estoque_atacado'] >= total_solicitado:
                    disponiveis.append(p.title())
                else:
                    insuficiente.append(p.title())

            if insuficiente:
                self.memoria = "aguardando_confirmacao_encomenda"
                msg = f"✅ Disponível: {', '.join(disponiveis)}\n\n" if disponiveis else ""
                msg += f"⚠️ O modelo ({', '.join(insuficiente)}) exige **encomenda** (15 dias) para esta quantidade. Deseja seguir?"
                return msg

            self.memoria = "aguardando_grade"
            return f"✅ **{total_solicitado} peças** registradas! Informe a **grade** (tamanhos e cores) em uma mensagem."

        if self.memoria == "aguardando_confirmacao_encomenda":
            if any(s in t for s in ["sim", "quero", "pode", "ok", "aceito"]):
                self.memoria = "aguardando_grade"
                return "✅ Ótimo! Informe a **grade** desejada para prosseguirmos."
            self.resetar_sessao()
            return "Sem problemas! Digite 'Menu' para recomeçar."

        if self.memoria == "aguardando_grade":
            self.memoria = None
            return "📝 Recebido! Nosso comercial entrará em contato por e-mail em breve. Mais alguma dúvida?"

        # 1. Verifica se o usuário escolheu uma opção do menu
        opcoes_menu = {
            "1": "1", "reposição": "1", "reposicao": "1",
            "2": "2", "especificação": "2", "especificacao": "2",
            "3": "3", "atacado": "3",
            "4": "4", "qualidade": "4",
            "5": "5", "preço": "5", "preco": "5"
        }
        
        nova_opcao = None
        for chave, valor in opcoes_menu.items():
            if chave == t or f" {chave} " in f" {t} ":
                nova_opcao = valor
                break
        
        if nova_opcao:
            self.memoria = nova_opcao

        # 2. Busca de produtos
        encontrados = []
        for modelo, variacoes in self.VARIACOES.items():
            if any(v in t for v in variacoes):
                encontrados.append(modelo)
        
        if not encontrados and not nova_opcao and not any(s in t for s in ["oi", "menu"]):
             self.produtos_sessao = []
        elif encontrados:
            self.produtos_sessao = encontrados
            self.erros_seguidos = 0

        # Saudação / Menu
        if any(s in t for s in ["oi", "olá", "bom dia", "menu", "ajuda", "boa tarde", "boa noite"]):
            self.resetar_sessao()
            return ("👋 Olá! Sou o assistente da Adis Camisaria.\n\n"
                    "1️⃣ **Reposição** | 2️⃣ **Especificações** | 3️⃣ **Atacado** | 4️⃣ **Qualidade** | 5️⃣ **Preços**")

        # Respostas Baseadas na Memória com as novas tratativas de erro de modelo
        if self.memoria == "1":
            if self.produtos_sessao:
                res = [f"{'✅' if self.PRODUTOS[p]['previsao'].lower() == 'disponível' else '📅'} **{p.title()}**: {self.PRODUTOS[p]['previsao']}" for p in self.produtos_sessao]
                return "Sobre a reposição:\n\n" + "\n".join(res)
            return f"🔍 Não trabalhamos com esse modelo. Por favor, escolha um dos nossos produtos disponíveis:{self.OPCOES_DISPONIVEIS}"

        if self.memoria == "2":
            if self.produtos_sessao:
                res = [f"📋 **{p.title()}**: {self.PRODUTOS[p]['specs']}" for p in self.produtos_sessao]
                return "Especificações técnicas:\n\n" + "\n".join(res)
            return f"📋 Infelizmente não temos esse modelo em nosso catálogo. Tente um destes:{self.OPCOES_DISPONIVEIS}"

        if self.memoria == "3":
            if self.produtos_sessao:
                res = [f"• **{p.title()}**: {self.PRODUTOS[p]['estoque_atacado']} em estoque." for p in self.produtos_sessao]
                self.memoria = "aguardando_quantidade"
                return "📦 Estoque Atacado:\n\n" + "\n".join(res) + "\n\nQual a **quantidade total**?"
            return f"📦 Esse item não está disponível para atacado. Trabalhamos com:{self.OPCOES_DISPONIVEIS}"

        if self.memoria == "4":
            if self.produtos_sessao:
                res = [f"✨ **{p.title()}**: {self.PRODUTOS[p]['qualidade']}" for p in self.produtos_sessao]
                return "Qualidade:\n\n" + "\n".join(res)
            return f"✨ Não trabalhamos com esse modelo. Conheça a qualidade dos nossos itens ativos:{self.OPCOES_DISPONIVEIS}"

        if self.memoria == "5":
            if self.produtos_sessao:
                res = [f"💰 **{p.title()}**: {self.PRODUTOS[p]['preco']}" for p in self.produtos_sessao]
                return "Valores atuais:\n\n" + "\n".join(res)
            return f"💰 Não trabalhamos com este modelo, por isso não temos um preço definido. Sugerimos consultar um de nossos modelos:{self.OPCOES_DISPONIVEIS}"

        self.erros_seguidos += 1
        return "🛠️ Transferindo para um atendente..." if self.erros_seguidos >= 2 else "🤔 Não entendi. Pode repetir ou escolher uma opção?"

    def resetar_sessao(self):
        self.memoria, self.produtos_sessao, self.erros_seguidos = None, [], 0

# Streamlit
st.set_page_config(page_title="ADS Camisaria", page_icon="👕")
st.title("👕 ADS Camisaria - Atendimento")
if "bot" not in st.session_state: st.session_state.bot = AdsBot()
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])
if prompt := st.chat_input("Diga o que você precisa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    resposta = st.session_state.bot.responder(prompt)
    st.session_state.messages.append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"): st.markdown(resposta)
