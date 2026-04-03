import google.generativeai as genai
import streamlit as st

def init_chatbot():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "search_context" not in st.session_state:
        st.session_state.search_context = ""

def update_search_context(results: list[dict]):
    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(
            f"Résultat {i}:\n"
            f"  - Source: {r.get('url', 'N/A')}\n"
            f"  - Bourse: {r.get('scholarship', 'N/A')}\n"
            f"  - Montant: {r.get('montant', 'N/A')}\n"
            f"  - Coût scolarité: {r.get('cout_annuel', 'N/A')}\n"
            f"  - Détails: {r.get('details', 'N/A')}\n"
        )
    st.session_state.search_context = "\n".join(context_parts)

def get_chatbot_response(user_message: str) -> str:
    # Récupération directe depuis les secrets
    api_key = st.secrets.get("Gemini_API_Key")
    
    if not api_key:
        return "❌ Erreur : La clé 'Gemini_API_Key' n'est pas configurée dans les Secrets Streamlit."

    try:
        genai.configure(api_key=api_key)
        # Modèle haute capacité (1500 req/jour)
        model = genai.GenerativeModel("gemini-flash-lite-latest")

        system_prompt = (
            "Tu es un assistant expert en bourses d'études. "
            "Réponds en français de manière claire. "
            "Utilise le contexte suivant si disponible pour aider l'utilisateur :\n\n"
        )

        context = st.session_state.get("search_context", "")
        full_prompt = system_prompt + context + "\nQuestion: " + user_message

        response = model.generate_content(full_prompt)
        answer = response.text

        st.session_state.chat_history.append({"role": "user", "content": user_message})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        return answer
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"

def render_chatbot():
    """Affiche l'interface du chatbot sans demander de clé."""
    init_chatbot()
    st.markdown("---")
    st.subheader("🤖 Assistant IA")

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Posez votre question sur les bourses ou les résultats...")
    if user_input:
        st.chat_message("user").write(user_input)
        response = get_chatbot_response(user_input)
        st.chat_message("assistant").write(response)