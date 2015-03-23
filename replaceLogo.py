#! /usr/bin/python

# Takes an .html report file (MAXrm)
# Replaces the logo and removes undesired links/images.
# written for python 2.7

from bs4 import BeautifulSoup as bsoup
from sys import argv
from os import path
import re

script_loc = path.abspath(argv[0])
script_dir = path.dirname(script_loc)
company_logo_loc = path.abspath(path.join(script_dir, 'data/uiTechLogo.gif'))

def usage():
    print """
Usage: %s INPUTFILE [OUTPUTFILE] 
    Modifies INPUTFILE, replacing logo and removing undesired elements.
    Overwrites INPUTFILE or writes to OUTPUTFILE. Intended for use on html/xml.
""" % path.basename(argv[0])

def replace_attr_value(soup_object, target_attr, attr_val_old, attr_val_new):
    """Takes target_attribute, search_value, and replace_value and replaces matching attribute='search_value' with replace_value.
    Matches ^ATTR_VAL_OLD(.*$), which assumes attr_val_old starts at the beginning of the string.
    Captures everything else from the end of attr_val_old to the end of string, if anything, and concatenates the captured group to the end of attr_val_new."""
    
    old_re_obj = re.compile(r'\A%s(.*$)' % attr_val_old, re.I)
    old_attr_dict = {'%s' % target_attr: old_re_obj}
    
    new_re_obj = re.compile(attr_val_new, re.I)
    new_attr_dict = {'%s' % target_attr: new_re_obj}
    
    new_tags = soup_object.find_all(attrs=new_attr_dict)
    old_tags = soup_object.find_all(attrs=old_attr_dict)
    
    if len(new_tags) != 0:
        print 'Already exists: '   
        for item in new_tags:
            print item
     
    if len(old_tags) == 0:
        print 'Not found: ', attr_val_old
         
    else:
        print 'Replacing: '
        for item in old_tags:
            old_match = old_re_obj.match(item[target_attr])
            if old_match != None:
                print 'Old: ', item
                item[target_attr] = attr_val_new + old_match.group(1)
                print 'New: ', item 
    
    # legacy code, did not capture groups after attr_val_old
    """
    if alt_tag != None:
        print 'Already exists: ', alt_tag
    
    elif tag == None:
        print 'Not found: ', attr_dict
   
    else:
        tag[target_attr] = attr_val_new
        print 'Old: ', attr_val_old 
        print 'New: ', tag
    """
def strip_attr_line(soup_object, target_attr, attr_val):
    """Take target_attribute and target_value and destroy all matching (case-insensitive). Warning: Deletes matches regardless of tag. Also deletes match children."""
    re_obj = re.compile(attr_val, re.I)
    attr_dict = {'%s' % target_attr: re_obj}
    tags = soup_object.find_all(attrs=attr_dict)
    print 'Found: %d' % len(tags)
    if len(tags) != 0:
        print 'Removing: '
    for item in tags:
        print item
        item.decompose()

def strip_tags(soup_object, target_tag, target_attr=None):
    tags = soup_object.find_all(target_tag)
    print 'I\'m looking for %s', target_tag
    if len(tags) != 0:
        remove_count = 0
        left_count = 0
        remove_list = []

        for item in tags:
            print 'start loop'
            
            if item.b:
                print 'NOT removing: ', item
                left_count += 1
            else:
                # no idea why append(item) puts '<NONE></NONE>' in the list
                remove_list.append(repr(item))
                item.decompose()
                remove_count += 1
        print 'Removed: %d' % remove_count
       
        for item in remove_list:
            print item
        
        if remove_count + left_count != len(tags):
            print 'WARNING: __main__.strip_tags\n remove_count + left_count != found tags.'
            print 'The output file is may contain unexpected results.'
            raw_input('Press any key to continue: ')

    else:
        print 'Not found: ', target_tag

def writeFile(output_file, data):
    with open(output_file, 'w') as f:
        f.write(data)
        f.close()

def digest_soup(soup_object):
    """Grouping of calls to process and modify file data."""
    print 'Processing:'
    
    print '\n# replace header logo'
    replace_attr_value(soup_object, 'src', 'https://dashboard.systemmonitor.us/customisation/reseller/0/icon.gif', company_logo_loc)
    
    print '\n# replace imcomplete image links'
    replace_attr_value(soup_object, 'src', 'images/silk/', 'https://dashboard.systemmonitor.us/images/silk/')
    
    print '\n# remove external link images' # Patch reports
    strip_attr_line(soup_object, 'src', 'external-link')

    print '\n# remove footer tag line'
    strip_attr_line(soup_object, 'class', 'ReportFooter')

    print '\n# remove links' # Critical Events reports
    strip_tags(soup_object, 'a')

    print ''

def main(argv):
    if len(argv) > 3:
        print 'Too many arguments provided on command line.'
        usage()
        exit(99)

    try:
        input_file_loc = argv[1]
        
        if path.isfile(input_file_loc) != True:
            print '%r does not appear to be a valid file' % input_file_loc
            usage()
            exit(99)
    except IndexError:
        print 'No files specified.'
        usage()
        exit(99)

    try:
        output_file_loc = path.join(script_dir, argv[2])
    except IndexError:
        output_file_loc = input_file_loc

        print '\nNo output file specified on CLI. Using default.\nOutput file will be %s\n' % output_file_loc

    def abs_path(rel_path):
        return path.abspath(rel_path)

    with open(input_file_loc) as f:
        file_data = f.read()
        f.close()

    soup_object = bsoup(file_data)

    org_encoding = soup_object.original_encoding
     
    digest_soup(soup_object)

    edited_data = soup_object.prettify(org_encoding)

    writeFile(output_file_loc, edited_data)

if __name__ == '__main__':
    main(argv)

# legacy code before replace_attr_value with subtly different functionality
"""

search_string = 'ReportLogo'

desired_tag = soup_object.find('div', search_string)

if desired_tag == None:
    print 'Did not find a %s class in %r. Please check your source.' % (search_string, input_file_loc)
    exit(99)

tag_to_edit = desired_tag.contents[0]

tag_to_edit['src'] = abs_path(company_logo_loc)
"""


