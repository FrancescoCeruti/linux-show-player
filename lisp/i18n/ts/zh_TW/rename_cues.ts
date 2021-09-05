<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="zh-TW" sourcelanguage="en">
  <context>
    <name>RenameCues</name>
    <message>
      <location filename="../../../plugins/rename_cues/rename_cues.py" line="37"/>
      <source>Rename Cues</source>
      <translation>重新命名多個 Cue</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="46"/>
      <source>Rename cues</source>
      <translation>重新命名 Cue</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="72"/>
      <source>Capitalize</source>
      <translation>首字母大寫</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="77"/>
      <source>Lowercase</source>
      <translation>小寫</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="82"/>
      <source>Uppercase</source>
      <translation>大寫</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="87"/>
      <source>Remove Numbers</source>
      <translation>移除號碼</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="93"/>
      <source>Add numbering</source>
      <translation>添加號碼</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="101"/>
      <source>Reset</source>
      <translation>重設</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="111"/>
      <source>Rename all cue. () in regex below usable with $0, $1 ...</source>
      <translation>重新命名所有cue。() 在下列的正規表達式，可用$0, $1 ...</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="121"/>
      <source>Type your regex here: </source>
      <translation>在此輸入正規表達式: </translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="232"/>
      <source>Regex help</source>
      <translation>正規表達式幫助</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="234"/>
      <source>You can use Regexes to rename your cues.

Insert expressions captured with regexes in the line below with $0 for the first parenthesis, $1 forthe second, etc...
In the second line, you can use standard Python Regexes to match expressions in the original cues names. Use parenthesis to capture parts of the matched expression.

Exemple: 
^[a-z]([0-9]+) will find a lower case character([a-z]), followed by one or more number.
Only the numbers are between parenthesis and will be usable with $0 in the first line.

For more information about Regexes, consult python documentation at: https://docs.python.org/3/howto/regex.html#regex-howto</source>
      <translation>你可以用正規表達式（Regexes）重新命名cues。

在第一行輸入正規表達式，$0為第一個括號，$1為第二個括號，如此類推...
在第二行中，你可以使用標準python正規表達式以搜尋匹配的cues名稱。使用括號以搜尋匹配的表達式。

例子：
^[a-z]([0-9]+) 會尋找小寫字元 ([a-z])，兼且有一個或以上的數字。
只有數字是在括號之間而能用於第一行的$0。

若要獲取更多正規表達式的資訊，請查閱python說明：https://docs.python.org/3/howto/regex.html#regex-howto</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="57"/>
      <source>Current</source>
      <translation>當前名稱</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="58"/>
      <source>Preview</source>
      <translation>預覽</translation>
    </message>
  </context>
  <context>
    <name>RenameCuesCommand</name>
    <message>
      <location filename="../../../plugins/rename_cues/command.py" line="44"/>
      <source>Renamed {number} cues</source>
      <translation>已重新命名 {number} 個 Cue</translation>
    </message>
  </context>
  <context>
    <name>RenameUiDebug</name>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="259"/>
      <source>Regex error: Invalid pattern</source>
      <translation>正規表達式錯誤：無效表達式</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="288"/>
      <source>Regex error: catch with () before display with $n</source>
      <translation>正規表達式錯誤：在顯示 $n 前已用 () 捕捉</translation>
    </message>
  </context>
</TS>
