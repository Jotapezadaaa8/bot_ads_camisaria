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
            "polo": {
                "previsao": "15/06/2026",
                "specs": "Algodão Pima com elastano, gola estruturada.",
                "estoque_atacado": 150, 
                "qualidade": "Produzida com Algodão Pima legítimo.", 
                "preco": "R$ 89,90"
            },
            "regata": {
                "previsao": "Disponível",
                "specs": "Tecido Dry Fit esportivo com proteção UV.",
                "estoque_atacado": 200, 
                "qualidade": "Fabricada em tecido Dry Fit esportivo de alta performance com proteção UV integrada.Possui tecnologia avançada de secagem rápida, ideal para atividades físicas intensas.", 
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
        self.memoria = None
        self.produtos_sessao = []
        self.erros_seguidos = 0

    def responder(self, mensagem: str) -> str:
        t = mensagem.lower().strip()
        
        # 1. ENCERRAMENTO
        if any(s in t for s in ["obrigado", "obg", "tchau", "valeu", "encerrar", "obrigada"]):
            self.resetar_sessao()
            return "😊 De nada! A Adis Camisaria agradece o contato. Tenha um excelente dia!"

        # 2. CAPTURA DE NÚMEROS ISOLADOS (SOMA PARA MULTIPLOS MODELOS)
        numeros = [int(s) for s in t.split() if s.isdigit()]
        total_solicitado = sum(numeros)

        # INTERCEPCAO CRÍTICA: Lógica de Atacado / Encomenda
        if self.memoria == "aguardando_quantidade" and numeros:
            if total_solicitado < 100:
                return f"⚠️ O total informado ({total_solicitado} peças) é inferior ao mínimo de 100 peças para atacado. Deseja ajustar a quantidade?"
            
            # Verifica se há estoque para todos os produtos selecionados
            estoque_insuficiente = False
            for p in self.produtos_sessao:
                if total_solicitado > self.PRODUTOS[p]['estoque_atacado']:
                    estoque_insuficiente = True
                    break
            
            if estoque_insuficiente:
                self.memoria = "aguardando_confirmacao_encomenda"
                return (f"📦 Notei que o total de **{total_solicitado} peças** excede nosso estoque pronta-entrega para alguns modelos.\n\n"
                        "Podemos seguir via **encomenda**! O prazo de produção é de 15 dias, mantendo o valor de atacado. Podemos registrar seu pedido assim?")

        if self.memoria == "aguardando_confirmacao_encomenda":
            if any(s in t for s in ["sim", "pode", "ok", "quero", "aceito"]):
                self.memoria = "aguardando_grade"
                return "✅ Ótima escolha! Pedido por encomenda pré-aprovado. Agora, por favor, me informe a **grade** desejada (tamanhos e cores)."
            else:
                self.resetar_sessao()
                return "Entendido. Caso mude de ideia ou queira outros modelos pronta-entrega, basta chamar no menu!"

        if self.memoria == "aguardando_grade":
            self.memoria = None
            return "📝 Recebido! Enviamos sua solicitação com a grade ao nosso setor comercial, em breve o senhor(a) receberá um e-mail com a confirmação do pedido. Mais alguma dúvida?"

        # 3. CAPTURA DE INTENÇÃO
        if "1" in t or "reposição" in t: 
            self.memoria = "1"
            if t in ["1", "reposição"]:
                self.produtos_sessao = []
        elif "2" in t or "especificação" in t: self.memoria = "2"
        elif "3" in t or "atacado" in t: self.memoria = "3"
        elif "4" in t or "qualidade" in t: self.memoria = "4"
        elif "5" in t or "preço" in t: self.memoria = "5"

        # 4. CAPTURA DE PRODUTOS
        t_limpo = t.replace(" de ", " ").replace(" da ", " ").replace(" do ", " ")
        encontrados = [p for p in self.PRODUTOS if p in t or p in t_limpo]
        
        if encontrados:
            self.produtos_sessao = encontrados 
            self.erros_seguidos = 0

        # 5. SAUDAÇÃO / MENU
        if any(s in t for s in ["oi", "olá", "bom dia", "menu", "ajuda"]):
            self.resetar_sessao()
            return ("👋 Olá! Sou o assistente da Adis Camisaria.\n\n"
                    "1️⃣ **Reposição** | 2️⃣ **Especificações** | 3️⃣ **Atacado** | 4️⃣ **Qualidade** | 5️⃣ **Preços**")

        # 6. LÓGICA DE RESPOSTA IMEDIATA
        if self.memoria == "1":
            if self.produtos_sessao:
                itens_unicos = list(dict.fromkeys(self.produtos_sessao))
                if "camisa polo" in itens_unicos and "polo" in itens_unicos:
                    itens_unicos.remove("polo")
                
                res = []
                for p in itens_unicos:
                    status = self.PRODUTOS[p]['previsao']
                    if status.lower() == "disponível":
                        msg = f"✅ **{p.title()}**: Atualmente em estoque e disponível para envio imediato!"
                    else:
                        msg = f"📅 **{p.title()}**: A previsão de chegada de novo lote é para o dia **{status}**."
                    res.append(msg)
                
                return "Sobre a reposição solicitada:\n\n" + "\n".join(res)
            return "🔍 De qual modelo você deseja saber a reposição? (Ex: Camisa de Linho, Polo, etc)"

        if self.memoria == "2":
            if self.produtos_sessao:
                res = [f"📋 **{p.title()}**: {self.PRODUTOS[p]['specs']}" for p in self.produtos_sessao]
                return "Especificações técnicas:\n\n" + "\n".join(res)
            return "📋 Qual peça você quer ver as especificações?"

        if self.memoria == "3":
            if self.produtos_sessao:
                itens_unicos = list(dict.fromkeys(self.produtos_sessao))
                if "camisa polo" in itens_unicos and "polo" in itens_unicos:
                    itens_unicos.remove("polo")
                res = [f"• **{p.title()}**: {self.PRODUTOS[p]['estoque_atacado']} em estoque." for p in itens_unicos]
                self.memoria = "aguardando_quantidade"
                return (f"📦 Estoque disponível:\n\n" + "\n".join(res) + 
                        "\n\nQual a **quantidade total** que você deseja? (Mínimo de 100 peças. Ex: *Quero 100 polo e 100 regata* ou apenas *200*)")
            return "📦 Para atacado, qual modelo você deseja consultar?"

        if self.memoria == "4":
            if self.produtos_sessao:
                res = [f"✨ **{p.title()}**: {self.PRODUTOS[p]['qualidade']}" for p in self.produtos_sessao]
                return "Qualidade do produto:\n\n" + "\n".join(res)
            return "✨ De qual modelo você quer conhecer a qualidade?"

        if self.memoria == "5":
            if self.produtos_sessao:
                itens_unicos = list(dict.fromkeys(self.produtos_sessao))
                if "camisa polo" in itens_unicos and "polo" in itens_unicos:
                    itens_unicos.remove("polo")
                res = [f"💰 **{p.title()}**: {self.PRODUTOS[p]['preco']}" for p in itens_unicos]
                return "Valores atuais:\n\n" + "\n".join(res)
            return "💰 Qual produto você deseja consultar o preço?"

        # 7. ERRO E TRANSFERÊNCIA
        self.erros_seguidos += 1
        if self.erros_seguidos >= 2:
            return "🛠️ Transferindo para um **atendente humano**... 🧑‍💻"
        return "🤔 Não entendi. Poderia repetir o produto ou escolher uma opção do menu?"

    def resetar_sessao(self):
        self.memoria = None
        self.produtos_sessao = []
        self.erros_seguidos = 0

# --- Interface Streamlit ---
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