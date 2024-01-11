import csv
from flask import Flask, helpers, render_template, request
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
    try:
        resp = es.index(index="livres_index", body=doc)
        logger.info(f"Document indexé : {resp}")
        return resp
    except Exception as e:
        logger.error(f"Erreur lors de l'indexation du document : {e}")

# Indexer les livres dans Elasticsearch au démarrage de l'application
if not es.indices.exists(index="livres_index"):
    try:
        es.indices.create(index="livres_index")

        # Lire le fichier CSV et indexer les données
        with open('data/books.csv', mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                doc = {
                    'titre': row['book_title'],
                    'auteur': row['book_author']
                }
                indexer_document(doc)
    except RequestError as e:
        logger.error(f"Une erreur s'est produite lors de la création de l'index : {e}")


@app.route('/', methods=['GET', 'POST'])
def accueil():
    recherche = request.form.get('recherche', '').lower()
    if recherche:
        # Effectuer la recherche dans Elasticsearch
        resp = es.search(index="livres_index", body={"query": {"match": {"titre": recherche}}})
        resultats = [hit['_source'] for hit in resp['hits']['hits']]
    else:
        # Récupérer tous les livres si aucune recherche n'est effectuée
        resp = es.search(index="livres_index", body={"query": {"match_all": {}}})
        resultats = [hit['_source'] for hit in resp['hits']['hits']]
    return render_template('index.html', livres=resultats, recherche=recherche)

if __name__ == '__main__':
    app.run(debug=True)
