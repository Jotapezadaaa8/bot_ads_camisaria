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
        
        if any(s in t for s in ["obrigado", "obg", "tchau", "valeu", "encerrar", "obrigada"]):
            self.resetar_sessao()
            return "😊 De nada! A Adis Camisaria agradece o contato. Tenha um excelente dia!"

        # Captura de números e o texto para identificar qual quantidade pertence a qual produto
        numeros = [int(s) for s in t.split() if s.isdigit()]
        total_solicitado = sum(numeros)

        if self.memoria == "aguardando_quantidade" and numeros:
            if total_solicitado < 100:
                return f"⚠️ O total informado ({total_solicitado} peças) é inferior ao mínimo de 100 peças para atacado. Deseja ajustar a quantidade?"
            
            disponiveis = []
            insuficiente = []
            
            # Lógica de separação inteligente por item individual mencionado no texto
            for p in self.produtos_sessao:
                nome_curto = p.replace("camisa ", "").replace("camiseta ", "")
                # Tenta achar a quantidade específica para aquele produto no texto (ex: "100 linho")
                encontrou_especifico = False
                for palavra in t.split():
                    if nome_curto in palavra or p in t:
                        # Se achou o nome do produto, busca o número mais próximo no texto
                        for n in numeros:
                            if str(n) in t:
                                qtd_item = n
                                if self.PRODUTOS[p]['estoque_atacado'] >= qtd_item and self.PRODUTOS[p]['estoque_atacado'] >= 100:
                                    disponiveis.append(p.title())
                                else:
                                    insuficiente.append(p.title())
                                encontrou_especifico = True
                                break
                    if encontrou_especifico: break
                
                # Caso o cliente digite apenas um número (ex: "200"), valida contra o total
                if not encontrou_especifico:
                    if self.PRODUTOS[p]['estoque_atacado'] >= total_solicitado and self.PRODUTOS[p]['estoque_atacado'] >= 100:
                        disponiveis.append(p.title())
                    else:
                        insuficiente.append(p.title())

            # Remove duplicatas das listas
            disponiveis = list(set(disponiveis))
            insuficiente = list(set(insuficiente))

            if insuficiente:
                self.memoria = "aguardando_confirmacao_encomenda"
                msg_retorno = ""
                if disponiveis:
                    msg_retorno += f"✅ Para o modelo ({', '.join(disponiveis)}), temos estoque disponível para envio imediato!\n\n"
                
                msg_retorno += (f"⚠️ Porém, a quantidade em estoque para o modelo ({', '.join(insuficiente)}) é abaixo do necessário para pronta-entrega em atacado.\n\n"
                                f"Indicamos fazer a parte deste modelo por **encomenda**! Mantemos o preço de atacado e produzimos em até 15 dias. Deseja seguir com os itens disponíveis e encomendar o restante?")
                return msg_retorno

            self.memoria = "aguardando_grade"
            return f"✅ **{total_solicitado} peças** registradas com sucesso! Agora, por favor, me informe a **grade** desejada em apenas 1 mensagem (tamanhos e cores)."

        if self.memoria == "aguardando_confirmacao_encomenda":
            if any(s in t for s in ["sim", "quero", "pode", "ok", "aceito", "com certeza"]):
                self.memoria = "aguardando_grade"
                return "✅ Perfeito! Excelente escolha. Agora, por favor, me informe a **grade** desejada de todo o pedido em apenas 1 mensagem (especificando tamanhos e cores)."
            else:
                self.resetar_sessao()
                return "Sem problemas! Caso queira ajustar o pedido ou consultar outro modelo pronto para entrega, basta digitar 'Menu'."

        if self.memoria == "aguardando_grade":
            self.memoria = None
            return "📝 Recebido! Enviamos sua solicitação com a grade ao nosso setor comercial, em breve o senhor(a) receberá um e-mail com a confirmação do pedido. Mais alguma dúvida?"

        if "1" in t or "reposição" in t: 
            self.memoria = "1"
            if t in ["1", "reposição"]: self.produtos_sessao = []
        elif "2" in t or "especificação" in t: self.memoria = "2"
        elif "3" in t or "atacado" in t: self.memoria = "3"
        elif "4" in t or "qualidade" in t: self.memoria = "4"
        elif "5" in t or "preço" in t: self.memoria = "5"

        t_limpo = f" {t} ".replace(" de ", " ").replace(" da ", " ").replace(" do ", " ")
        encontrados = []
        if "linho" in t_limpo: encontrados.append("camisa linho")
        if "polo" in t_limpo: encontrados.append("camisa polo")
        if "regata" in t_limpo: encontrados.append("regata")
        if "basica" in t_limpo or "básica" in t_limpo: encontrados.append("camiseta basica")
            
        if encontrados:
            self.produtos_sessao = encontrados 
            self.erros_seguidos = 0

        if any(s in t for s in ["oi", "olá", "bom dia", "menu", "ajuda", "valeu", "cole", "coe", "fala"]):
            self.resetar_sessao()
            return ("👋 Olá! Sou o assistente da Adis Camisaria.\n\n"
                    "1️⃣ **Reposição** | 2️⃣ **Especificações** | 3️⃣ **Atacado** | 4️⃣ **Qualidade** | 5️⃣ **Preços**")

        if self.memoria == "1":
            if self.produtos_sessao:
                res = [f"{'✅' if self.PRODUTOS[p]['previsao'].lower() == 'disponível' else '📅'} **{p.title()}**: {self.PRODUTOS[p]['previsao']}" for p in self.produtos_sessao]
                return "Sobre a reposição solicitada:\n\n" + "\n".join(res)
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
                return (f"📦 Estoque para atacado:\n\n" + "\n".join(res) + 
                        "\n\nQual a **quantidade total** que você deseja? (Mínimo de 100 peças).")
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

        self.erros_seguidos += 1
        return "🛠️ Transferindo para um **atendente humano**... 🧑‍💻" if self.erros_seguidos >= 2 else "🤔 Não entendi. Poderia repetir ou escolher uma opção?"

    def resetar_sessao(self):
        self.memoria, self.produtos_sessao, self.erros_seguidos = None, [], 0

# Interface Streamlit
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
