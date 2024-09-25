import os

from toolbox.data.keys.structure_keys import StructuredKeys
from toolbox.data.readers.entity.entity_reader import EntityReader
from toolbox_test.base.paths.format_paths import toolbox_TEST_FORMAT_XML_PATH
from toolbox_test.base.tests.base_test import BaseTest
from toolbox_test.data.readers.entity.formats.test_xml_entity_format import TestXmlEntityFormat


class TestEntityReader(BaseTest):
    """
    Responsible for testing the reading and processing of entities.
    """

    def test_read_entities(self):
        """
        Tests that source entities are read in and conversions are applied.
        """
        project_path, file = os.path.split(toolbox_TEST_FORMAT_XML_PATH)
        new_col = "new_name"
        conversion_id = "conversion-id"
        conversions = {conversion_id: {"name": new_col}}
        definition = self.create_definition(file, **{
            StructuredKeys.PARAMS: {"xpath": TestXmlEntityFormat.get_xpath()},
            "cols": conversion_id
        })
        entity_reader = EntityReader(project_path, definition, conversions)
        original_df = entity_reader.read_entities()
        converted_entities = [{new_col: e["name"]} for e in TestXmlEntityFormat.get_entities()]
        self.verify_entities_in_df(converted_entities, original_df)

    def test_read_original_entities(self):
        """
        Tests that source entities are read in and all entries are present.
        """
        project_path, file = os.path.split(toolbox_TEST_FORMAT_XML_PATH)
        definition = self.create_definition(file, **{StructuredKeys.PARAMS: {"xpath": TestXmlEntityFormat.get_xpath()}})
        entity_reader = EntityReader(project_path, definition)
        parser, parser_params = entity_reader.get_parser()
        original_df = parser.parse(entity_reader.path, **parser_params)
        self.verify_entities_in_df(TestXmlEntityFormat.get_entities(), original_df)

    def test_read_column_conversions(self):
        """
        Tests ability to read column conversions from definition.
        """
        expected_value = 42
        definition = self.create_definition(**{StructuredKeys.COLS: "conversion-id"})
        conversions = {"conversion-id": expected_value}
        entity_reader = EntityReader("", definition, conversions)
        self.assertEqual(expected_value, entity_reader.get_column_conversion())

    def test_read_column_conversions_default_value(self):
        """
        Tests that default value is None when definition contains no column conversions.
        """
        definition = {StructuredKeys.PATH: ""}
        entity_reader = EntityReader("", definition, {})
        self.assertIsNone(entity_reader.get_column_conversion())

    @staticmethod
    def create_definition(path: str = "", **kwargs):
        return {StructuredKeys.PATH: path, **kwargs}
