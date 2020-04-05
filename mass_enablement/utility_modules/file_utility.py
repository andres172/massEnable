# -*- coding: utf-8 -*-
import os
import tkinter as tk
import glob
import zipfile
import shutil
from shutil import copyfile
from tkinter import filedialog
import xml.etree.ElementTree as ET
import platform
import sys
import logging
from properties_modules import properties as prop
from program_flow_modules import error_handler as eh
from pathlib import Path
import re
from os import path

logging.basicConfig(filename=os.curdir + '/mass_enable.log',
                    format='%(levelname)s %(asctime)s :: %(message)s',
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
templates_folder = os.curdir + '/templates/'


# prompts the select directory dialog and returns as string
def get_directory(prompt_type, message):
    root = tk.Tk()
    root.withdraw()
    printi(1, message)
    printi(1, "Select " + prompt_type + " directory.")
    path = filedialog.askdirectory(initialdir=get_initial_dir(), title="> Select " + prompt_type + " Directory")
    if (path == '' or path is None) and prompt_type == 'Input':
        eh.error("*** ERROR: Folder is obligatory! ***")
    if (path == '' or path is None) and prompt_type == 'Output':
        printi(1, "No output folder selected. Default will be used.")
        path = os.path.abspath(os.getcwd())
    printi(2, path)
    return path


# prompts the select directory dialog and returns as string
def get_file_list(prompt_type, message):
    root = tk.Tk()
    root.withdraw()
    printi(1, message)
    printi(1, "Select " + prompt_type + " File.")
    file_path = filedialog.askopenfile(initialdir=get_initial_dir(), title="> Select " + prompt_type + " File")
    if file_path == '' or file_path is None:
        eh.error("*** ERROR: An input file is obligatory! ***")
    printi(2, file_path.name)
    list_result = get_list_from_path(file_path.name)
    printi(2, list_result)
    return list_result


def get_list_from_path(path):
    with open(path, 'r') as f:
        list_result = [line.strip() for line in f]
    if len(list_result) == 0:
        eh.error("*** ERROR: Input File list cannot be EMPTY! ***")
    return list_result


# gets features depending on argument
def validate_templates_folder():
    printi(1, "Validating templates folder...")
    templates_dir_list = os.listdir(templates_folder)
    # folder empty
    if len(templates_dir_list) == 0:
        eh.error("*** ERROR: Templates folder is empty! ***")
    missing_elements = "\n"
    # _empty properties
    regex = "[_].*properties"
    r = re.compile(regex)
    if not any(r.match(item) for item in templates_dir_list):
        printi(2, "No '_empty.properties' file found!")
        missing_elements = missing_elements + "\t\t_EMPTY.PROPERTIES FILE\n"
    # properties
    regex = "^(?!_).*properties"
    r = re.compile(regex)
    if not any(r.match(item) for item in templates_dir_list):
        printi(2, "No Properties files found!")
        missing_elements = missing_elements + "\t\tPROPERTIES FILES\n"
    # deletions.xml
    regex = "deletions.xml"
    r = re.compile(regex)
    if not any(r.match(item) for item in templates_dir_list):
        printi(2, "No 'deletions.xml' file found!")
        missing_elements = missing_elements + "\t\tDELETIONS.XML FILE\n"
    # exclusions
    regex = "exclusions"
    r = re.compile(regex)
    if not any(r.match(item) for item in templates_dir_list):
        printi(2, "No 'exclusions' folder found!")
        missing_elements = missing_elements + "\t\tEXCLUSIONS FOLDER\n"

    if missing_elements and not missing_elements == "\n":
        eh.error("*** ERROR: Templates folder inconsistent. The following elements are missing: ***" +
                 missing_elements)


def get_features(feature):
    # templates folder can only hold .properties and .xml files and exclusions folder
    clean_templates_folder()
    # check if templates folder is not corrupted
    validate_templates_folder()
    templates_features = [os.path.splitext(val)[0][12:] for val in glob.glob(os.curdir + '/templates/[!_]*.properties')]
    if feature is None:
        printi(1, "Displaying list of available features:")
        printi(2, templates_features)
        eh.error("")
    elif feature == 'all':
        features = templates_features
        if len(features) == 0:
            eh.error("*** ERROR: Features list is empty! ***")
    else:
        features = feature.split(",")
        validate_features_exist(features)
    return features


def clean_templates_folder():
    printi(1, "Cleaning templates folder...")
    # folder exists
    if not path.exists(templates_folder):
        eh.error("*** ERROR: Templates folder is missing! ***")
    templates_dir_list = os.listdir(templates_folder)
    for item in templates_dir_list:
        if item.endswith(".properties") or item.endswith(".xml") or item == "exclusions":
            continue
        else:
            printi(2, "Removing: " + item)
            os.remove(os.path.join(templates_folder, item))


def validate_features_exist(features):
    printi(1, "Validating inputted features...")
    templates_features = [os.path.splitext(val)[0][12:] for val in glob.glob(os.curdir + '/templates/[!_]*.properties',
                                                                             recursive=False)]
    if set(features) <= set(templates_features):
        printi(2, "Features OK!")
    else:
        printi(3, features)
        printi(2, "*** ERROR: The selected feature(s) are not available. Please use any of the following available"
                  " features: ***")
        printi(3, templates_features)
        eh.error("*** ERROR: Feature(s) not available. ***")


# get list of zip files
def get_zip_list(source_directory):
    zip_list = [os.path.basename(val)[:-4] for val in glob.glob(source_directory + '/*.zip')]
    if len(zip_list) == 0:
        eh.error("*** ERROR: There are no zip files in selected input folder. ***")
    return zip_list


# unzip all files from source and get properties file into temp dir
def unzip_get_properties(source_directory, tmp_path, final_list):
    printi(1, "Unzipping properties files...")
    for fis_name in final_list:
        zip_path = source_directory + '/' + fis_name + '.zip'
        with zipfile.ZipFile(zip_path) as z:
            try:
                with z.open('META-INF/mf-cfgmgmt/' + fis_name + '.properties', mode='r') as zf, \
                        open(tmp_path + fis_name + '.properties', 'wb') as f:
                    shutil.copyfileobj(zf, f)
            except KeyError as e:
                printi(2, fis_name + ".zip KeyError: " + str(e))


# create a .zip file from the directory
def zip_dir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


# returns the resulting list according to operation selected
def filter_list(zip_list, fi_list, operation):
    remove_list = []
    final_list = []
    if operation == 'optout':
        for zip in zip_list:
            for fi in fi_list:
                if fi == zip:
                    remove_list.append(fi)
        final_list = [x for x in zip_list if x not in remove_list]
    else:
        validate_final_list(fi_list, zip_list)
        final_list = set(zip_list) & set(fi_list)
    if len(final_list) == 0:
        eh.error("*** ERROR: FIS-to-Process list is empty. Please check your input file and directory! ***")
    return final_list


# if opt-in or deletions, validate the complete list exists in zip file list
def validate_final_list(fi_list, zip_list):
    printi(1, "Validating if all elements from input list exist for the list of zip files...")
    # perform validation
    if all(elem in zip_list for elem in fi_list):
        printi(2, "Validation OK!")
    else:
        # if there is a mismatch, show elements and exit script
        difference_list = list(set(fi_list).difference(zip_list))
        printi(2, "ERROR: Validation NOT OK")
        printi(2, "The following", str(len(difference_list)), "FI were missing in the input directory:")
        for elem in difference_list:
            printi(3, elem)
        printi(2, "Please, verify your zip files and try again!")
        eh.error("*** ERROR: Mismatch between FI list and zip files found. ***")


def create_deletions(final_list, features, base_directory, deletions_path):
    printi(1, '*** Starting deletion files generation process ***')
    not_processed_c = []
    # get properties from features
    property_list = prop.get_properties(features)
    # get excluded properties for deletion
    exclusions = get_list_from_path(os.curdir + '/templates/exclusions/deletions.txt')
    printi(2, 'Found ' + str(len(exclusions)) + ' deletion exclusion(s):')
    printi(3, exclusions)
    filtered_list = [x for x in property_list if x not in exclusions]
    printi(2, 'Properties to be added in deletion.xml:')
    printi(3, filtered_list)
    print()
    if len(filtered_list) == 0:
        printi(2, 'ERROR: There are no properties to be added!')
        eh.error("*** ERROR: At least ONE property from Features should be specified for the process. ***")
    Path(deletions_path).mkdir(parents=True, exist_ok=True)
    for fis in final_list:
        try:
            printi(2, 'Processing ' + fis.upper() + ' FI...')
            # initialize file
            tmp_file = os.curdir + '/META-INF/mf-cfgmgmt/deletions.xml'
            copyfile(os.curdir + '/templates/deletions.xml', tmp_file)
            for property in filtered_list:
                # add properties to xml
                tree = ET.parse(tmp_file)
                root = tree.getroot()
                attrib = {'name': property}
                for properties in root.findall('properties'):
                    element = properties.makeelement('property', attrib)
                    properties.append(element)
                    tree.write(tmp_file)
            # create zip file
            zipf = zipfile.ZipFile(deletions_path + fis + '.zip', 'w', zipfile.ZIP_DEFLATED)
            zip_dir(base_directory, zipf)
            zipf.close()
            printi(3, "File " + deletions_path + fis + ".zip created.")
        except EnvironmentError:
            not_processed_c.append(fis)
            continue
    print()
    if len(not_processed_c) > 0:
        printi(1, "The following FIs were not processed:")
        printi(2, not_processed_c)
    printi(1, "Deletion files generation process completed.")
    return not_processed_c


def get_initial_dir():
    current_system = platform.system()
    initial_dir = ''
    if current_system == 'Windows':
        initial_dir = 'C:/'
    elif current_system == 'Linux' or current_system == 'Darwin':
        initial_dir = '/'
    return initial_dir


def printi(indent_depth, text, *args):
    indent = '\t' * indent_depth
    if len(args) == 0:
        # print('\t' * indent_depth, text)
        if type(text) is list:
            return logging.info(indent + '[' + ', '.join(map(str, text)) + ']')
        else:
            return logging.info(indent + text)
    else:
        for arg in args:
            text = text + ' ' + arg
        return logging.info(indent + text)
