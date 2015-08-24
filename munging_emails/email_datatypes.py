__author__ = 'alex'
from fuzzywuzzy import fuzz
from profile import Contact
import re
import glob
import os


class Email:
    __email_dict = {}
    __has_field = {}
    __previous_replies = []
    __list_of_lines = []

    def __init__(self, list_of_lines):
        """
        Converts an email (represented by a list of lines) into a python dictionary object with fields.

        :param list_of_lines: The individual li to convert to a python dictionary in the form of a list of lines.
        :return: The dictionary object that represents an email with the fields: From, To, Sent, Subject, CC, Attachments, and Body
        """
        if type(self) is type(list_of_lines):
            self.__list_of_lines = list_of_lines.get_raw()
        else:
            self.__list_of_lines = list_of_lines[:]
        to_convert = {'From': "", 'To': "", 'Sent': "", 'Subject': "", 'CC': "", 'Attachments': ""}
        has_field = {'From': False, 'To': False, 'Sent': False, 'Subject': False, 'CC': False, 'Attachments': False}
        body = ""
        for line in self.__list_of_lines:
            line_in_dic = False
            broken_by_spaces = line.split(" ")
            if broken_by_spaces:
                for key in to_convert:
                    if fuzz.ratio(key.lower(), broken_by_spaces[0].lower()) > 50 and to_convert[key] == '':
                        for x in xrange(1, len(broken_by_spaces)):
                            to_convert[key] += broken_by_spaces[x]
                            has_field[key] = True
                            if x != len(broken_by_spaces) - 1:
                                to_convert[key] += " "
                        line_in_dic = True
            if not line_in_dic:
                body += (line + "\n")
        to_convert['Body'] = body
        self.__has_field = has_field
        self.__email_dict = to_convert

    def is_email(self):
        """
        Checks to see if the email contains the fields that would qualify it as an email.

        :return: The boolean representing if it is an email or not.
        """
        return sum([self.get_body() != '', self.get_from() != '', self.get_to() != '', self.get_sent() != '',
                    self.get_subject() != '']) >= 2

    def set_previous_replies(self, lines):
        """
        Sets the previous replies in a thread.

        :param lines: The list of lines to be set as the previous replies.
        :return: None
        """
        self.__previous_replies = lines

    def get_previous_replies(self):
        """
        Gets the previous replies in a thread.

        :return: The list of lines representing the previous replies.
        """
        return self.__previous_replies

    def get_raw(self):
        """
        Gets the raw value of the Email from the objects instantiation.

        :return: The raw list of strings from instantiation.
        """
        return self.__list_of_lines

    def get_from(self):
        """
        Gets the from field of the email

        :return: The from field of the email.
        """
        return self.__email_dict['From']

    def get_to(self):
        """
        Gets the to field of the email.

        :return: The to field of the email.
        """
        return self.__email_dict['To']

    def get_sent(self):
        """
        Gets the sent field of the email. Also works with date field.

        :return: The sent or date field of the email.
        """
        return self.__email_dict['Sent']

    def get_subject(self):
        """
        Gets the subject field of the email.

        :return: The subject field of the email.
        """
        return self.__email_dict['Subject']

    def get_cc(self):
        """
        Gets the CC field of the email.

        :return: The CC field of the email.
        """
        return self.__email_dict['CC']

    def get_attachments(self):
        """
        Gets the attachments names from the attachments field.

        :return: The name(s) of the attachments.
        """
        return self.__email_dict['Attachments']

    def get_body(self):
        """
        Returns the body of the email.

        :return: The body of the email.
        """
        return self.__email_dict['Body']

    def has_from(self):
        """
        Has the from field of the email

        :return: The from field of the email.
        """
        return self.__has_field['From']

    def has_to(self):
        """
        Has the to field of the email.

        :return: The to field of the email.
        """
        return self.__has_field['To']

    def has_sent(self):
        """
        Has the sent field of the email. Also works with date field.

        :return: The sent or date field of the email.
        """
        return self.__has_field['Sent']

    def has_subject(self):
        """
        Has the subject field of the email.

        :return: The subject field of the email.
        """
        return self.__has_field['Subject']

    def has_cc(self):
        """
        Has the CC field of the email.

        :return: The CC field of the email.
        """
        return self.__has_field['CC']

    def has_attachments(self):
        """
        Has the attachments names from the attachments field.

        :return: The name(s) of the attachments.
        """
        return self.__has_field['Attachments']

    def has_body(self):
        """
        Has the body of the email.

        :return: The body of the email.
        """
        return self.__has_field['Body']


class Document:
    __emails = None
    __id = None
    __link = None
    __use_threads = True
    __document_lines = []
    __doc_should_be_checked = False

    def get_pdf_link(self):
        """
        Gets the assigned PDF link.

        :return: String. PDF link.
        """
        return self.__link

    def set_pdf_link(self, link):
        """
        Sets the PDF link.

        :param link: The PDF link to set.
        :return: None.
        """
        self.__link = link

    def get_doc_id(self):
        """
        Gets the assigned document ID.

        :return: String. Doc ID.
        """
        return self.__id

    def set_doc_id(self, doc_id):
        """
        Sets the document ID.

        :param doc_id: The ID to set.
        :return: None.
        """
        self.__id = doc_id

    def doc_should_be_checked(self):
        """
        Gets the boolean value if this document likely has parsing errors.

        :return: Boolean, does this likely contain errors. True if it does, false if it does not.
        """
        if self.__doc_should_be_checked:
            return True
        # Load all contacts in document
        contacts_in_doc = []
        for email in self.__emails:
            # Create an email object from the list of lines.
            email = Email(email)
            contacts_list = [email.get_from()]

            # Add each from contact.
            contacts_in_doc.append(Contact(email.get_from(), "(This info has been redacted)"))
            # Checks to see if there is a "to:" field.
            if email.has_to():
                # Gets the first "to:" field if there are multiple.
                contacts_in_doc.append(Contact(email.get_to().split(";")[0], "(This info has been redacted)"))
                contacts_list.append(email.get_to())
            # Checks to see if there is a "CC:" field.
            if email.has_cc():
                # Gets the first "CC:" field if there are multiple.
                contacts_in_doc.append(Contact(email.get_cc().split(";")[0], "(This info has been redacted)"))
                contacts_list.append(email.get_cc())
            contacts_list = [email.get_from(), email.get_to().split(";")[0], email.get_cc().split(";")[0]]
            for c in [Contact(con, "(This info has been redacted)") for con in contacts_list]:
                if c.is_mangled():
                    return True

        # Loop through the contacts to check if any have issues.
        for contact in contacts_in_doc:
            # Check if the contact is empty, or the string is longer than 55 characters (likely caught a sentence).
            if contact.is_empty() or len(contact.get_raw().replace("(This info has been redacted)", "")) > 60:
                return True

        # No problems were found
        return False

    def __init__(self, document_lines, use_threads, doc_id):
        """
        Creates a document, representing a thread of emails (FW or RE).

        :param document_lines: The lines of the file.
        :param use_threads: Boolean if to break emails up into threads or not.
        :param doc_id: String, the id of the document.
        :return: None
        """
        self.__id = doc_id
        self.__use_threads = use_threads
        self.__document_lines = document_lines
        self.__emails = self._break_into_emails()

    def add_email(self, email):
        """
        Add an email to a document... Haven't found a use for this yet.

        :param email: The email object to add.
        :return: None.
        """
        self.__emails.append(email)

    def __len__(self):
        """
        Gets the number of emails in the document.

        :return: The number of emails in the document.
        """
        return len(self.__emails)

    def __iter__(self):
        """
        The iterable interface: return an iterator from __iter__().
        """
        for email in self.__emails:
            yield Email(email)

    def _break_into_emails(self):
        """
        Turn a document, preferably a list of lines that has already been run through the fix_file method, into a list of emails.

        :return: A list of lists of strings, each entry in the first list represents a list of lines each representing an email.
        """
        lines = self.__document_lines[:]
        email = []
        broken = []
        pos_froms = ["From", "Prom"]
        # pos_sents = ["Sent", "Sant", "5ent", "Sont", "Semt"]
        pos_sents = ["Date", "Sent"]
        pos_fws = ['FW:', 'PIN:']
        pos_res = ['RE:']
        from_locations = []
        if self.__use_threads:
            for idx, line in enumerate(lines):
                if idx < len(lines) - 1:
                    for x in xrange(1, 5):
                        try:
                            if any(pos_from.lower() in lines[idx][0:6].lower() for pos_from in pos_froms) and any(
                                            pos_sent.lower() in
                                            lines[idx + x][0:6].lower() for pos_sent
                                            in
                                            pos_sents):
                                from_locations.append(idx)
                                break
                        except IndexError:
                            self.__doc_should_be_checked = True
                            break
            for idx, line in enumerate(lines):
                for from_location_idx, from_location in enumerate(from_locations):
                    if idx == from_location:
                        try:
                            found_re_or_fw = False
                            for x in xrange(2, 4):
                                if any(pos_fw.lower() in lines[idx + x].lower() for pos_fw in pos_fws):
                                    for l in lines[idx:]:
                                        email.append(re.sub(' +', ' ', l.strip()))
                                    broken.append(email)
                                    email = []
                                    found_re_or_fw = True
                                    break
                                elif any(pos_re.lower() in lines[idx + x].lower() for pos_re in pos_res):
                                    for l in lines[idx:]:
                                        email.append(re.sub(' +', ' ', l.strip()))
                                    broken.append(email)
                                    email = []
                                    found_re_or_fw = True
                                    break
                            if not found_re_or_fw:
                                if from_location_idx < len(from_locations) - 1:
                                    for l in lines[idx:from_locations[from_location_idx + 1]]:
                                        email.append(re.sub(' +', ' ', l.strip()))
                                    broken.append(email)
                                    email = []
                                else:
                                    for l in lines[idx:]:
                                        email.append(re.sub(' +', ' ', l.strip()))
                                broken.append(email)
                                email = []

                        except IndexError:
                            self.__doc_should_be_checked = True
        else:
            for idx, line in enumerate(lines):
                if idx < len(lines) - 1:
                    for x in xrange(1, 5):
                        try:
                            if any(pos_from.lower() in lines[idx][0:6].lower() for pos_from in pos_froms) and any(
                                            pos_sent.lower() in
                                            lines[idx + x][0:6].lower() for pos_sent
                                            in
                                            pos_sents):
                                from_locations.append(idx)
                                break
                        except IndexError:
                            print "Error"
            for idx, line in enumerate(lines):
                for from_location_idx, from_location in enumerate(from_locations):
                    if idx == from_location:
                        if from_location_idx < len(from_locations) - 1:
                            for l in lines[idx:from_locations[from_location_idx + 1]]:
                                email.append(re.sub(' +', ' ', l.strip()))
                            broken.append(email)
                            email = []
                        else:
                            for l in lines[idx:]:
                                email.append(re.sub(' +', ' ', l.strip()))
                        broken.append(email)
                        email = []
        to_return = []
        for email in broken:
            to_return.append(Email(email))
        return filter(None, broken)


class Collection(object):
    __documents_locs = []
    __debug = False
    __use_threads = True

    def __init__(self, *args):
        """
        Creates a streaming object for all of the documents in a folder.

        :param args: TODO
        :return:
        """
        function_input = args[0]
        file_type = args[1]
        if type(function_input) is list:
            self.__documents_locs = function_input[:]
        elif type(function_input) is str:
            for f in glob.glob(os.path.join(function_input, "*" + file_type)):
                if "." not in file_type:
                    if "." not in f:
                        self.__documents_locs.append(f)
                else:
                    self.__documents_locs.append(f)

    def __getitem__(self, item):
        self.__documents_locs = self.__documents_locs[item]
        return self

    def add_document(self, document_loc):
        """
        Adds a document location to the list to iterate through.

        :param document_loc: The location of the document to be added.
        :return: None.
        """
        self.__document_locs.append(document_loc)

    def set_debug(self, debug):
        """
        Sets the debug option.

        :param debug: Boolean, the option to print or not.
        :return: None.
        """
        self.__debug = debug

    def pull_contacts(self):
        """
        Pulls all of the contacts from the collection's to, from, and cc fields.

        :return: The list of contact objects.
        """
        contacts = []
        if self.__debug:
            print "\nPulling all contacts..."
            print "===================================="
        for d in self:
            for email in d:
                contacts.append(Contact(email.get_from(), "(This info has been redacted)"))
                tos = email.get_to().split(";")
                ccs = email.get_cc().split(";")
                for to in tos:
                    contacts.append(Contact(to, "(This info has been redacted)"))
                for cc in ccs:
                    contacts.append(Contact(cc, "(This info has been redacted)"))
        if self.__debug:
            print "\nDone!"
            print "===================================="
        return contacts

    def get_debug(self):
        """
        Gets the debug option

        :return: The debug option
        """
        return self.__debug

    def set_use_threads(self, use_threads):
        """
        Whether or not to use threads in emails

        :param use_threads: Whether or not to use threads.
        :return: None
        """
        self.__use_threads = use_threads

    def get_use_threads(self):
        """
        Gets if the emails are using threads or not.

        :return: The boolean representing using threads or not.
        """
        return self.__use_threads

    def __len__(self):
        return len(self.__documents_locs)

    def __iter__(self):
        _num = 0
        _len_of_docs = len(self)
        for loc in self.__documents_locs:
            with open(loc) as f:
                if self.__debug:
                    print ("\r" + str((float(_num) / _len_of_docs) * 100) + "% done with document iteration."),
                _num += 1
                d = Document(f.readlines(), self.__use_threads, os.path.basename(f.name).split(".")[0])
                yield d
