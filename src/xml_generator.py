# src/xml_generator.py
from typing import Any, Optional
from pathlib import Path

import xmlschema
from xmlschema.validators import XsdType, XsdGroup, XsdAtomicRestriction, XsdComplexType
from lxml import etree


class XmlGenerator:
    def __init__(self, xsd_path: Path, xml_path: Path) -> None:
        self.xsd: Path = xsd_path
        self.xml: Path = xml_path

    @staticmethod
    def get_base_type(t: Any) -> Optional[str]:
        """
        Recursively find the first built-in type in the type chain (not the primitive).
        """
        if getattr(t, "base_type", None) and "XsdAtomicBuiltin" not in str(t.base_type):
            return XmlGenerator.get_base_type(t.base_type)
        return getattr(getattr(t, "base_type", None), "local_name", None)

    @staticmethod
    def create_sample_value(type_info: Any) -> str:
        """Generate sample values based on type information."""

        # Check for enumerated values
        if hasattr(type_info, "enumeration") and type_info.enumeration:
            return type_info.enumeration[0]

        base_type = XmlGenerator.get_base_type(type_info)

        if base_type:
            examples = {
                "string": "Sample Text",
                "date": "2025-02-11",
                "integer": "123",
                "int": "123",
                "decimal": "123.45",
                "float": "123.45",
                "hexBinary": "48656C6C6F",
                "base64Binary": "SGVsbG8=",
            }
            for key, value in examples.items():
                if key in base_type:
                    return value

        return "Sample Value"

    @staticmethod
    def handle_attributes(element: etree.Element, element_type: XsdType) -> None:
        """Set attributes on the element based on its XSD definition."""
        if hasattr(element_type, "attributes"):
            for attr_name, attr_props in element_type.attributes.items():
                if attr_props.fixed:
                    element.set(attr_name, attr_props.fixed)
                elif attr_props.default:
                    element.set(attr_name, attr_props.default)
                else:
                    element.set(attr_name, "sample_attr")

    @staticmethod
    def handle_child_elements(element: etree.Element, element_type: XsdType) -> None:
        """Add child elements according to XSD constraints (groups, complex types, etc.)."""

        # Default maxOccurs value
        MAX_OCCURS_DEFAULT = 1

        if isinstance(element_type.content, XsdGroup):
            for child in element_type.content.iter_elements():
                min_occurs = child.min_occurs or 0
                max_occurs = (
                    child.max_occurs
                    if child.max_occurs is not None
                    else MAX_OCCURS_DEFAULT
                )
                occurs = max(min_occurs, 1) if max_occurs == 1 else MAX_OCCURS_DEFAULT
                for _ in range(occurs):
                    child_element = XmlGenerator.build_element(child.type, child.name)
                    element.append(child_element)
        elif isinstance(element_type.content, XsdAtomicRestriction):
            element.text = XmlGenerator.create_sample_value(element_type.content)
        elif isinstance(element_type.content, XsdComplexType):
            for child in element_type.content.iter_elements():
                child_element = XmlGenerator.build_element(child.type, child.name)
                element.append(child_element)

    @staticmethod
    def build_element(element_type: XsdType, element_name: str) -> etree.Element:
        """
        Recursively build XML elements and return the constructed element.
        """
        element = etree.Element(element_name)

        # Handle attributes
        XmlGenerator.handle_attributes(element, element_type)

        # Handle child elements
        if hasattr(element_type, "content") and element_type.content:
            XmlGenerator.handle_child_elements(element, element_type)
        elif hasattr(element_type, "simple_type"):
            element.text = XmlGenerator.create_sample_value(element_type.simple_type)
        elif hasattr(element_type, "base_type"):
            element.text = XmlGenerator.create_sample_value(element_type.base_type)

        return element

    def generate_sample_xml(self) -> etree.ElementTree:
        """
        Generate a sample XML document from an XSD schema.
        """
        schema = xmlschema.XMLSchema(self.xsd)
        root_element = next(iter(schema.elements.values()))
        root = self.build_element(root_element.type, root_element.name)

        xml_tree = etree.ElementTree(root)
        xml_string = etree.tostring(
            xml_tree, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )
        with open(self.xml, "wb") as f:
            f.write(xml_string)

        print("Generated sample XML file:", self.xml)
        return xml_tree
