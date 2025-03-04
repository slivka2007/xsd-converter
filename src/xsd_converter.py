# src/xsd_converter.py
import json
import xmltodict
from typing import Any
import xmlschema
from xmlschema.validators import XsdType, XsdGroup, XsdAtomicRestriction, XsdComplexType
from lxml import etree
from data_loader import DataLoader


class XSDConverter:
    _xml_string: str = None

    @classmethod
    def _get_base_type(cls, type_info: Any) -> str:
        """
        Recursively find the first built-in type in the type chain (not the primitive).
        """

        if getattr(type_info, "base_type", None) and "XsdAtomicBuiltin" not in str(
            type_info.base_type
        ):
            return XSDConverter._get_base_type(type_info.base_type)
        return getattr(getattr(type_info, "base_type", None), "local_name", None)

    @classmethod
    def _create_sample_value(cls, type_info: Any) -> str:
        """Generate sample values based on type information."""

        if hasattr(type_info, "enumeration") and type_info.enumeration:
            return type_info.enumeration[0]

        base_type = cls._get_base_type(type_info)

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

    @classmethod
    def _handle_attributes(cls, element: etree.Element, element_type: XsdType) -> None:
        """Set attributes on the element based on its XSD definition."""

        if hasattr(element_type, "attributes"):
            for attr_name, attr_props in element_type.attributes.items():
                if attr_props.fixed:
                    element.set(attr_name, attr_props.fixed)
                elif attr_props.default:
                    element.set(attr_name, attr_props.default)
                else:
                    element.set(attr_name, "sample_attr")

    @classmethod
    def _handle_child_elements(
        cls, element: etree.Element, element_type: XsdType, max_occurs: int
    ) -> None:
        """Add child elements according to XSD constraints (groups, complex types, etc.)."""

        if isinstance(element_type.content, XsdGroup):
            for child in element_type.content.iter_elements():
                child_min_occurs = child.min_occurs or 0
                child_max_occurs = (
                    child.max_occurs if child.max_occurs is not None else max_occurs
                )
                occurs = (
                    max(child_min_occurs, 1) if child_max_occurs == 1 else max_occurs
                )
                for _ in range(occurs):
                    child_element = cls._build_element(
                        child.type, child.name, max_occurs
                    )
                    element.append(child_element)
        elif isinstance(element_type.content, XsdAtomicRestriction):
            element.text = cls._create_sample_value(element_type.content)
        elif isinstance(element_type.content, XsdComplexType):
            for child in element_type.content.iter_elements():
                child_element = cls._build_element(child.type, child.name)
                element.append(child_element)

    @classmethod
    def _build_element(
        cls, element_type: XsdType, element_name: str, max_occurs: int
    ) -> etree.Element:
        """
        Recursively build XML elements and return the constructed element.
        """

        element = etree.Element(element_name)

        cls._handle_attributes(element, element_type)

        if hasattr(element_type, "content") and element_type.content:
            cls._handle_child_elements(element, element_type, max_occurs)
        elif hasattr(element_type, "simple_type"):
            element.text = cls._create_sample_value(element_type.simple_type)
        elif hasattr(element_type, "base_type"):
            element.text = cls._create_sample_value(element_type.base_type)

        return element

    @classmethod
    def _convert_xsd(cls, max_occurs: int) -> Any:
        """
        Convert an XSD schema to a parsable tree.
        """

        schema = xmlschema.XMLSchema(DataLoader.get_xsd_path())
        root_element = next(iter(schema.elements.values()))
        root = cls._build_element(root_element.type, root_element.name, max_occurs)

        xml_string = etree.tostring(
            etree.ElementTree(root),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )

        return xml_string

    @classmethod
    def generate_sample(cls, max_occurs: int, xsd_string: str, sample_type: str) -> Any:
        """
        Generate a sample.
        """

        if xsd_string != "":
            DataLoader.write_xsd_file(xsd_string)

        xml_xstring = cls._convert_xsd(max_occurs)

        if sample_type == "xml":
            sample_string = cls.generate_sample_xml(xml_xstring)
        elif sample_type == "json":
            sample_string = cls.generate_sample_json(xml_xstring)

        return sample_string

    @classmethod
    def generate_sample_xml(cls, xml_xstring: Any) -> str:
        """
        Generate a sample XML document from an XSD schema.
        """

        DataLoader.write_xml_file(xml_xstring)
        print("Sample XML successfully generated.")

        return DataLoader.load_xml_file()

    @classmethod
    def generate_sample_json(cls, xml_xstring: Any) -> str:
        """
        Generate a sample JSON document from an XSD schema.
        """

        xml_dict = xmltodict.parse(xml_xstring)
        json_string = json.dumps(xml_dict, indent=4)
        DataLoader.write_json_file(json_string)
        print("Sample JSON successfully generated.")

        return DataLoader.load_json_file()
