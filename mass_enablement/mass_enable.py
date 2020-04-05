# -*- coding: utf-8 -*-
import os
import zipfile
import shutil
from properties_modules import properties as prop
from utility_modules import file_utility as fu
from program_flow_modules import arguments as arg
from pathlib import Path


if __name__ == '__main__':
    fu.printi(0, "***** MASS ENABLEMENT SCRIPT START *****")
    arguments = arg.get_arguments()
    features = fu.get_features(arguments.feature)
    fu.printi(1, 'Features: [%s]' % ', '.join(map(str, features)))
    operation = 'optin' if arguments.optin else ('optout' if arguments.optout else 'deletion')
    fu.printi(1, "Operation: "+operation)

    # input is file with FI list and input/output directories
    if arguments.path is not None and arguments.path != '':
        paths = arguments.path.split(' ')
        file_path = paths[0]
        fi_list = fu.get_list_from_path(file_path)
        fu.printi(1, "FI input List:")
        fu.printi(2, file_path)
        fu.printi(2, fi_list)
        source_directory = paths[1]
        fu.printi(1, "Zip Files Input Folder:")
        fu.printi(2, source_directory)
        output_directory = paths[2]
        fu.printi(1, "Output Folder:")
        fu.printi(2, output_directory)
    else:
        fi_list = fu.get_file_list('FI List', "Please, select the input file with the list of FI. The file should have"
                                              " a .TXT extension and each element be line separated:")
        source_directory = fu.get_directory('Input',
                                            'Please, select the folder in your computer where the zipped configurations'
                                            ' are located:')
        output_directory = fu.get_directory('Output',
                                            'Please, select the folder in your computer where you want the resulting '
                                            'files to be generated:')
    out_path = output_directory + '/mass_enable_out/'
    deletions_path = output_directory + '/mass_enable_deletions/'
    tmp_path = source_directory+'/tmp/'

    # get list of zips from source
    zip_list = fu.get_zip_list(source_directory)
    fu.printi(1, 'FIs zip found: ' + "[" + ', '.join(map(str, zip_list)) + "]")

    # filter zip file from fis_list according to operation
    final_list = fu.filter_list(zip_list, fi_list, operation)
    fu.printi(1, 'FIs to process: ' + "[" + ', '.join(map(str, final_list)) + "]")

    # create folder structure
    base_directory = "META-INF/"
    complete_directory = base_directory + "mf-cfgmgmt/"
    Path(complete_directory).mkdir(parents=True, exist_ok=True)

    # create temp folder for properties in current zipped fis
    Path(tmp_path).mkdir(parents=True, exist_ok=True)

    not_processed_c = []
    if operation == 'deletion':
        # deletion will create a deletions.xml file
        not_processed_c = fu.create_deletions(final_list, features, base_directory, deletions_path)
    else:
        # create out folder
        Path(out_path).mkdir(parents=True, exist_ok=True)
        # files must be unzipped
        fu.unzip_get_properties(source_directory, tmp_path, final_list)
        # for every fis listed
        # must have templates since the properties are always the same
        # folder and file structure is: META-INF/mf-cfgmgmt/<fi_name>.properties
        # and it must be zipped: <fi_name>.zip
        fu.printi(1, '*** Starting zipped properties generation process ***')
        for fis in final_list:
            try:
                fu.printi(2, 'FI name: ' + fis)
                # create property file from templates
                properties = prop.process_properties(fis, features, operation, tmp_path, out_path, base_directory)
                # create properties file
                new_property_path = complete_directory + fis + '.properties'
                properties.store(open(new_property_path, 'w'))
                # create zip file
                zip_file_path = out_path + fis + '.zip'
                zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
                fu.zip_dir(base_directory, zipf)
                zipf.close()
                fu.printi(2, 'Zip file created in ' + zip_file_path)
                print()
                # remove property from folder for reuse
                os.remove(new_property_path)
            except EnvironmentError:
                not_processed_c.append(fis)
                continue
        fu.printi(1, "Successful: "+str(len(final_list)-len(not_processed_c))+" - Failed: "+str(len(not_processed_c)))
        if len(not_processed_c) > 0:
            fu.printi(1, "The following FIs were not processed:")
            fu.printi(2, not_processed_c)
        fu.printi(1, "Mass enable process completed.")

    shutil.rmtree(base_directory)
    shutil.rmtree(tmp_path)
    fu.printi(1, "Log file saved to: mass_enable.log")
    fu.printi(0, "***** MASS ENABLEMENT SCRIPT EXIT *****")
