import ast
import enum
from dataclasses import dataclass, field
from os import path
from pathlib import Path
from typing import List, Dict, Union, Iterable
from xml.etree import ElementTree as ET


class TextElement(ET.Element):
    def __init__(self, tag, text=None, **kwargs):
        super().__init__(tag, **kwargs)
        self.text = text


class Obsolete(enum.Enum):
    # Keep: keep the obsolete translations, mark them as such
    Keep = enum.auto()
    # Discard: discard obsolete translations
    Discard = enum.auto()
    # Nothing: the option should not be ignored
    Nothing = enum.auto()


@dataclass
class TSLocation:
    filename: str = ""
    line: int = 0

    def to_xml(self):
        return ET.Element(
            "location",
            attrib={"filename": self.filename, "line": str(self.line)},
        )

    @staticmethod
    def from_xml(element: ET.Element) -> "TSLocation":
        return TSLocation(element.get("filename", ""), element.get("line", 0))


@dataclass
class TSTranslation:
    class Types(enum.Enum):
        Unfinished = "unfinished"
        Vanished = "vanished"
        Obsolete = "obsolete"

    type: Union[Types, None] = Types.Unfinished
    translations: List[str] = field(default_factory=list)

    def update(self, translation: "TSTranslation", obsolete=Obsolete.Nothing):
        if obsolete == Obsolete.Nothing:
            if len(translation.translations) > len(self.translations):
                self.translations = translation.translations
        else:
            for n in range(
                min(len(self.translations), len(translation.translations))
            ):
                self.translations[n] = translation.translations[n]

        self.type = None if all(self.translations) else self.Types.Unfinished

    def to_xml(self):
        element = ET.Element("translation")

        if self.type is not None:
            element.set("type", self.type.value)

        if len(self.translations) > 1:
            # TODO: some languages have different plurals rules/forms
            for translation in self.translations:
                element.append(TextElement("numerusform", translation))
        elif self.translations:
            element.text = self.translations[0]

        return element

    @staticmethod
    def from_xml(element: ET.Element) -> "TSTranslation":
        translations = []
        if len(element) > 0:
            translations.extend(element.itertext())
        elif element.text:
            translations.append(element.text)

        return TSTranslation(element.get("type"), translations)


@dataclass
class TSMessage:
    source: str
    location: TSLocation
    translation: TSTranslation

    comment: str = ""
    extracomment: str = ""
    translatorcomment: str = ""

    @property
    def plural(self) -> bool:
        return len(self.translation.translations) > 1

    def key(self):
        return hash((self.source, self.comment))

    def update(self, message: "TSMessage", obsolete=Obsolete.Nothing):
        if obsolete == obsolete.Nothing:
            # We keep the newer value
            self.location = message.location

        self.extracomment = message.extracomment
        self.translatorcomment = message.translatorcomment

        self.translation.update(message.translation, obsolete)

    def mark_obsolete(self):
        self.translation.type = TSTranslation.Types.Obsolete

    def to_xml(self):
        element = ET.Element("message")

        if self.plural:
            element.attrib["numerus"] = "yes"

        element.append(self.location.to_xml())
        element.append(TextElement("source", self.source))

        if self.comment:
            element.append(TextElement("comment", self.comment))
        if self.extracomment:
            element.append(TextElement("extracomment", self.comment))
        if self.translatorcomment:
            element.append(
                TextElement("translatorcomment", self.translatorcomment)
            )

        element.append(self.translation.to_xml())

        return element

    @staticmethod
    def from_xml(element: ET.Element) -> "TSMessage":
        attributes = {
            "source": "",
            "comment": "",
            "extracomment": "",
            "translatorcomment": "",
        }
        location = TSLocation()
        translation = TSTranslation()

        for child in element:
            if child.tag in attributes:
                attributes[child.tag] = child.text
            elif child.tag == "location":
                location = TSLocation.from_xml(child)
            elif child.tag == "translation":
                translation = TSTranslation.from_xml(child)

        return TSMessage(
            location=location, translation=translation, **attributes
        )


@dataclass
class TSContext:
    name: str
    messages: Dict[int, TSMessage] = field(default_factory=dict)

    def add(self, message: TSMessage, obsolete=Obsolete.Nothing):
        message_key = message.key()
        existing_message = self.messages.get(message_key)

        if existing_message is None:
            if obsolete == Obsolete.Discard:
                return

            if obsolete == Obsolete.Keep:
                message.mark_obsolete()

            self.messages[message_key] = message
        else:
            existing_message.update(message, obsolete)

    def update(self, context: "TSContext", obsolete=Obsolete.Nothing):
        for message in context.messages.values():
            self.add(message, obsolete)

    def mark_obsolete(self):
        for message in self.messages.values():
            message.mark_obsolete()

    def to_xml(self):
        element = ET.Element("context")
        element.append(TextElement("name", self.name))

        for message in self.messages.values():
            element.append(message.to_xml())

        return element

    @staticmethod
    def from_xml(element: ET.Element) -> "TSContext":
        context = TSContext(name=element.find("name").text)
        for message_element in element.findall("message"):
            context.add(TSMessage.from_xml(message_element))

        return context


class TSTranslations:
    XML_HEADER = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n'

    def __init__(self, language="en", src_language="en"):
        self.contexts = {}
        self.src_language = src_language
        self.language = language

    def add(self, context: TSContext, obsolete=Obsolete.Nothing):
        existing_context = self.contexts.get(context.name)

        if existing_context is None:
            if obsolete == Obsolete.Discard:
                return

            if obsolete == Obsolete.Keep:
                context.mark_obsolete()

            self.contexts[context.name] = context
        else:
            existing_context.update(context, obsolete)

    def add_message(self, context_name: str, message: TSMessage):
        if context_name not in self.contexts:
            self.contexts[context_name] = TSContext(context_name)

        self.contexts[context_name].add(message)

    def update(self, translations: "TSTranslations", obsolete=Obsolete.Nothing):
        for name, context in translations.contexts.items():
            self.add(context, obsolete)

    def to_xml(self):
        if self.src_language != self.language:
            source_language = self.src_language
        else:
            source_language = ""

        element = ET.Element(
            "TS",
            attrib={
                "version": "2.0",
                "language": self.language,
                "sourcelanguage": source_language,
            },
        )

        for context_name in sorted(self.contexts.keys()):
            element.append(self.contexts[context_name].to_xml())

        return element

    def write(self, file: Union[str, Path]):
        filename = file if isinstance(file, str) else file.as_posix()

        root_element = self.to_xml()
        self.indent(root_element)

        with open(filename, mode="w") as out:
            out.write(
                self.XML_HEADER + ET.tostring(root_element, encoding="unicode")
            )

    def __str__(self):
        return str(self.contexts)

    @staticmethod
    def from_file(file: Union[str, Path]):
        filename = file if isinstance(file, str) else file.as_posix()

        return TSTranslations.from_xml(ET.parse(filename).getroot())

    @staticmethod
    def from_xml(element: ET.Element) -> "TSTranslations":
        translations = TSTranslations()
        for context in element.findall("context"):
            translations.add(TSContext.from_xml(context))

        return translations

    @staticmethod
    def indent(element: ET.Element):
        try:
            # noinspection PyUnresolvedReferences
            ET.indent(element)
        except AttributeError:
            TSTranslations.fallback_indent(element)

    @staticmethod
    def fallback_indent(element: ET.Element, level: int = 0):
        # http://effbot.org/zone/element-lib.htm#prettyprint
        i = "\n" + level * "  "
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + "  "
            if not element.tail or not element.tail.strip():
                element.tail = i
            for element in element:
                TSTranslations.fallback_indent(element, level + 1)
            if not element.tail or not element.tail.strip():
                element.tail = i
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = i


class PyTrFinder:
    FunctionNames = ("translate", "QT_TRANSLATE_NOOP")
    FunctionArgTypes = (ast.Constant, ast.Constant, ast.Constant, ast.expr)

    def __init__(self, destination=".", language="en", src_language="en"):
        self.destination = destination
        self.translations = TSTranslations(language, src_language)

    def find_in_files(self, files: Iterable[Union[str, Path]]):
        for file in files:
            self.find_in_file(file)

    def find_in_file(self, file: Union[str, Path]):
        filename = file if isinstance(file, str) else file.as_posix()

        with open(filename, "r", encoding="utf-8") as file_io:
            self.find_in_code(file_io.read(), filename)

    def find_in_code(self, source_code: str, filename: str):
        self.find_in_ast(ast.parse(source_code), filename)

    def find_in_ast(self, root: ast.AST, filename: str):
        filename = path.relpath(filename, path.dirname(self.destination))

        for function_call in self.walk_function_calls(root):
            context_name, message = self.message_from_args(
                function_call.args, TSLocation(filename, function_call.lineno)
            )
            if context_name and message:
                self.translations.add_message(context_name, message)

    def walk_function_calls(self, root: ast.AST):
        """Go through all the nodes, via `ast.walk`, yield only the one need.

        Specifically we keep only function calls where the function name
        is present in `self.FunctionNames`.
        We only consider "names", not "attributes".
        """
        for node in ast.walk(root):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in self.FunctionNames
            ):
                yield node

    def message_from_args(self, args, location: TSLocation):
        if len(args) < 2:
            return None, None

        for arg_type, argument in zip(self.FunctionArgTypes, args):
            if not isinstance(argument, arg_type):
                return None, None

        context_name = args[0].value
        plural = len(args) > 3
        message = TSMessage(
            source=args[1].value,
            comment=args[2].value if len(args) > 2 else "",
            translation=TSTranslation(
                type=TSTranslation.Types.Unfinished,
                translations=["", ""] if plural else [""],
            ),
            location=location,
        )

        return context_name, message
