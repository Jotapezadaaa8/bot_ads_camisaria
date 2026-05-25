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

        # INTERCEPCAO CRÍTICA: Processamento unificado para múltiplos modelos e verificação de estoque
        if self.memoria == "aguardando_quantidade" and numeros:
            if total_solicitado < 100:
                return f"⚠️ O total informado ({total_solicitado} peças) é inferior ao mínimo de 100 peças para atacado. Deseja ajustar a quantidade?"
            
            # Validação inteligente de estoque baixo/insuficiente para atacado
            insuficiente = [p for p in self.produtos_sessao if total_solicitado > self.PRODUTOS[p]['estoque_atacado'] or self.PRODUTOS[p]['estoque_atacado'] < 100]
            
            if insuficiente:
                self.memoria = "aguardando_confirmacao_encomenda"
                nomes_produtos = ", ".join([p.title() for p in insuficiente])
                return (f"⚠️ Infelizmente, a quantidade em estoque para o modelo ({nomes_produtos}) é abaixo do necessário para pronta-entrega em atacado.\n\n"
                        f"Porém, indicamos fazer por **encomenda**! Mantemos o mesmo preço de atacado e produzimos tudo em até 15 dias. Deseja fechar seu pedido por encomenda?")

            self.memoria = "aguardando_grade"
            return f"✅ **{total_solicitado} peças** registradas com sucesso! Agora, por favor, me informe a **grade** desejada em apenas 1 mensagem (tamanhos e cores)."

        # LÓGICA COMPLEMENTAR DA ENCOMENDA
        if self.memoria == "aguardando_confirmacao_encomenda":
            if any(s in t for s in ["sim", "quero", "pode", "ok", "aceito", "com certeza"]):
                self.memoria = "aguardando_grade"
                return "✅ Perfeito! Excelente escolha. Agora, por favor, me informe a **grade** desejada para a encomenda em apenas 1 mensagem (tamanhos e cores)."
            else:
                self.resetar_sessao()
                return "Sem problemas! Caso queira consultar outro modelo disponível para pronta-entrega, basta digitar 'Menu' ou escolher uma opção."

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

        # 4. CAPTURA DE PRODUTOS (Tratamento preciso de substring e remoção de conectivos)
        t_limpo = f" {t} ".replace(" de ", " ").replace(" da ", " ").replace(" do ", " ")
        encontrados = []
        
        # Garante casamento exato das chaves do dicionário
        if "linho" in t_limpo:
            encontrados.append("camisa linho")
        if "polo" in t_limpo:
            encontrados.append("camisa polo")
        if "regata" in t_limpo:
            encontrados.append("regata")
        if "basica" in t_limpo or "básica" in t_limpo:
            encontrados.append("camiseta basica")
            
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
                res = []
                for p in self.produtos_sessao:
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
                res = [f"• **{p.title()}**: {self.PRODUTOS[p]['estoque_atacado']} em estoque." for p in self.produtos_sessao]
                self.memoria = "aguardando_quantidade"
                return (f"📦 Estoque para atacado:\n\n" + "\n".join(res) + 
                        "\n\nQual a **quantidade total** que você deseja? (Mínimo de 100 peças. Ex: *Quero 100 polo e 100 regata* ou apenas *200*)")
            return "📦 Para atacado, qual modelo você deseja consultar?"

        if self.memoria == "4":
            if self.produtos_sessao:
                res = [f"✨ **{p.title()}**: {self.PRODUTOS[p]['qualidade']}" for p in self.produtos_sessao]
                return "Qualidade do produto:\n\n" + "\n".join(res)
            return "✨ De qual modelo você quer conhecer a qualidade?"

        if self.memoria == "5":
            if self.produtos_sessao:
                res = [f"💰 **{p.title()}**: {self.PRODUTOS[p]['preco']}" for p in self.produtos_sessao]
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
