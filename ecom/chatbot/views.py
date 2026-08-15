from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import nltk
from nltk.corpus import stopwords
from transformers import pipeline
import json

# Télécharger NLTK (une seule fois)
nltk.download('punkt')
nltk.download('stopwords')

# Charger le modèle Transformers
chatbot = pipeline('text-generation', model='distilgpt2')

def home(request):
    return render(request, 'chat.html')

@csrf_exempt
def repondre(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        
        # Nettoyer avec stopwords
        stop_words = set(stopwords.words('french'))
        mots = nltk.word_tokenize(message.lower())
        mots_filtres = [mot for mot in mots if mot not in stop_words]
        
        # Générer réponse avec Transformers
        reponse = chatbot(message, max_length=50)[0]['generated_text']
        
        return JsonResponse({'reponse': reponse})