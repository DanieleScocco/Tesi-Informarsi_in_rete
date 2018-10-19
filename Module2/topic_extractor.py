import mysql.connector
from textblob import TextBlob
import nltk


def connect_to_db():
	try:
		res = mysql.connector.connect(user='module1', password='insertnews', host='localhost', database='tesi')
		return res
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("\nPassword e/o username errati")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("\nDatabase does not exist")
		else:
			print("\nErrore: " + err)
		return None

def contains_word(s, w):
	return(' ' + w + ' ') in (' ' + s + ' ')

def insert_topics(topics, article):
	insertconnection = connect_to_db()
	insertcursor = insertconnection.cursor()
	for t in topics:
		if t in tlist:
			#Inserimento della correlazione nel database
			correlation_query = ("INSERT INTO articolitopic (articolo, topic) VALUES (%s, %s)")
			correlation_data = (article[0], t)
			insertcursor.execute(correlation_query, correlation_data)
			insertconnection.commit()
		else:
			#Inserimento dei dati nel database
			tlist.append(t)
			
			extracted_topic = ("INSERT INTO topic (nome) VALUES (%s)")
			extracted_data = (t)
			insertcursor.execute(extracted_topic, extracted_data)
			
			correlation_query = ("INSERT INTO articolitopic (articolo, topic) VALUES (%s, %s)")
			correlation_data = (article[0], t)
			insertcursor.execute(correlation_query, correlation_data)
			insertconnection.commit()
	insertcursor.close()
	insertconnection.close()

#connessione al database
print("---------- MODULO 2 - ESECUZIONE ----------\n")
print("------- Elaborazione topic articoli--------\n")
print("Connessione al database... ")
articleconnection = connect_to_db()
articlecursor = articleconnection.cursor();
print("completata\n")

articlecursor.execute("SELECT COUNT * FROM articoli")
n_articoli = articlecursor.fetchall()
progress = 0


print("Raccolta articoli...\n")
articlecursor.execute("SELECT * FROM articoli")
articoli = articlecursor.fetchall()

print("Articoli ottenuti\n")

#ottenere lista topic
articlecursor.execute("SELECT * FROM topic")
tlist = articlecursor.fetchall()

articlecursor.close()
articleconnection.close()

print("Analisi articoli per topic...\n")

for a in articoli:
	text = TextBlob(a[1])
	if text.detect_language() == "it":
		#poichè in italiano la ricerca dei nomi funziona molto peggio rispetto all'inglese effettuo la traduzione, il risultato più affidabile
		text = text.translate(to="en")
	
	raw = text.noun_phrases
	#rimozione duplicati puri
	unique = list(set(raw))
	topic = []
	atmp = []
	#rimozione dei dublicati logici: es. sergio mattarella e mattarella sono la stessa cosa, viene mantenuto solo sergio mattarella
	for t in unique:
		f = True
		atmp = unique.copy()
		atmp.remove(t)
		for a in atmp:
			if contains_word(a, t):
				f = False
		if f:
			topic.append(t)
	
	insert_topics(topic, a)
		
	#Output di aggiornamento
	progress = progress + 1
	percentage = progress/n_articoli*100
	print("Avanzamento: " percentage "   " progress "/" n_articoli, end='\r')
	



#chiusura script

print("\n---------- ESECUZIONE TERMINATA! ----------")