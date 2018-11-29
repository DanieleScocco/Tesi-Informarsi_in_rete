'''
Nome:
Controllo della qualità dell'estrazione

Obiettivo:
L'algoritmo veifica la qualità delle estrazioni ottenendo informazioni di vario genere

Passaggi:
Collegamento al database
Raccolta della lista dei siti web
Per ogni notizia vengono estratti testo e titolo, poi viene salvato il testo puro
Stampa a schermo dei dati ottenuti
'''


import mysql.connector
import os
from newspaper import Article


#Funzione di connessione al database
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

#Inizio script
		
#Connessione al database
print("---------- MODULO 2 - ESECUZIONE ----------\n")
print("-------- Test estrazione testo articoli---------\n")
print("Connessione al database... ")
newsconnection = connect_to_db()
newscursor = newsconnection.cursor()
print("completata\n")

progress = 0

#Minimo di parole perchè un articolo non sia considerato corto:
minWd = 100
avgWd = 300
#Numero di articoli da analizzare:
numTst = 20000

#Creazione elenco nomi dei siti
erroriPerSito = dict()
newscursor.execute("SELECT nome FROM sitiweb")
nomiSiti = newscursor.fetchall()

for s in nomiSiti:
	erroriPerSito[s[0]] = 0

#Raccolta dei link dei siti web
print("Raccolta pagine html...\n")
newscursor.execute("SELECT * FROM notizie")

print("Notizie ottenute\n")

testate = 0
voidTitleArticle = 0
titleArticleShort = 0
voidTextArticle = 0
textArticleShort = 0
textArticleAvgWd = 0
RMcount = 0
errori = 0
TOTtextLen = 0

rm = "read more"
RM = "Read more"
readMore = False
errAttuale = False


print("Estrazione articoli...\n")

while True:
	notizie = newscursor.fetchmany(50)
	if testate >= numTst:
		break
	for n in notizie:
		#Estrazione info dall'articolo
		html = n[4]
		a = Article('')
		a.set_html(html)
		try:
			a.parse()
			titleArticle = a.title
			textArticle = a.text
			
			#Conteggio del numero di aticoli testati
			testate = testate + 1
			
			#Controllo della lunghezza del titolo
			titleArticleLen = len(titleArticle.split())
			
			#Se la lunghezza del titolo è nulla o troppo corta (<5 parole) viene aumentato l'apposito contatore
			if titleArticleLen == 0:
				voidTitleArticle = voidTitleArticle + 1
				errAttuale = True
			elif titleArticleLen <= 5:
				titleArticleShort = titleArticleShort + 1
			
			#Controllo della lunghezza del testo
			textArticleLen = len(textArticle.split())
			
			#Se la lunghezza del testo è nulla, troppo corta o inferiore alla media viene aumentato l'apposito contatore
			if textArticleLen == 0:
				voidTextArticle = voidTextArticle + 1
				errAttuale = True
			elif textArticleLen <= minWd:
				textArticleShort = textArticleShort + 1
			elif textArticleLen <= avgWd:
				textArticleAvgWd = textArticleAvgWd + 1
			
			#Controllo della presenza del read more (indice della possibile parzialità dell'articolo)
			if textArticle.find(rm, (len(textArticle)-200), len(textArticle)) >= 0:
				readMore = True
				errAttuale = True
			if textArticle.find(RM, (len(textArticle)-200), len(textArticle)) >= 0:
				readMore = True
				errAttuale = True
			
			#Se ha trovato un read more viene aumentato l'apposito contatore
			if readMore:
				RMcount = RMcount + 1
				readMore = False
		except:
			errAttuale = True
		
		#Se questo articolo è vuoto, corto o contiene un read more viene aumentato l'apposito contatore
		if errAttuale:
			errori = errori + 1
			erroriPerSito[n[2]] = erroriPerSito[n[2]] + 1
			errAttuale = False
		
		#Output di aggiornamento
		print("Avanzamento:   Testate: ", testate, "   Errori", errori, end='\r')
		
		#Conteggio della lunghezza totale
		TOTtextLen = TOTtextLen + textArticleLen
		
print("")
percErrori = "{0:.2f}".format(errori*100 / testate)
lunghezzaMedia = int(TOTtextLen / testate)
print("\n\n")
print("Errori per sito:")
for x, y in erroriPerSito.items():
	print(x, ": ", y)
print("\n\n")
print(">>>>>>>>>>>>>   RISULTATI FINALI ANALISI   <<<<<<<<<<<<< \n\n")
print("Titoli vuoti (errore): ----------------------------->  ", voidTitleArticle, "\n")
print("Titoli sotto le 5 parole --------------------------->  ", titleArticleShort, "\n")
print("Articoli vuoti (errore): --------------------------->  ", voidTextArticle, "\n")
print("Articoli sotto il minimo di", minWd, "parole: ---------->  ", textArticleShort, "\n")
print("Articoli sotto la media attesa di", avgWd, "parole: ---->  ", textArticleAvgWd, "\n")
print("Read more trovati (errore): ------------------------>  ", RMcount, "\n")
print("Errori trovati: ------------------------------------>  ", errori, "\n")
print("Percentuale errori trovati: ------------------------>  ", percErrori, "%\n")
print("Lunghezza media articoli: -------------------------->  ", lunghezzaMedia, "parole\n")

newscursor.close()
newsconnection.close()

print("\n---------- ESECUZIONE TERMINATA! ----------")

#Fine script