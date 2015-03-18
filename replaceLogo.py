#! /usr/bin/python

# search through the provided .html for the search_string class
# if found, replace the subsequent img src with the company logo
# write out new .html file 

# written for python 2.7

from bs4 import BeautifulSoup as bsoup
from sys import argv
import os.path, re

print "\n\n*************"

search_string = 'ReportLogo'

if len(argv) > 3:
    print 'Too many arguments provided on command line.'
    exit(99)

script_loc = os.path.abspath(argv[0])
script_dir = os.path.dirname(script_loc)

company_logo_loc = os.path.abspath(os.path.join(script_dir, 'data/uiTechLogo.gif'))

try:
    input_file_loc = argv[1]
    
    if os.path.isfile(input_file_loc) != True:
        print '%r does not appear to be a valid file' % input_file_loc
except IndexError:
    print 'No files specified. Exiting.'
    exit(99)

try:
    output_file_loc = os.path.join(script_dir, argv[2])
except IndexError:
    output_file_loc = input_file_loc
    print 'No output file specified. Default output file is %s' % output_file_loc

def abs_path(rel_path):
    return os.path.abspath(rel_path)

with open(input_file_loc) as f:
    file_data = f.read()
    f.close()

soup_object = bsoup(file_data)

org_encoding = soup_object.original_encoding
   
def replace_attr_value(target_attr, attr_val_old, attr_val_new):
    """Takes target_attribute, search_value, and replace_value to find only first matching attribute='value' pair and replace with replace_value."""
    attr_dict = {'%s' % target_attr: '%s' % attr_val_old}
    print attr_dict
    tag = soup_object.find(attrs=attr_dict)
    tag[target_attr] = attr_val_new
    print tag

def strip_attr_line(target_attr, attr_val):
    """Take target_attribute and target_value and destroy all matching (case-insensitive). Warning: Deletes matches regardless of tag. Also deletes match children."""
    re_obj = re.compile(attr_val, re.I)
    attr_dict = {'%s' % target_attr: re_obj}
    tags = soup_object.find_all(attrs=attr_dict)
    print 'Removing: %d' % len(tags)
    for item in tags:
        print item
        item.decompose()

def strip_tags(target_tag, target_attr=None):
    tags = soup_object.find_all(target_tag)
    print 'Processing: %d' % len(tags)
    for item in tags:
       
        if item.b:
            print 'NOT removing: ', item
        else:
            print 'Removing: ', item
            print 'Removing contents:', item.contents
            item.decompose()

print '# replace header logo'
replace_attr_value('src', 'https://dashboard.systemmonitor.us/customisation/reseller/0/icon.gif', company_logo_loc)

print '# remove external link images'
strip_attr_line('src', 'external-link')

print '# remove footer tag line'
strip_attr_line('class', 'ReportFooter')

print '# remove links'
strip_tags('a')

# legacy code before replace_attr_value with subtly different functionality
"""
desired_tag = soup_object.find('div', search_string)

if desired_tag == None:
    print 'Did not find a %s class in %r. Please check your source.' % (search_string, input_file_loc)
    exit(99)

tag_to_edit = desired_tag.contents[0]

tag_to_edit['src'] = abs_path(company_logo_loc)
"""

edited_data = soup_object.prettify(org_encoding)

def writeAllFiles():
    with open(output_file_loc, 'w') as f:
        f.write(edited_data)
        f.close()

writeAllFiles()
