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
                "qualidade": "Fabricada em tecido Dry Fit esportivo de alta performance com proteção UV integrada.", 
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
        
        self.VARIACOES = {
            "camisa polo": ["polo", "gola polo", "camisa polo", "camisaria polo"],
            "regata": ["regata", "regatas", "camisa regata", "camiseta regata", "dry fit"],
            "camisa linho": ["linho", "camisa de linho", "camisa linho", "linhos"],
            "camiseta basica": ["basica", "básica", "camiseta basica", "camiseta básica", "tshirt", "t-shirt", "algodao"]
        }

        self.memoria = None
        self.produtos_sessao = []
        self.erros_seguidos = 0

    def responder(self, mensagem: str) -> str:
        t = mensagem.lower().strip()
        
        if any(s in t for s in ["obrigado", "obg", "tchau", "valeu", "encerrar", "obrigada"]):
            self.resetar_sessao()
            return "😊 De nada! A Adis Camisaria agradece o contato. Tenha um excelente dia!"

        numeros = [int(s) for s in t.split() if s.isdigit()]
        total_solicitado = sum(numeros)

        # --- LÓGICA DE ATACADO CORRIGIDA (QUANTIDADE/ESTOQUE) ---
        if self.memoria == "aguardando_quantidade" and numeros:
            if total_solicitado < 100:
                return f"⚠️ O total informado ({total_solicitado} peças) é inferior ao mínimo de 100 peças para atacado. Deseja ajustar a quantidade?"
            
            disponiveis = []
            insuficiente = []
            quantidades_por_produto = {}
            
            if len(numeros) == len(self.produtos_sessao):
                for i, p in enumerate(self.produtos_sessao):
                    quantidades_por_produto[p] = numeros[i]
            else:
                por_item = total_solicitado / len(self.produtos_sessao)
                for p in self.produtos_sessao:
                    quantidades_por_produto[p] = por_item

            for p in self.produtos_sessao:
                qtd_vontade = quantidades_por_produto[p]
                if self.PRODUTOS[p]['estoque_atacado'] >= qtd_vontade:
                    disponiveis.append(f"• **{p.title()}**: {int(qtd_vontade)} peças (Pronta Entrega)")
                else:
                    insuficiente.append(f"• **{p.title()}**: {int(qtd_vontade)} peças (Encomenda 15 dias)")

            if insuficiente:
                self.memoria = "aguardando_confirmacao_encomenda"
                msg = "📋 **Análise do seu pedido de Atacado:**\n\n"
                if disponiveis:
                    msg += "✅ **Disponível em Estoque:**\n" + "\n".join(disponiveis) + "\n\n"
                msg += "⚠️ **Necessita Encomenda:**\n" + "\n".join(insuficiente) + "\n\n"
                msg += "Deseja seguir com o pedido nestas condições?"
                return msg

            self.memoria = "aguardando_grade"
            return f"✅ **{total_solicitado} peças** registradas! Tudo disponível em estoque. Informe a **grade** (tamanhos e cores)."

        # --- FLUXO DE CONFIRMAÇÃO ---
        if self.memoria == "aguardando_confirmacao_encomenda":
            if any(s in t for s in ["sim", "quero", "pode", "ok", "aceito"]):
                self.memoria = "aguardando_grade"
                return "✅ Ótimo! Informe a **grade** desejada para prosseguirmos."
            self.resetar_sessao()
            return "Sem problemas! Digite 'Menu' para recomeçar."

        if self.memoria == "aguardando_grade":
            self.memoria = None
            return "📝 Recebido! Nosso comercial entrará em contato por e-mail em breve. Mais alguma dúvida?"

        # --- MENU E IDENTIFICAÇÃO ---
        opcoes_menu = {"1": "1", "2": "2", "3": "3", "4": "4", "5": "5"}
        nova_opcao = None
        for chave in opcoes_menu:
            if chave == t or f" {chave} " in f" {t} ":
                nova_opcao = opcoes_menu[chave]
                break
        
        if nova_opcao: self.memoria = nova_opcao

        encontrados = []
        for modelo, variacoes in self.VARIACOES.items():
            if any(v in t for v in variacoes):
                encontrados.append(modelo)
        
        # --- FILTRO DE NICHO (RESPOSTA IMEDIATA PARA ITENS FORA DE LINHA) ---
        if not encontrados and not nova_opcao and not any(s in t for s in ["oi", "olá", "menu", "ajuda"]):
            # Caso contenha palavras de esporte/outros times ou o item não esteja no catálogo
            return ("🚫 A Adis Camisaria é especialista em **Alfaiataria Premium**.\n\n"
                    "Não trabalhamos com essa linha de produtos (como artigos esportivos ou casuais fora do catálogo). "
                    "Que tal conferir nossas **Camisas de Linho** ou **Polos Pima**? São nossas especialidades.")

        if encontrados:
            self.produtos_sessao = encontrados
            self.erros_seguidos = 0
        elif not nova_opcao and not any(s in t for s in ["oi", "menu", "ajuda"]):
            if self.memoria not in ["1","2","3","4","5"]: self.produtos_sessao = []

        if any(s in t for s in ["oi", "olá", "menu", "ajuda"]):
            self.resetar_sessao()
            return ("👋 Olá! Sou o assistente da Adis Camisaria.\n\n"
                    "1️⃣ **Reposição** | 2️⃣ **Especificações** | 3️⃣ **Atacado** | 4️⃣ **Qualidade** | 5️⃣ **Preços**")

        # --- RESPOSTAS POR CATEGORIA ---
        if self.memoria == "1":
            if self.produtos_sessao:
                res = [f"{'✅' if self.PRODUTOS[p]['previsao'].lower() == 'disponível' else '📅'} **{p.title()}**: {self.PRODUTOS[p]['previsao']}" for p in self.produtos_sessao]
                return "Sobre a reposição:\n\n" + "\n".join(res)
            return "🔍 De qual modelo você deseja saber a reposição?"

        if self.memoria == "2":
            if self.produtos_sessao:
                res = [f"📋 **{p.title()}**: {self.PRODUTOS[p]['specs']}" for p in self.produtos_sessao]
                return "Especificações técnicas:\n\n" + "\n".join(res)
            return "📋 Qual peça você quer ver as especificações?"

        if self.memoria == "3":
            if self.produtos_sessao:
                res = [f"• **{p.title()}**: {self.PRODUTOS[p]['estoque_atacado']} em estoque." for p in self.produtos_sessao]
                self.memoria = "aguardando_quantidade"
                return "📦 Estoque Atacado:\n\n" + "\n".join(res) + "\n\nQual a **quantidade total**?"
            return "📦 Para atacado, qual modelo você deseja consultar?"

        if self.memoria == "4":
            if self.produtos_sessao:
                res = [f"✨ **{p.title()}**: {self.PRODUTOS[p]['qualidade']}" for p in self.produtos_sessao]
                return "Qualidade:\n\n" + "\n".join(res)
            return "✨ De qual modelo você quer conhecer a qualidade?"

        if self.memoria == "5":
            if self.produtos_sessao:
                res = [f"💰 **{p.title()}**: {self.PRODUTOS[p]['preco']}" for p in self.produtos_sessao]
                return "Valores atuais:\n\n" + "\n".join(res)
            return "💰 Qual produto você deseja consultar o preço?"

        self.erros_seguidos += 1
        return "🛠️ Transferindo para um atendente..." if self.erros_seguidos >= 2 else "🤔 Não entendi. Pode repetir ou escolher uma opção?"

    def resetar_sessao(self):
        self.memoria, self.produtos_sessao, self.erros_seguidos = None, [], 0

# Streamlit App
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
