from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import nltk
from nltk.corpus import stopwords
from transformers import pipeline


chatbot = None


def get_chatbot():
    global chatbot

    if chatbot is None:
        chatbot = pipeline(
            'text-generation',
            model='distilgpt2'
        )

    return chatbot


def home(request):
    return render(request, 'chat.html')


@csrf_exempt
def repondre(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')

        # Vérifier/télécharger les ressources NLTK uniquement si nécessaire
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)

        # Nettoyer avec stopwords
        stop_words = set(stopwords.words('french'))

        mots = nltk.word_tokenize(message.lower())

        mots_filtres = [
            mot for mot in mots
            if mot not in stop_words
        ]

        # Charger le modèle uniquement lorsqu'il est utilisé
        model = get_chatbot()

        reponse = model(
            message,
            max_length=50
        )[0]['generated_text']

        return JsonResponse({
            'reponse': reponse
        })