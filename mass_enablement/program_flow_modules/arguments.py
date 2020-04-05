# -*- coding: utf-8 -*-
import argparse


# parse python command line arguments
# for example: $ python mass_enable -enable -feature <name>
# arguments must accept: enable/disable, name of the feature
def get_arguments():
    parser = argparse.ArgumentParser("mass_enable", description="*** Mass Enablement of features for FIS ***")
    parser.add_argument("-i", "--optin", help="Enable listed features for the list of FIs with the Opt-In strategy"
                        , action='store_true')
    parser.add_argument("-o", "--optout", help="Enable listed features for the non listed FIs with the Opt-Out"
                                               " strategy."
                        , action='store_true')
    parser.add_argument("-d", "--deletion", help="Remove properties to reverse decision to enable a feature by"
                                                 " generating a deletions.xml file for selected FIs."
                        , action='store_true')
    parser.add_argument("-f", "--feature", help="Insert a feature name to be included. Comma separated features can be"
                                                " listed. Accepted values are properties file names in templates folder"
                                                ": 'add_payee' (Add Payee feature), 'android_biometrics' (Android"
                                                " Biometrics feature), 'app_store_feedback' (App Store Feedback"
                                                " feature), 'ios_biometrics' (Ios Biometrics feature), 'wallet_ui'"
                                                " (Wallet UI feature). 'all' will enable every feature in templates."
                                                " You can also run -f without any value to get the available features"
                                                " list.",
                        required=True, metavar='', action='store', nargs='?')
    parser.add_argument("-p", "--path", help="Specify three paths in this order: input file list, input folder"
                                             " and output folder. Arguments must be enclosed by quotation marks."
                                             " Example: -p \"/fi_list.txt /input_folder /output_folder\"",
                        metavar='')
    args = parser.parse_args()
    if args.feature is None:
        return args
    else:
        if not args.optin and not args.optout and not args.deletion:
            parser.error("Must specify 'Opt-in', 'Opt-out' or 'Deletion' argument!")
        if (args.optin and args.optout) or (args.optin and args.deletion) or (args.optout and args.deletion):
            parser.error("Only one operation can be set in arguments!")
    return args
