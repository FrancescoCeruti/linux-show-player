<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="it" sourcelanguage="en">
  <context>
    <name>RenameCues</name>
    <message>
      <location filename="../../../plugins/rename_cues/rename_cues.py" line="37"/>
      <source>Rename Cues</source>
      <translation>Rinomina cue</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="46"/>
      <source>Rename cues</source>
      <translation>Rinomina cue</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="72"/>
      <source>Capitalize</source>
      <translation>Iniziali in maiuscolo</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="77"/>
      <source>Lowercase</source>
      <translation>Minuscolo</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="82"/>
      <source>Uppercase</source>
      <translation>Maiuscolo</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="87"/>
      <source>Remove Numbers</source>
      <translation>Rimuovi Numeri</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="93"/>
      <source>Add numbering</source>
      <translation>Aggiungi numerazione</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="101"/>
      <source>Reset</source>
      <translation>Azzera</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="111"/>
      <source>Rename all cue. () in regex below usable with $0, $1 ...</source>
      <translation>Rinomina tutte le cue. () nell'espressione regolare utilizzabili con $0, $1 ...</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="121"/>
      <source>Type your regex here: </source>
      <translation>Scrivi qui la tue espressione regolare: </translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="232"/>
      <source>Regex help</source>
      <translation>Aiuto per espressioni regolari</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="234"/>
      <source>You can use Regexes to rename your cues.

Insert expressions captured with regexes in the line below with $0 for the first parenthesis, $1 forthe second, etc...
In the second line, you can use standard Python Regexes to match expressions in the original cues names. Use parenthesis to capture parts of the matched expression.

Example: 
^[a-z]([0-9]+) will find a lower case character([a-z]), followed by one or more number.
Only the numbers are between parenthesis and will be usable with $0 in the first line.

For more information about Regexes, consult python documentation at: https://docs.python.org/3/howto/regex.html#regex-howto</source>
      <translation>Puoi per rinominare le tue cue tramite espressioni regolari.

Inserisci i testi catturati tramite espressioni nella riga sottostante, utilizzando $0 per la prima parentesi, $1 per la seconda, ecc...
Nella seconda riga, puoi utilizzare le espressioni regolari di Python per catturare del test nei nomi delle cue. Usa la parentesi per catturare parti dell'espressione corrispondente.

Esemplo:
^[a-z]([0-9]+) troverà un carattere minuscolo ([a-z]), seguito da uno o più numeri.
Solo i numeri sono tra parentesi e saranno utilizzabili con $0 nella prima riga.

Per maggiori informazioni sulle espressioni regolari consulta la documentazione di python all'indirizzo: https://docs.python.org/3/howto/regex.html#regex-howto</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="57"/>
      <source>Current</source>
      <translation>Attuale</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="58"/>
      <source>Preview</source>
      <translation>Anteprima</translation>
    </message>
  </context>
  <context>
    <name>RenameCuesCommand</name>
    <message>
      <location filename="../../../plugins/rename_cues/command.py" line="44"/>
      <source>Renamed {number} cues</source>
      <translation>Rinominate {number} cue</translation>
    </message>
  </context>
  <context>
    <name>RenameUiDebug</name>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="259"/>
      <source>Regex error: Invalid pattern</source>
      <translation>Errore Regex: Pattern invalido</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="288"/>
      <source>Regex error: catch with () before display with $n</source>
      <translation>Errore Regex: cattura con () prima di visualizzare con $n</translation>
    </message>
  </context>
</TS>
