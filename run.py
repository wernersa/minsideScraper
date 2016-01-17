# -*- coding: utf-8 -*-
"""
@author: Tommy & Werner
"""

# ----------------------
# --- IMPORTS
# ----------------------

import os
import mechanicalsoup
import string
from os import listdir
from os.path import isfile, join, isdir
import zipfile
import datetime
import time


import pathlib
import shutil
import pynma
import argparse

# ----------------------
# --- CONSTANTS
# ----------------------

parser = argparse.ArgumentParser(description='''Parse and download files from
                                                minside and extract to dir.''')
parser.add_argument('subjects', metavar='course_names', type=str, nargs='+',
                   help='name of courses (e.g. PROPSY301)')

args = parser.parse_args()

if not args.subjects:
    print("Course names required. Exiting.")


"""
Read the github README for info on environment variables
"""
USERNAME = os.environ['MINSIDE-USERNAME']
PASSWORD = os.environ['MINSIDE-PASS']

SAVE_PATH = os.environ['MINSIDE-FOLDER']

nma = pynma.PyNMA(os.environ['PYNMA-API'])




# ----------------------
# --- SECONDARY FUNCTIONS
# --- Helper functions, not directly associated with main program
# ----------------------

def delete_files_by_extension(path, extensions, recursive=False):
    """
    Recursively deletes all files if their extensions are given.
    """

    extensions = list(extensions)
    deleted_count = 0

    # Delete recursively
    if recursive:
        # Walk the path
        for root, dirs, files in os.walk(path):
            for file in files:
                if get_file_exension(file) in extensions:

                    file_path = os.path.join(root,file)
                    try:
                        os.remove(file_path)
                    except PermissionError as e:
                        print('ERROR:', e)
                    deleted_count += 1

    # Not do go recursively into folder structure
    # when looking for files
    else:
        for file in files_in_dir(path):
            if get_file_exension(file) in extensions:

                file_path = os.path.join(path,file)
                try:
                    os.remove(file_path)
                except PermissionError as e:
                    print('ERROR:', e)
                deleted_count += 1

    return deleted_count


def get_file_exension(string):
    """
    Returns the file extension.
    
    get_file_exension('new.document.txt')
    
    will return 'txt'
    """

    for index, char in enumerate(reversed(string)):
        if char == '.':
            break

    return string[-index:]


def delete_empy_directories(root_directory):
    """
    Recursively deletes directories which have no sub-directories
    and no files.
    """

    # Cannot delete if it does not exist
    if not os.path.exists(root_directory):
        return 0

    deleted_count = 0
    for root, dirs, files in os.walk(root_directory):

        if len(dirs) == 0 and len(files) == 0:
            os.rmdir(root)
            deleted_count += 1

    return deleted_count


def files_in_dir(path):
    """
    Returns a list of FILES in a directory.
    
    Not not include sub-directories.
    """
    return [f for f in listdir(path) if isfile(join(path, f))]


def subdirs_in_dir(path):
    """
    Returns a list of FILES in a directory.
    
    Not not include sub-directories.
    """
    return [f for f in listdir(path) if isdir(join(path, f))]


def sanitize_text(input_string):
    """
    Removes special characters.
    Replaces some characters with underscore.
    """
    all_strings = string.ascii_letters + '1234567890'
    output_string = ''
    for char in input_string:
        if char in all_strings:
            output_string += char

        if char in [' ', '_']:
            output_string += '_'

    return output_string.strip('_')


def create_dir(directory):
    """
    Creates a directory if it does not exist
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


# ----------------------
# --- PRIMARY FUNCTIONS
# --- Primary functions, directly associated with main program
# ----------------------

def login(browser):
    """
    Logs in, returns the index page.
    """

    url = 'https://miside.uib.no/'

    # Get the page, find the form
    login_page = browser.get(url)
    login_form = login_page.soup.find('form')

    # Input the data, submit the form
    login_form.select("#email")[0]['value'] = USERNAME
    login_form.select("#password")[0]['value'] = PASSWORD
    page2 = browser.submit(login_form, login_page.url)

    return page2


def join_subject(browser, subject_name):
    """
    Join all earlier semesters of a subject.
    """

    counter = 0
    results_url = 'https://miside.uib.no/dotlrn/manage-memberships?search_text={}'.format(subject_name)
    results_page = browser.get(results_url)
    for tr in results_page.soup.find_all('tr'):

        # Check that the <tr> contain the join button
        if subject_name not in tr.text:
            continue

        # Assume there is a title, if not, skip it
        try:
            tr.a['title']
        except:
            continue

        if tr.a['title'] != 'Bli medlem':
            continue

        # Get registration link
        registration_link = tr.a['href']
        base_url = 'https://miside.uib.no/dotlrn/'

        # Join the subject
        browser.get(base_url + registration_link)
        counter += 1

    print('Joined {} earlier courses for {}'.format(counter, subject_name))
    return counter


def confirm_unsub(browser, unsub_link):
    """
    Confirms that we wish to unsubscribe to a subject.
    """
    unsub_confirm_page = browser.get(unsub_link)

    confirm_form = unsub_confirm_page.soup.find('form')

    if confirm_form is None:
        return False
    if confirm_form['action'] == 'deregister':
        browser.submit(confirm_form, unsub_confirm_page.url)
        return True
    return False


def leave_subject(browser, subject_name):
    """
    Leaves all instances of a subject.
    """
    memberships_url = 'https://miside.uib.no/dotlrn/manage-memberships'
    memberships_page = browser.get(memberships_url)
    counter = 0
    for tr in memberships_page.soup.find_all('tr'):
        # Make sure it's the right kind of <tr> element
        if subject_name not in tr.text:
            continue

        # Assume there is a title, if not, skip it
        try:
            tr.a['title']
        except:
            continue

        if tr.a['title'] != 'Dropp medlemskap':
            continue

        # Get URL, drop subjects
        unsub_link = tr.a['href']
        base_url = 'https://miside.uib.no'
        if confirm_unsub(browser, base_url + unsub_link):
            counter += 1
        else:
            print(' ERROR dropping subject:', subject_name)

    print('Left {} earlier courses for {}'.format(counter, subject_name))
    return counter


def number_of_files(browser, course_url):
    """
    Returns the number of files for a course url.
    """

    # Go to page
    files_url = course_url + '?page_num=2'
    files_page = browser.get(files_url)

    # Get course name
    course_name = files_page.soup.title.text.strip().encode('utf-8')

    # Iterate, count number of files
    files_count = 0
    for td in files_page.soup.find_all('td'):
        stripped_text = td.text.strip()
        if 'filer' not in stripped_text:
            continue
        if len(stripped_text) > 10:
            continue

        try:
            integer, text = stripped_text.split('f')
            files_count += int(integer)
        except:
            pass

    return files_count


def save_response(reponse, path):
    """
    Saves a reponse object.
    """

    if reponse.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in reponse:
                file.write(chunk)
    return True


def save_course_zip(browser, course_url, subject_name):
    """
    Saves a zip file from a course URL.
    """

    # Create a save path if it does not exist
    save_path = os.path.join(SAVE_PATH,subject_name)
    create_dir(save_path)

    # Get url for files, enter, get download link
    files_url = course_url + '?page_num=2'
    files_page = browser.get(files_url)
    course_title = sanitize_text(files_page.soup.title.text.strip())
    for a in files_page.soup.find_all('a'):
        if a.text == 'Last ned et arkiv av denne mappen':
            break

    base_url = 'https://miside.uib.no'
    download_url = base_url + a['href']

    # Enter download link, get response
    response = browser.get(download_url, stream=True)
    save_path = os.path.join(save_path,(course_title + '.zip'))

    # Save the zip file
    save_response(response, save_path)
    return True


def course_urls(browser, subject_name):
    """
    Returns course URLs for courses we are member of
    for MAT111 the following would be returned:
        ...
        url for mat111 spring
        url for mat 111 fall
        ...
    """
    memberships_url = 'https://miside.uib.no/dotlrn/manage-memberships'
    memberships_page = browser.get(memberships_url)
    for tr in memberships_page.soup.find_all('tr'):
        # Make sure it's the right kind of <tr> element
        if subject_name not in tr.text:
            continue
        for a in tr.find_all('a'):
            if subject_name in a.text:
                yield 'https://miside.uib.no' + a['href']


def removed_files(to_unzip):
    """
    Remove older files from list of files.
    Keep the newer versions.
    """
    filenames = [f for f, t in to_unzip]
    removed_count = 0
    for data in to_unzip[:]:
        name, zipped_time = data
        # Directory, we continue along
        if name[-1] == '/':
            continue
        # No duplicate, we continue along
        if filenames.count(name) <= 1:
            continue

        # We have a conflict. Keep the newest
        conflicting_files = [(f, t) for f, t in to_unzip if f == name]
        conflicting_files.sort(key=lambda item: item[1])

        # Remove all except the newest file
        for to_remove in conflicting_files[:-1]:
            to_unzip.remove(to_remove)
            removed_count += 1

    return to_unzip, removed_count


def unzip_and_clean_up(subject_name):
    """
    1) Get all zipped directories
    2) Go into every file. If there is a duplicate, keep latest
    3) Unzip every directory
    4) Delete empty subdirectories
    """


    # Path for the downloaded files
    path = os.path.join(SAVE_PATH,subject_name)

    # If the path does not exist, return immediately 
    if not os.path.exists(path):
        return 0, 0

    # Get all zipped files in the path
    files = files_in_dir(path)
    files = [f for f in files if '.zip' in f]
    num_files = len(files)

    # A list of files to unzip
    to_unzip = []


    # Iterate over all the zipped files in the directory, getting all sub-files
    for zipped_file in files:

        # Open the zipped file
        file_handle = open(os.path.join(path,zipped_file), 'rb')

        # Attempt to open. Skip if there are errors with the .zip file
        try:
            zipped = zipfile.ZipFile(file_handle)
        except:
            file_handle.close()
            continue

        # Iterate over all the zipped files
        for name in zipped.namelist():
            # Get date information, add to list
            file_info = zipped.getinfo(name)
            zipped_time = datetime.datetime(*file_info.date_time)
            
            #file_info.file_size
            to_unzip.append((name, zipped_time))

        file_handle.close()


    # Remove older versions of files
    files_count_before = len(to_unzip)
    to_unzip, removed_count = removed_files(to_unzip)
    files_count_after = len(to_unzip)
    diff = files_count_before - files_count_after
    #if diff > 0:
    #    print('A total of {} files will not be unzipped. Newer versions exist.\n'.format(diff))


    # Do the unzipping
    unique_filenames = []
    error_count = 0
    global_files_count = 0
    existing_count = 0
    # Iterate over all the zipped files in the directory
    for index, zipped_file in enumerate(files):
        if(num_files > 1):
            print('Working with directory number number {} / {}:\n  {}'.format(index + 1, num_files, zipped_file))
        files_count = 0

        fh = open(os.path.join(path,zipped_file), 'rb')
        # Attempt to open. Skip if there are errors with the .zip file
        try:
            z = zipfile.ZipFile(fh)
        except:
            fh.close()
            print('   -- ERROR with file: ', zipped_file)
            continue

        # Iterate over all the zipped files
        for name in z.namelist():
            #Remove the first relative directory
            new_name = pathlib.Path(name.encode('utf-8'))
            new_name = pathlib.Path(*new_name.parts[1:])
            
            #If this is the first directory, which we removed, don't do anything
            if str(new_name) == ".":
                continue
            
            file_path = os.path.join(path, str(new_name))
            
            
            #For creating directories
            if not os.path.basename(name):
                folder = os.path.join(path, str(new_name))
                if not os.path.exists(folder):
                    os.makedirs(folder)
                continue
            
            #Check if the file already exists:
            if os.path.isfile(file_path):
                existing_count += 1
                continue
            
            file_info = z.getinfo(name)
            zipped_time = datetime.datetime(*file_info.date_time)

            # We do not unzip, a newer versions exists
            if (name, zipped_time) not in to_unzip:
                continue

            # Attempt to extract the file
            try:
                source = z.open(name)
                target = open(file_path, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
                files_count += 1
                unique_filenames.append(os.path.basename(name))
            except:
                error_count += 1

        fh.close()
        global_files_count += files_count

    delete_empy_directories(path)

    return global_files_count, error_count, unique_filenames


def clean_zip_from_dl_directory():
    extension = 'zip'

    # To through all folders
    deleted_count = 0
    for subdir in subdirs_in_dir(SAVE_PATH):
        # Delete all zip folders, but we do not go recursively into folder
        # strucutre, as there can be zip files within zip files!
        full_path = os.path.join(SAVE_PATH,subdir)
        deleted_count += delete_files_by_extension(full_path, (extension,),
                                                   recursive=False)

    return deleted_count


def main(subjects):
    start_time = time.time()
    joined = False

    # Initialize the browser
    browser = mechanicalsoup.Browser()

    # Log in to MinSide
    login(browser)
    
    tot_successful = 0
    
    subjects = [{'name':x} for x in subjects]
    
    for subject in subjects:
        
        #INIT: First run
        if not os.path.exists(os.path.join(SAVE_PATH,subject['name'])):  
            # Sign up for all earlier courses
            joined = True
            join_subject(browser, subject['name'])
    
        # Download files, require at least 'num_files_required'
        num_files_required = 5
        subject['courses'] = list(course_urls(browser, subject['name']))
    
        for course_url in subject['courses']:
    
            # Skip if there are not enough files in directory
            if number_of_files(browser, course_url) < num_files_required:
                continue
    
            # Found enough files, download the zip
            save_course_zip(browser, course_url, subject['name'])
    
        # Finally, remove self from all courses
        if joined:
            leave_subject(browser, subject['name'])
    
        # Unzip and clean up the files
        subject['successful'], subject['errors'], subject['unique_filenames'] = unzip_and_clean_up(subject['name'])
        
        tot_successful += subject['successful']
    
        # Delete zipped files, now that they are unzipped
        clean_zip_from_dl_directory()
    
        subject['runtime'] = (time.time() - start_time)
    
    successful_subjects = [subject for subject in subjects if subject['successful'] > 0]
    successful_subjects_names = [subject['name'] for subject in successful_subjects]
    
    if tot_successful > 10:
        out = "Scraperen har lastet ned {} nye filer. ".format(tot_successful)
        if len(successful_subjects) > 1:
            for subject in successful_subjects:
                out = out + "{}: {} filer. ".format(subject['name'],subject['successful'])
        nma.push("Minside Scraper",",".join(successful_subjects_names), out)
        print(out)
    elif tot_successful > 0:
        out = ""
        for subject in successful_subjects:
            out = "{}: {} . ".format(subject['name'],",".join(subject['unique_filenames']))   
        nma.push("Minside Scraper",",".join(successful_subjects_names),out)
        print(out)
        
        
if __name__ == '__main__':
    main(args.subjects)
            
            