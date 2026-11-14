# N.A.P.L.E.S. — The Big Hack 2026

## Contesto
- Challenge 05 di Fastweb + Vodafone, «Napoli Agentic City». Il nostro progetto è N.A.P.L.E.S.:
  agenti AI per la resilienza urbana di Napoli, con la control room comunale. Il concept sta in
  docs/PROGETTO.md.
- Cinque persone (docs/TEAM.md) su tre PC, stesso repository, branch main. Consegna domenica 15/11 alle 12:00.
- La giuria valuta: utilità e valore, attinenza alla challenge, chiarezza e completezza, design
  e user experience, creatività e innovazione. Lo sponsor guarda visione, originalità,
  concretezza e benefici misurabili.

## Priorità, in ordine
1. Il percorso demo funziona sempre su main, dall'inizio alla fine.
2. Si vede che gli agenti si coordinano e si misura la differenza con e senza coordinamento.
3. Cura dell'interfaccia lungo il percorso demo.
4. Tutto il resto.

## Lavoro in team
- Il contesto condiviso sta nel repository, non nelle conversazioni. A inizio sessione esegui
  `git pull --rebase origin main`, poi leggi docs/STATO.md e docs/PIANO.md.
- Chiunque può lavorare su qualunque modulo: non ci sono aree riservate. Prima di iniziare un
  compito fai pull e guarda la tabella «Chi sta lavorando su cosa» in docs/STATO.md. Se il
  compito è libero aggiungi la riga e mandala subito su GitHub con un commit di quella sola
  riga, `chore(status): claim <compito>`: è l'unico commit che non richiede la conferma del
  nome. Se è già preso fermati e dimmelo: decidiamo noi come dividerci.
- A compito finito togli la riga e aggiorna Fatto e Prossimi compiti liberi.
- Mai `git push --force` e mai riscrivere la storia di main. Se c'è un conflitto fermati,
  mostra i file e proponi la soluzione che conserva il lavoro di entrambi.
- Le chiavi stanno in .env, che non si committa. Ogni variabile nuova va aggiunta a
  .env.example, senza valore.

## Architettura modulare
- Un modulo, una cartella, con i suoi test e un README di dieci righe che dice cosa espone.
- Un file per cosa: un agente, una fonte dati, una schermata stanno ciascuno nel proprio file.
  Se due compiti richiedono lo stesso file, il file va diviso.
- I moduli comunicano solo attraverso i contratti in contracts/ (stato del simulatore,
  messaggi sul bus, API interne). Nessun import dentro la cartella di un altro modulo.
- Un contratto si cambia con un commit piccolo e dedicato, mandato subito su GitHub, con una
  riga in docs/STATO.md che avvisa gli altri.
- Un agente, un adattatore o una schermata nuova si registra aggiungendo una riga a un indice,
  senza modificare il codice degli altri moduli.
- File che tutti toccano (README.md, docs/STATO.md, contratti, dipendenze, configurazione):
  modifiche minime, pull subito prima e push subito dopo.

## Commit
Per ogni commit, in quest'ordine:
1. `git pull --rebase origin main`.
2. `make check` deve passare.
3. Aggiorna README.md (Stato attuale e una riga nuova in cima al Registro delle modifiche) e
   docs/STATO.md.
4. Mostra `git status` e un riepilogo delle modifiche, proponi il messaggio di commit e chiedi
   al team di confermarlo o di dare un altro nome. Aspetta la risposta: non committare prima.
5. Commit, poi push subito.
Messaggio in formato Conventional Commits, `tipo(ambito): descrizione`: in inglese,
all'imperativo, al massimo 72 caratteri, tipi feat, fix, docs, test, refactor, chore, con il
modulo come ambito. Nel corpo il perché, quando non è ovvio. Un commit contiene una sola
modifica logica; niente segreti e niente file generati.
Ogni commit, compresi quelli di presa in carico, termina con una riga vuota seguita da una riga
`Co-authored-by: Nome <email>` per ciascun collaboratore di docs/TEAM.md diverso da chi fa il
commit. Chi fa il commit si riconosce da `git config user.email`.

## Regole di lavoro
- A inizio compito esegui `date` e confronta con le scadenze in docs/STATO.md. Se siamo in
  ritardo proponi cosa tagliare dal fondo delle priorità.
- Lavora un compito alla volta. A compito finito segui la procedura di commit, poi fermati con
  il riepilogo e aspetta il via.
- A inizio compito rileggi docs/STAND.md e docs/FEEDBACK.md: contengono risposte dello sponsor
  e prove fatte a mano dal team, e prevalgono sulle tue ipotesi.
- Ogni dato simulato e ogni ipotesi vanno in docs/IPOTESI.md e sono etichettati nell'interfaccia.
  I dati confermati e quelli incerti si distinguono sempre, anche a schermo.
- Ogni evento sismico o di emergenza della demo è simulato ed etichettato come simulazione. Il
  sistema affianca INGV e Protezione Civile, non li sostituisce, e non inventa istruzioni di
  evacuazione. L'operatore approva ogni decisione. Nessun dato personale.
- Il percorso demo funziona offline: ogni chiamata di rete o a un LLM ha cache o esecuzione
  registrata.
- Chiedi prima di usare servizi a pagamento o dipendenze molto pesanti.
- Interfaccia e materiali per la giuria in italiano; codice e commit in inglese.
- Interfaccia con una direzione visiva precisa e coerente, leggibile su un proiettore.
  Controlla ogni schermata del percorso demo con uno screenshot.
- Nel riepilogo di fine compito distingui ciò che funziona da ciò che è simulato, parziale o
  rotto, allega la prova e chiudi con l'elenco di ciò che il team deve provare a mano.

## Comandi
Da compilare appena esistono: installazione, avvio della demo, make check.

## Compact Instructions
Conserva scadenze, compito in corso, decisioni di architettura, comandi e problemi aperti.
