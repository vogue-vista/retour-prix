import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# -------------------------
# CONFIGURATION DE LA PAGE
# -------------------------
st.set_page_config(page_title="SaaS Retours Auto Pro", page_icon="📦", layout="wide")

# Masquer la sidebar par défaut pour un look épuré
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
@import url('https://googleapis.com');
html, body, div, p, h1, h2, h3, h4, h5, h6, span {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIGURATION PAYPAL (À REMPLIR PLUS TARD)
# -------------------------
PAYPAL_CLIENT_ID = "DEMO"  # Mettez votre Client ID ici plus tard
PAYPAL_PLAN_ID = "DEMO"    # Mettez votre Plan ID ici plus tard (Abonnement à 30$/mois)

# -------------------------
# GESTION DE L'ACCÈS (SESSION STATE)
# -------------------------
if "est_abonne" not in st.session_state:
    st.session_state.est_abonne = False

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_KEY = ""

# -------------------------
# INTERFACE SÉCURISÉE
# -------------------------
st.title("📦 RetoursAuto IA — Version Premium")

# CAS 1 : L'UTILISATEUR N'A PAS PAYÉ
if not st.session_state.est_abonne:
    st.warning("🔒 Cette application est réservée aux membres de la version Premium.")
    
    col_offre, col_connexion = st.columns(2, gap="large")
    
    with col_offre:
        st.subheader("🚀 Débloquez l'IA pour 30 $/mois")
        st.write("Automatisez la gestion de vos retours e-commerce, analysez l'état des produits et réduisez vos pertes logistiques.")
        st.write("Le paiement est entièrement sécurisé par **PayPal**.")
        
        if PAYPAL_CLIENT_ID == "DEMO":
            paypal_html = """
            <a href="https://paypal.com" target="_blank" style="text-decoration: none;">
                <div style="background-color: #ffc439; color: #003087; text-align: center; 
                            padding: 12px; font-family: Arial, sans-serif; font-weight: bold; 
                            border-radius: 4px; max-width: 300px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🟨 S'abonner avec PayPal (30$/mois)
                </div>
            </a>
            """
        else:
            paypal_html = f"""
            <div id="paypal-button-container-fixed" style="max-width: 350px; margin-top: 20px;"></div>
            <script src="https://paypal.com{PAYPAL_CLIENT_ID}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
            <script>
              paypal.Buttons({{
                  style: {{ shape: 'rect', color: 'gold', layout: 'vertical', label: 'subscribe' }},
                  createSubscription: function(data, actions) {{
                    return actions.subscription.create({{ 'plan_id': '{PAYPAL_PLAN_ID}' }});
                  }},
                  onApprove: function(data, actions) {{
                    alert('Abonnement réussi ! ID : ' + data.subscriptionID);
                  }}
              }}).render('#paypal-button-container-fixed');
            </script>
            """
        
        components.html(paypal_html, height=150, scrolling=False)
        
    with col_connexion:
        st.subheader("🔑 Déjà abonné ?")
        st.write("Connectez-vous pour activer vos accès.")
        email = st.text_input("Adresse e-mail", key="login_email")
        mot_de_passe = st.text_input("Mot de passe", type="password", key="login_password")
        
        if st.button("Se connecter", use_container_width=True):
            if email == "test@client.com" and mot_de_passe == "access30":
                st.session_state.est_abonne = True
                st.success("Accès accordé ! Chargement...")
                st.button("👉 Cliquer ici pour entrer")
            else:
                st.error("Identifiants incorrects ou abonnement PayPal inactif.")

# CAS 2 : L'UTILISATEUR EST ABONNÉ -> ACCÈS COMPLET
else:
    st.write("✨ **Bienvenue dans votre espace Premium.** Votre gestionnaire de retours automatisé est actif.")
    if st.button("🚪 Se déconnecter", key="logout"):
        st.session_state.est_abonne = False
        st.rerun()
        
    st.write("---")

    with st.container(border=True):
        col_input, col_details = st.columns(2)
        
        with col_input:
            produit_retourne = st.text_input("Nom de l'article retourné", 
                                             placeholder="Ex: Chaussures Nike Dunk Low (Taille 42)")
            raison_retour = st.selectbox("Raison principale invoquée par le client", [
                "❌ Problème de taille / Trop petit ou trop grand",
                "⚠️ Article défectueux ou endommagé",
                "🎨 Ne correspond pas aux photos du site",
                "🤔 Changement d'avis du client",
                "📦 Erreur d'expédition (Mauvais article reçu)"
            ])
            
        with col_details:
            etat_produit = st.selectbox("État visuel du produit à la réception", [
                "💎 Comme neuf (Emballage d'origine intact)",
                "🙂 Légèrement utilisé (Sans étiquette / Boîte abîmée)",
                "🔥 Endommagé / Impossible à revendre en l'état"
            ])
            frais_livraison_retour = st.number_input("Coût de l'étiquette de retour payée par votre boutique ($)", min_value=0.0, value=7.50, step=0.50)

        generer = st.button("🚀 Automatiser le Traitement & Générer le Rapport IA", use_container_width=True)

    if generer:
        if not API_KEY:
            st.error("⚠️ Erreur : La clé GROQ_API_KEY est manquante dans les Secrets du serveur.")
        elif not producto_retourne: # Correction de la variable si vide
            st.error("⚠️ Veuillez indiquer le nom du produit retourné.")
        else:
            with st.spinner("L'IA de Groq traite le retour et met à jour l'inventaire..."):
                try:
                    client = Groq(api_key=API_KEY)
                    
                    prompt_systeme = """Tu es un expert en logistique e-commerce et en service client automatisé.
                    Tu dois obligatoirement formater ta réponse sous forme de tableau Markdown avec exactement 3 colonnes :
                    1. **Étape Logistique** (ex: Statut de l'inventaire, Action Client, Impact Financier)
                    2. **Décision Automatisée** (La décision claire de l'outil)
                    3. **Message automatique à envoyer au client** (Un court mail poli et prêt à envoyer)
                    Ne fais aucune intro ou conclusion."""

                    prompt_utilisateur = f"""
                    Article retourné : '{produit_retourne}'
                    Raison du retour : {raison_retour}
                    État à la réception : {etat_produit}
                    Frais de transport engagés : {frais_livraison_retour}$
                    """

                    reponse = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": prompt_systeme},
                            {"role": "user", "content": prompt_utilisateur}
                        ],
                        temperature=0.4
                    )
                    
                    script_genere = reponse.choices[0].message.content
                    st.success("✨ Le retour a été traité avec succès !")
                    st.markdown(script_genere)
                    st.text_area("Copier les données logistiques brutes :", value=script_genere, height=200)

                except Exception as e:
                    st.error(f"Erreur technique Groq : {str(e)}")
