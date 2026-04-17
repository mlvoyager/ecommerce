import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
import time

nltk.download('punkt')
nltk.download('stopwords')


def nettoyage(texte):
    texte = texte.lower()
    texte = word_tokenize(texte)

    stop_words = set(stopwords.words('french'))

    texte = [mot for mot in texte if mot not in stop_words]
    texte = [re.sub(r'[^\w\s]', '', mot) for mot in texte]

    return ' '.join(texte)


def simple_bot(texte):

    texte = nettoyage(texte)

    responses = {
        "bonjour": "Bonjour, comment puis-je vous aider ?",
        "au revoir": "Au revoir !",
        "heure": f"Il est {datetime.now().strftime('%H:%M')}",
        "date": f"Aujourd'hui nous sommes le {time.strftime('%d %B %Y')}",
    }

    for command in responses:
        if command in texte:
            return responses[command]

    return "Je n'ai pas compris votre question."