import unittest
import os
from pathlib import Path
from properties_modules import properties as prop

source_directory = os.curdir+"/tests/resources/"
tmp_path = source_directory
fis = "egg2"
features = "add_payee,android_biometrics,app_store_feedback,ios_biometrics,wallet_ui"
features_list = features.split(",")
Path(tmp_path).mkdir(parents=True, exist_ok=True)


class PropertiesMethods(unittest.TestCase):

    def test_process_properties(self):
        operation = "optin"
        properties = prop.process_properties(fis, features_list, operation, tmp_path)
        self.assertIsInstance(properties, prop.Properties)

    def test_validate_rule(self):
        prop_test = ["fi.payee.management_entitlement"]
        result = prop.validate_rule(prop_test)
        self.assertEqual(result, "white-listing")
        prop_test = ["any.other.property"]
        result = prop.validate_rule(prop_test)
        self.assertEqual(result, "true")

    def test_get_properties(self):
        result = prop.get_properties(features_list)
        self.assertEqual(len(result), 9)


if __name__ == '__main__':
    unittest.main()
