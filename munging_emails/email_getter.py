"""
email_getter.py

This file downloads a file from a server after being provided with a list of links.

- FileCreator: Creates, converts, and fixes the resulting text files.

"""
__author__ = 'alex'
import urllib2
import re
import os
import glob
from subprocess import call

import boto
from boto.s3.key import Key


class FileCreator:
    __download_emails = None
    __pdf_list_file = None
    __where_to_download = None
    __convert = None
    __convert_output_dir = None
    __fix_files = None
    __fixing_chops = None
    __s3 = None

    def __init__(self, **kwargs):
        """
        File creator, gets the emails.

        :param download_emails: Boolean, true if emails should be downloaded, false if not.
        :param pdf_list_file: File location, the list of emails to be downloaded.
        :param where_to_download: Directory, where to store the downloaded PDFs.
        :param convert: Boolean, true if PDFs should be converted.
        :param convert_output_dir: The directory where the text files should go.
        :param fix_files: Boolean, true if files should be fixed.
        :param fixing_chops: A list of three ints, top_chop, header_size, footer_size. Ex. [8,5,5].
        """
        if 'download_emails' in kwargs:
            self.__download_emails = kwargs['download_emails']
        if 'pdf_list_file' in kwargs:
            self.__pdf_list_file = kwargs['pdf_list_file']
        if 'where_to_download' in kwargs:
            self.__where_to_download = kwargs['where_to_download']
        if 'convert' in kwargs:
            self.__convert = kwargs['convert']
        if 'convert_output_dir' in kwargs:
            self.__convert_output_dir = kwargs['convert_output_dir']
        if 'fix_files' in kwargs:
            self.__fix_files = kwargs['fix_files']
        if 'fixing_chops' in kwargs:
            self.__fixing_chops = kwargs['fixing_chops'][:]
        if 'use_s3' in kwargs:
            self.__use_s3 = kwargs['use_s3']

    def start(self):
        """
        Runs everything that you specified.

        :return: None
        :rtype: None
        """
        if self.__use_s3:
            self.__s3 = boto.connect_s3()
        if self.__download_emails:
            self._download_emails()
        if self.__convert:
            self._convert_emails()
        if self.__fix_files:
            self._fix_files(self.__fixing_chops[0], self.__fixing_chops[1], self.__fixing_chops[2])

    def get_download_emails(self):
        """
        Gets the downloaded emails boolean.

        :return: The boolean to see if the emails are set to be downloaded.
        """
        return self.__download_emails

    def get_pdf_list_file(self):
        """
        Gets the file location that holds all of the links to the files to be downloaded.

        :return: A string with the file location for the file containing the links to the pdfs to be downloaded.
        """
        return self.__pdf_list_file

    def get_where_pdf_download_loc(self):
        """
        Gets where the files are to be downloaded.

        :return: The location of where the files are being downloaded
        """
        return self.__where_to_download

    def get_converted(self):
        """
        Gets the boolean to see if the files have been converted.

        :return: Boolean. True if the files were converted, False if not.
        """
        return self.__convert

    def get_convert_output_dir(self):
        """
        Gets the directory where the converted files are stored.

        :return: The string representing the converted output directory.
        """
        return self.__convert_output_dir

    def get_fix_files(self):
        """
        Gets the boolean representing if the files have been fixed or not.

        :return: The boolean representing if the files have been fixed or not.
        """
        return self.__fix_files

    def get_fixing_chops(self):
        """
        Gets the list of the different chop amounts used.

        :return: A list of the different chop amounts used.
        """
        return self.__fixing_chops

    def set_download_emails(self, download_emails):
        """
        Set to download emails.

        :param download_emails: The boolean to set download emails to.
        :return: None.
        """
        self.__download_emails = download_emails

    def set_pdf_list_file(self, pdf_list_file):
        """
        Set the file with the pdf links.

        :param pdf_list_file: The file location.
        :return: None.
        """
        self.__pdf_list_file = pdf_list_file

    def set_where_pdf_download_loc(self, where_pdf_download_loc):
        """
        Set where to download the pdf files.

        :param where_pdf_download_loc: The file location to download.
        :return: None.
        """
        self.__where_to_download = where_pdf_download_loc

    def set_convert_output_dir(self, output_dir):
        """
        Set where the converted files should be outputted to.

        :param output_dir: The directory to change to.
        :return: none.
        """
        self.__convert_output_dir = output_dir

    def set_fix_files(self, fix_files):
        """
        Set whether or not to fix files.

        :param fix_files: Boolean to fix files or not.
        :return: None.
        """
        self.__fix_files = fix_files

    def set_fixing_chops(self, fixing_chops):
        """
        Set the fixing chops (top, header, footer) how much to remove from file when fixed.

        :param fixing_chops: A list with three values: [top_chop, header_chop, footer_chop].
        :return: None.
        """
        self.__fixing_chops = fixing_chops

    def _convert_emails(self):
        """
        Converts emails to text files using pdftotext.

        :return: None
        """
        if self.__use_s3:
            self.__s3 = boto.connect_s3()
            # Get the bucket
            bucket = self.__where_to_download.split('/')[0]
            directory_list = self.__where_to_download.split('/')[1:]
            directory = ''
            # Rebuild the directory
            for part in directory_list:
                directory += (part + "/")
            directory = directory[:-1]
            bucket = self.__s3.get_bucket(bucket)
            pdf_locations = bucket.list(prefix=directory)

            for location in pdf_locations:
                name = location.split('/')[-1]
                pdf = open("temp/temp.pdf", "wb")
                bucket.get_key(location).get_contents_to_file(pdf)
                call(["pdftotext", "-layout", "-enc", "UTF-8", os.path.abspath(pdf.name),
                      "temp/" + name + ".txt"])
                k = Key(bucket)
                where = self.__convert_output_dir.split("/")
                where = where[1:]
                where = where.join("/")
                k.key = where + '/' + name + '.txt'
                text_file = open('temp/' + name + '.txt', "r")
                k.set_contents_from_filename(text_file)

        for f in glob.glob1(os.path.join(self.__where_to_download), "*.pdf"):
            call(["pdftotext", "-layout", "-enc", "UTF-8", os.path.join(self.__where_to_download, f),
                  os.path.join(self.__convert_output_dir, os.path.basename(f) + ".txt")])

    def _download_emails(self):
        """
        Downloads emails to the specified folder from a file containing a new link on each line.

        :return: None, downloads files to folder.
        """

        lines = open(self.__pdf_list_file, 'r').readlines()
        for idx, url in enumerate(lines):
            url_split = url.split("/")
            f = urllib2.urlopen(url)
            data = f.read()
            if self.__use_s3:
                bucket = self.__s3.get_bucket(self.__where_to_download.split("/")[0])
                k = Key(bucket)
                where = self.__where_to_download.split("/")[1:].join("/") + "/"
                name = url_split[-1].split(".")[0] + ".pdf"
                with open("temp/" + name, "wb") as pdf:
                    pdf.write(data)
                    k.key = where + name
                    k.set_contents_from_file(pdf)
            else:
                with open(os.path.join(self.__where_to_download, url_split[-1].split(".")[0] + ".pdf"), "wb") as pdf:
                    pdf.write(data)
                print("\r" + str(float(idx) / len(lines) * 100) + "% done with download."),

    def _fix_files(self, top_chop, header_size, footer_size):
        """
        Fixes a file and makes it left aligned and removes header and footer.

        :param top_chop: How many lines to remove at the top of the file.
        :param header_size: How many lines to remove at the top of a page.
        :param footer_size: How many lines to remove at the bottom of a page.
        :return: None, fixes a file
        """
        redacted_strings = ["B6", "B5", "B4", "B3", "B2"]

        def fix(file_to_fix):
            # Creates list to store lines
            to_write = []

            # Opens the file to read, then wipes it blank to write
            f = open(file_to_fix, "r")
            lines = f.readlines()
            f.close()
            f = open(file_to_fix, "wb+")

            # Adds to the list of lines
            for line in lines:
                to_write.append(line)

            # Deletes the header and footer around the feed return or "\f"
            for idx, l in enumerate(to_write):
                if l.find("\f") != -1:
                    del to_write[idx - footer_size:idx + header_size]

            # Deletes first header
            del to_write[:top_chop]

            # Strips the lines
            for idx, w in enumerate(to_write):
                to_write[idx] = w.strip()

            # Redacted detection
            for idx, w in enumerate(to_write):
                for red_string in redacted_strings:
                    if red_string in w:
                        w = re.sub('  +', ' (This info has been redacted) ', w)
                        w = re.sub(red_string, '', w)
                        to_write[idx] = w

            # Finally it writes to the new file
            for w in to_write:
                f.write(w + "\n")

        if self.__use_s3:
            bucket_name = self.__convert_output_dir.split("/")[0]
            bucket = self.__s3.get_bucket(bucket_name)
            directory = self.__convert_output_dir[1:].join("/") + "/"
            files = bucket.list(prefix=directory)
            for file_name in files:
                with open("temp/temp_fix.txt", "rw") as f:
                    bucket.get_key(file_name).get_contents_to_file(f)
                    fix(f)
                    bucket.get_key(file_name).set_contents_from_file(f)
        else:
            for to_fix in glob.glob(os.path.join(self.__convert_output_dir, "*.txt")):
                fix(to_fix)
