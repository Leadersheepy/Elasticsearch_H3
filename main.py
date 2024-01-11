from flask import Flask, render_template, request
from elasticsearch import Elasticsearch, RequestError
from datetime import datetime
import logging

app = Flask(__name__)

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connexion à Elasticsearch
es = Elasticsearch(hosts="http://localhost:9200")

# Cette fonction indexe un document dans Elasticsearch
def indexer_document(doc):
    resp = es.index(index="livres-index", body=doc)
    return resp

# Une liste de livres de démonstration pour cet exemple
livres = [
    {"titre": "Harry Potter", "auteur": "J.K. Rowling"},
    {"titre": "Le Seigneur des anneaux", "auteur": "J.R.R. Tolkien"},
]

# Indexer les livres dans Elasticsearch au démarrage de l'application
if not es.indices.exists(index="livres-index"):
    try:
        es.indices.create(index="livres-index")
        for idx, livre in enumerate(livres, start=1):
            livre_doc = {
                'titre': livre['titre'],
                'auteur': livre['auteur'],
                'id': idx
            }
            indexer_document(livre_doc)
    except RequestError as e:
        logger.error(f"Une erreur s'est produite lors de la création de l'index : {e}")

@app.route('/')
def accueil():
    # Exemple de production de logs
    logger.info('Accès à la page d\'accueil!')

    # Récupérer tous les livres de la base de données Elasticsearch
    resp = es.search(index="livres-index", body={"query": {"match_all": {}}})
    livres = [hit['_source'] for hit in resp['hits']['hits']]
    return render_template('index.html', livres=livres)

if __name__ == '__main__':
    app.run(debug=True)
