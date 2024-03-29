<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="zh-CN" sourcelanguage="en">
  <context>
    <name>RenameCues</name>
    <message>
      <location filename="../../../plugins/rename_cues/rename_cues.py" line="37"/>
      <source>Rename Cues</source>
      <translation>重新命名 Cue</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="46"/>
      <source>Rename cues</source>
      <translation>重新命名多个 Cue</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="72"/>
      <source>Capitalize</source>
      <translation>首字母大写</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="77"/>
      <source>Lowercase</source>
      <translation>小写</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="82"/>
      <source>Uppercase</source>
      <translation>大写</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="87"/>
      <source>Remove Numbers</source>
      <translation>移除号码</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="93"/>
      <source>Add numbering</source>
      <translation>添加号码</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="101"/>
      <source>Reset</source>
      <translation>重设</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="111"/>
      <source>Rename all cue. () in regex below usable with $0, $1 ...</source>
      <translation>重新命名所有cue。 () 在下列的正规表达式，可用$0, $1 ...</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="121"/>
      <source>Type your regex here: </source>
      <translation>在此输入正规表达式: </translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="232"/>
      <source>Regex help</source>
      <translation>正规表达式帮助</translation>
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
      <translation>您可以使用正则表达式来重命名您的提示。

在下面的行中插入用正则表达式捕获的表达式，第一个括号为 $0，第二个括号为 $1，等等...
在第二行中，您可以使用标准 Python 正则表达式来匹配原始提示名称中的表达式。 使用括号来捕获匹配表达式的部分内容。

例：
^[a-z]([0-9]+) 将找到一个小写字符 ([a-z])，后跟一个或多个数字。
只有数字在括号之间并且可以在第一行中使用 $0。

有关正则表达式的更多信息，请参阅 Python 文档：https://docs.python.org/3/howto/regex.html#regex-howto</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="57"/>
      <source>Current</source>
      <translation>当前名称</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="58"/>
      <source>Preview</source>
      <translation>预览</translation>
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
      <translation>正规表达式错误：无效表达式</translation>
    </message>
    <message>
      <location filename="../../../plugins/rename_cues/rename_ui.py" line="288"/>
      <source>Regex error: catch with () before display with $n</source>
      <translation>正规表达式错误：在显示 $n 前已用 () 捕捉</translation>
    </message>
  </context>
</TS>
