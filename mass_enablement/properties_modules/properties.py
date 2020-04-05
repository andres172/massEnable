# -*- coding: utf-8 -*-
import os
from utility_modules import file_utility as fu
from pyjavaproperties import Properties
from program_flow_modules import error_handler as eh
import shutil


# create property file from templates
# features define properties templates to use
# operation defines true/false value for property
def process_properties(fis, features, operation, tmp_path, out_path, base_directory):
    properties = Properties()
    properties.load(open(os.curdir+"/templates/_empty.properties"))
    property_count = 0
    for feature in features:
        # get feature.properties
        p = Properties()
        p.load(open("templates/" + feature + ".properties"))
        # properties must be validated against current ones using selected strategy
        # to check which ones include in zip output
        original_properties = Properties()
        original_properties.load(open(tmp_path + fis + ".properties"))
        op_list = []
        for op in original_properties.items():
            op_list.append(op[0])
        fu.printi(3, feature.upper() + " feature properties:")
        # if the properties file has no properties, stop process
        if len(p.items()) == 0:
            shutil.rmtree(base_directory, True)
            shutil.rmtree(out_path, True)
            shutil.rmtree(tmp_path, True)
            fu.printi(2, 'ERROR: There are no properties to be added for feature '+feature.upper()+'!')
            eh.error("*** ERROR: At least ONE property from Features should be specified for the process. ***")
        for prop in p.items():
            out_text = "Property: " + prop[0]
            # check if tuple for prop exists
            if prop[0] in op_list:
                # property exists
                out_text = out_text + " -> Exists in original:"
                if operation == 'optout':
                    # go to next prop
                    fu.printi(4, out_text, "Ignoring property (OPT-OUT).")
                    continue
                if operation == 'optin' and original_properties[prop[0]] == 'false':
                    properties[prop[0]] = validate_rule(prop)
                    fu.printi(4, out_text, "Enabling property with value '"+properties[prop[0]].upper()+"' (OPT-IN).")
                    property_count = property_count + 1
                if operation == 'optin' and not original_properties[prop[0]] == 'false':
                    fu.printi(4, out_text, "Property already enabled (OPT-IN).")
            else:
                # property does not exist
                fu.printi(4, out_text, "-> Adding property.")
                properties[prop[0]] = validate_rule(prop)
                property_count = property_count + 1
    fu.printi(2, "Added "+str(property_count)+" properties")
    return properties


def validate_rule(prop):
    if prop[0] == 'fi.payee.management_entitlement' or prop[0] == 'fi.com.fismobile.wallet_entitlement':
        return 'white-listing'
    else:
        return 'true'


def get_properties(features):
    property_list = []
    for feature in features:
        p = Properties()
        p.load(open("templates/" + feature + ".properties"))
        for prop in p.items():
            property_list.append(prop[0])
    return property_list
