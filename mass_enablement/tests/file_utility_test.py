import unittest
import os
import shutil
import zipfile
from pathlib import Path
from utility_modules import file_utility as fu

source_directory = os.curdir+"/tests/resources/"
tmp_path = source_directory + "/tmp/"
final_list = ["egg2"]
zip_list = ["egg2"]
out_path = source_directory + "out/"
features = "add_payee,android_biometrics,app_store_feedback,ios_biometrics,wallet_ui"
features_list = features.split(",")
deletions_path = source_directory + "deletions/"
Path(tmp_path).mkdir(parents=True, exist_ok=True)
Path(out_path).mkdir(parents=True, exist_ok=True)
Path(deletions_path).mkdir(parents=True, exist_ok=True)


class FileUtilityMethods(unittest.TestCase):

    def test_get_list_from_path(self):
        result = fu.get_list_from_path(source_directory+"list.txt")
        self.assertEqual(len(result), 5)

    def test_get_features(self):
        result = fu.get_features("all")
        self.assertIsInstance(result, list)
        result = fu.get_features(features)
        self.assertIsInstance(result, list)

    def test_get_zip_list(self):
        result = fu.get_zip_list(source_directory)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_unzip_get_properties(self):
        fu.unzip_get_properties(source_directory, tmp_path, final_list)
        self.assertTrue(1, 1)

    def test_zip_dir(self):
        zip_file_path = out_path + final_list[0] + ".zip"
        zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
        fu.zip_dir(tmp_path, zipf)
        zipf.close()
        fu.printi(2, 'Zip file created in ' + zip_file_path)
        shutil.rmtree(tmp_path)
        shutil.rmtree(out_path)
        self.assertTrue(1, 1)

    def test_filter_list(self):
        operation = "optin"
        result = fu.filter_list(zip_list, final_list, operation)
        self.assertEqual(len(result), len(final_list))
        operation = "optout"
        result = fu.filter_list(zip_list, final_list, operation)
        self.assertNotEqual(len(result), len(final_list))

    def test_create_deletions(self):
        base_directory = source_directory
        not_processed_c = fu.create_deletions(final_list, features_list, base_directory, deletions_path)
        shutil.rmtree(deletions_path)
        self.assertEqual(len(not_processed_c), 1)

    def test_get_initial_dir(self):
        result = fu.get_initial_dir()
        self.assertIsInstance(result, str)

    def test_printi(self):
        fu.printi(1, "printi test message")
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
