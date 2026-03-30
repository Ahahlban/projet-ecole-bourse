import google.generativeai as genai
import streamlit as st


def init_chatbot():
    """Initialise l'historique du chatbot dans la session Streamlit."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "search_context" not in st.session_state:
        st.session_state.search_context = ""


def update_search_context(results: list[dict]):
    """
    Met à jour le contexte de recherche avec les résultats trouvés.
    Appelé après chaque recherche pour enrichir les réponses du chatbot.

    Args:
        results: Liste de dicts avec clés 'url', 'scholarship', 'montant', 'cout_annuel', 'details'
    """
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


def get_chatbot_response(user_message: str, api_key: str) -> str:
    """
    Génère une réponse du chatbot en utilisant le contexte de recherche.

    Args:
        user_message: La question de l'utilisateur
        api_key: Clé API Google Gemini

    Returns:
        La réponse générée par l'IA
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Construction du prompt avec contexte RAG
        system_prompt = (
            "Tu es un assistant expert en bourses d'études et orientation scolaire internationale. "
            "Tu réponds en français de manière claire, utile et encourageante. "
            "Si des résultats de recherche sont disponibles, utilise-les pour donner des réponses précises. "
            "Si tu ne sais pas, dis-le honnêtement.\n\n"
        )

        context = st.session_state.get("search_context", "")
        if context:
            system_prompt += (
                "Voici les résultats de recherche disponibles :\n"
                f"{context}\n\n"
                "Utilise ces informations pour répondre à la question de l'utilisateur.\n"
            )
        else:
            system_prompt += (
                "Aucune recherche n'a encore été effectuée. "
                "Tu peux quand même aider avec des conseils généraux sur les bourses.\n"
            )

        # Construire l'historique de conversation
        chat_messages = [{"role": "user", "parts": [system_prompt + "\n\nQuestion: " + user_message]}]

        response = model.generate_content(chat_messages)
        answer = response.text

        # Sauvegarder dans l'historique
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        return f"❌ Erreur du chatbot : {str(e)}"


def render_chatbot(api_key: str):
    """
    Affiche l'interface du chatbot dans Streamlit.

    Args:
        api_key: Clé API Google Gemini
    """
    init_chatbot()

    st.markdown("---")
    st.subheader("🤖 Assistant IA - Posez vos questions")
    st.caption("Demandez-moi n'importe quoi sur les bourses, les coûts, les démarches...")

    # Afficher l'historique des messages
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # Zone de saisie
    user_input = st.chat_input("Ex: Quelles bourses pour étudier au Canada ?")

    if user_input:
        st.chat_message("user").write(user_input)
        with st.spinner("Réflexion en cours..."):
            response = get_chatbot_response(user_input, api_key)
        st.chat_message("assistant").write(response)
