# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'
__author__ = 'alex'
import re
from fuzzywuzzy import fuzz
import pickle
import time


class ProfileStorage(object):
    __contacts = []
    __profiles = []
    __pickle_file = None

    def __init__(self, collection, use_pickle_load=False, pickle_file="profile_storage.pickle"):
        """
        Stores and creates profiles from a list of contacts.

        :param collection: The list of contacts.
        :param pickle_file: Where to pickle the data after each pass. Also where to load the data if use_pickle_load is True.
        :param use_pickle_load: If progressed was stopped, you can load from a pickle file on the most recent completed pass.
        :return: None.
        """
        self.__pickle_file = pickle_file

        if not use_pickle_load:
            self.__contacts = collection.pull_contacts()
        else:
            pass
        print "\nStarting profile disambiguation..."
        print "===================================="
        print "Creating initial profiles..."
        self._create_initial_profiles()
        print "Done!"
        print "------------------------------------"

        print "Starting to merge profiles..."
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        start = time.time()
        self._merge_iter()
        print "Total time to merge:", time.time() - start
        print "Length of the profiles after merging:", len(self.__profiles)
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

        print "Done!"
        print "===================================="
        print "Finished profile disambiguation."

    def _create_initial_profiles(self):
        contact_len = len(self.__contacts)
        for cidx, contact in enumerate(self.__contacts):
            print "\r", str(float(cidx) / contact_len * 100) + "% done with initial creation.",
            if not contact.get_name().get_redacted() or not contact.get_email_address().get_redacted():
                if not contact.is_empty() and len(contact.get_raw().replace("(This info has been redacted)", "")) < 60:
                    has_match = False
                    for profile in self.__profiles:
                        if profile.contact_matches_profile(contact):
                            profile.add_contact(contact, True)
                            has_match = True
                            break
                    if not has_match:
                        self.__profiles.append(Profile(contact))
        with open(self.__pickle_file, "w") as f:
            pickle.dump(self.__profiles, f)

    def _merge_rec(self, pass_num):
        profile_list_merged = []
        # if pass_num % 50 == 0:
        # print "----PASS " + str(pass_num) + "----"
        for idx1, pro1 in enumerate(self.__profiles):
            for idx2, pro2 in enumerate(self.__profiles):
                if idx1 != idx2:
                    if pro1.get_average_contact().get_name().compare_to(
                            pro2.get_average_contact().get_name()) > 90 or pro1.get_average_contact().get_email_address(). \
                            compare_to(pro2.get_average_contact().get_email_address()) > 90:
                        merged_profile = Profile()
                        for contact1 in pro1.get_contacts():
                            merged_profile.add_contact(contact1, False)
                        for contact2 in pro2.get_contacts():
                            merged_profile.add_contact(contact2, False)
                        merged_profile._update_average()
                        profile_list_merged.append(merged_profile)
                        for idx_p, profile_not_merged in enumerate(self.__profiles):
                            if idx_p not in [idx1, idx2]:
                                profile_list_merged.insert(0, profile_not_merged)
                        self.__profiles = profile_list_merged
                        return self._merge_rec(pass_num + 1)
        print "-----" + str(pass_num) + " Total Passes-----"

    def _merge_iter(self):
        idx = 0
        while True:
            # if idx % 50 == 0:
            # print "----PASS " + str(idx) + "----"
            idx += 1
            orig_len = len(self.__profiles)
            profile_list_merged = []
            try:
                for idx1, pro1 in enumerate(self.__profiles):
                    for idx2, pro2 in enumerate(self.__profiles):
                        if idx1 != idx2:
                            if pro1.get_average_contact().get_name().compare_to(
                                    pro2.get_average_contact().get_name()) > 90 or pro1.get_average_contact().get_email_address(). \
                                    compare_to(pro2.get_average_contact().get_email_address()) > 90:
                                merged_profile = Profile()
                                for contact1 in pro1.get_contacts():
                                    merged_profile.add_contact(contact1, False)
                                for contact2 in pro2.get_contacts():
                                    merged_profile.add_contact(contact2, False)
                                merged_profile._update_average()
                                profile_list_merged.append(merged_profile)
                                for idx_p, profile_not_merged in enumerate(self.__profiles):
                                    if idx_p not in [idx1, idx2]:
                                        profile_list_merged.insert(0, profile_not_merged)
                                self.__profiles = profile_list_merged
                                raise StopIteration
            except StopIteration:
                continue
            if orig_len == len(self.__profiles):
                break
        print "----" + str(idx) + " Total Passes----"

    def get_profile(self, contact):
        """
        :param contact: The contact to find the matching profile.
        :type contact: Contact
        :return: The profile that matches.
        :rtype: Profile
        """
        for profile in self.__profiles:
            if profile.contact_matches_profile(contact):
                return profile


class Profile(object):
    def __init__(self, *args):
        """
        Stores a profile and creates the most common contact for that person and returns it in a standardized format.

        :return: None.
        """
        if len(args) == 1:
            self.__contacts = [args[0]]
            self.__average_contact = args[0]
        else:
            self.__contacts = []
            self.__average_contact = None

    def add_contact(self, contact, update):
        """
        Adds a contact to the profile regardless of if it matches or not.

        :param contact: The contact to add.
        :param update: The boolean if to update the average. If adding many contacts you know match set to false. Then update after.
        :return: None.
        """
        self.__contacts.append(contact)
        if update:
            self._update_average()

    def get_contacts(self):
        """
        Returns the list of contacts inside of this profile.

        :return: The list of contacts inside of this profile.
        """
        return self.__contacts[:]

    def contact_matches_profile(self, contact_to_compare):
        """
        Checks to see if the contact matches this profile.

        :param contact_to_compare: The contact object to compare with the profile.
        :return: Boolean. True if it does match, False if not.
        """
        if self.__average_contact.get_name().compare_to(contact_to_compare.get_name()) > 90 or self.__average_contact. \
                get_email_address().compare_to(contact_to_compare.get_email_address()) > 90:
            return True
        else:
            return False

    def contact_in_profile(self, contact_to_check):
        """
        Checks to see if a contact is already in the profile.

        :param contact_to_check: The contact to check against the profile.
        :return: Boolean. True if it is inside, False if it is not.
        """
        for contact in self.__contacts[:]:
            if str(contact) == str(contact_to_check):
                return True
        return False

    def _update_average(self):
        """
        Updates the average contact inside of the profile. Done by comparing character by character and taking the one with more than half of the reference.

        :return: None.
        """

        names = [[], [], []]
        email = [[], []]
        name_str = ''
        # Working out average name
        for contact in self.__contacts[:]:
            # First, middle, and last names broken into characters
            names[0].append([char for char in contact.get_name().get_first()])
            names[1].append([char for char in contact.get_name().get_mid_init()])
            names[2].append([char for char in contact.get_name().get_last()])
        # Loop through each part of the name
        for part_of_name in names:
            part_of_name_len = len(part_of_name)
            # Creates an xrange from 0 to the longest name in list
            for x in xrange(0, len(max(part_of_name, key=len))):
                list_of_x_char = []
                # Create a list of characters at the nth location of the part of the name
                for x2 in xrange(0, part_of_name_len):
                    try:
                        # x2 is one of the different parts of a name
                        # x is the character from 0 to the longest name.
                        char = part_of_name[x2][x]
                        if char.isalpha() or char is "-":
                            list_of_x_char.append(char)
                    except IndexError:
                        list_of_x_char.append("")
                total_length_to_check = len(list_of_x_char)
                # Goes through each character at that location
                already_used_chars = []
                for char in list_of_x_char:
                    # Checks to see if it is not a letter, if it isn't it removes it's effect
                    if list_of_x_char.count(char) >= (total_length_to_check / 2) and char not in already_used_chars:
                        name_str += char
                        already_used_chars.append(char)
            name_str += " "
        # Is there an email?
        # Working out average email
        if any(con.has_email_address() for con in self.__contacts):
            for contact in self.__contacts[:]:
                # Parts of the email
                if (contact.has_email_address()):
                    email[0].append([char for char in contact.get_email_address().get_user()])
                    email[1].append([char for char in contact.get_email_address().get_domain()])
            # Longest part in list
            for idx, email_part in enumerate(email):
                if email_part is not "":
                    email_part_length = len(email_part)
                    for x in xrange(0, len(max(email_part, key=len))):
                        list_of_x_char = []
                        # Create a list of characters at the nth location of the part of the name
                        for x2 in xrange(0, email_part_length):
                            try:
                                list_of_x_char.append(email_part[x2][x])
                            except IndexError:
                                list_of_x_char.append("")
                        already_used_chars = []
                        total_length_to_check = len(list_of_x_char)
                        # Goes through each character at that location
                        for char in list_of_x_char:
                            # If it's occurrence is more than half of the total, use it as the definitive character.
                            if list_of_x_char.count(
                                    char) >= total_length_to_check / 2 and char not in already_used_chars:
                                name_str += char
                                already_used_chars.append(char)
                    if email.index(email_part) == 0:
                        name_str += "@"
        name_str = name_str.strip()
        self.__average_contact = Contact(name_str, "")

    def get_average_contact(self):
        """
        Get the average contact from the profile.

        :return: The average contact.
        :rtype: Contact
        """
        return self.__average_contact

    def get_dict(self):
        """
        Gets the dictionary representation of the profile.

        :return: The representation as a dictionary
        :rtype: dict
        """
        try:
            return {"".join(ch for ch in str(self.__average_contact) if ord(ch) < 128): [
                "".join(ch for ch in str(c) if ord(ch) < 128) for c in self.__contacts]}
        except:
            print sorted([ord(ch) for ch in str(self)], reverse=True)
            raise

    def __str__(self):
        return str(str(self.__average_contact) + ": " + str([str(c) for c in self.__contacts]))

    def __repr__(self):
        return str({str(self.__average_contact): [str(c) for c in self.__contacts]})


class EmailAddress(object):
    __raw_address = None
    __domain = None
    __user = None
    __redacted = None

    def __init__(self, email_str):
        """
        Creates a way to parse email addresses and set specific conventions.

        :param email_str: The string to be parsed into an email.
        :return: None
        """
        self.__redacted = False
        self.__raw_address = email_str
        self._run()

    def get_domain(self):
        """
        Returns the domain of the address.

        :return: The domain of the address. Returns None if there is not one.
        """
        return self.__domain

    def set_redacted(self, redacted):
        """
        Sets the redacted state of the email object.

        :param redacted: The Boolean to set.
        :return: None.
        """
        self.__redacted = redacted

    def get_redacted(self):
        """
        Gets the redacted state of the email object.

        :return: None.
        """
        return self.__redacted

    def get_user(self):
        """
        Gets the user in front of the "@".

        :return: A string representing the user.
        """
        return self.__user

    def get_whole(self):
        """
        Returns the whole email. Ex. "alex@example.com"

        :return: The whole email in the standard email format.
        """
        return self.__raw_address

    def _run(self):
        """
        Called when the object is initiated.

        :return: None.
        """
        try:
            split_up = self.__raw_address.split("@")
            self.__user = split_up[0]
            self.__domain = split_up[1]
        except IndexError:
            {}

    def compare_to(self, email_address):
        """
        Compares the given email address to itself and returns a similarity from 0-100.

        :param email_address: The email address object to compare.
        :return: The similarity between the two from 0-100.
        """
        if self.__domain is not None and self.__user is not None:
            if email_address.get_domain() is not None:
                return (float(fuzz.ratio(email_address.get_domain(), self.__domain)) / 2) + (
                    float(fuzz.ratio(email_address.get_user(), self.__user)) / 2)
            else:
                return 0
        return 0


class Name:
    __raw_name = None
    __first_name = ""
    __last_name = ""
    __middle_init = ""
    __redacted = False
    __redacted_str = ""

    def __init__(self, name_str, redacted_str):
        """
        Creates a way to parse name data. Ability to get first, last name and middle initial from a string.

        :param name_str: The string that represents the name in some format.
        :return: None.
        """
        self.__raw_name = name_str
        self.__redacted_str = redacted_str
        self._run()

    def get_first(self):
        """
        Gets the first name of the person.

        :return: The string representing the first name of the person.
        """
        return self.__first_name

    def get_last(self):
        """
        Gets the last name of the person.

        :return: The string representing the last name of the person.
        """
        return self.__last_name

    def get_mid_init(self):
        """
        Gets the middle initial of the person.

        :return: The string representing the middle initial of the person.
        """
        return self.__middle_init

    def get_full_name(self, name_type):
        """
        Returns the full name in one of two formats. 0 for First M Last. 1 for Last, M First.

        :param name_type: 0 or 1 for the type of name returned.
        :return: The string representing the name of the person.
        """
        if name_type == 0:
            return self.__first_name + " " + self.__middle_init + " " + self.__last_name
        elif name_type == 1:
            return self.__last_name + ", " + self.__first_name + " " + self.__middle_init

    def compare_to(self, name):
        """
        Compares the name object given to itself.

        :param name: The name object to be compared.
        :return: The ratio between them from 0-100.
        """
        return fuzz.token_sort_ratio(name.get_full_name(0), self.get_full_name(0))

    def set_redacted(self, redacted):
        """
        Sets the redacted state of the name object.

        :param redacted: Boolean to set if the name has been redacted.
        :return: None.
        """
        self.__redacted = redacted

    def get_redacted(self):
        """
        Gets the redacted state of the name object.

        :return: The Boolean for the redacted state.
        """
        return self.__redacted

    def get_raw(self):
        """
        Gets the raw string provided in the objects instantiation.

        :return: The raw string provided in the objects instantiation.
        """
        return self.__raw_name

    def _run(self):
        """
        The method called when the object is initiated. Breaks up raw string into its name part.

        :return: None
        """
        raw = self.__raw_name
        raw = re.sub(r' +', ' ', raw)
        raw = raw.replace(self.__redacted_str, "")
        if "," in raw:
            raw = raw.strip().split(",")
            self.__last_name = raw[0].capitalize()
            raw = raw[1].strip().split(" ")
            if len(raw) == 2:
                self.__first_name = raw[0].capitalize()
                self.__middle_init = raw[1].capitalize()[0]
            else:
                self.__first_name = raw[0].capitalize()
        else:
            raw = raw.strip().split(" ")
            if len(raw) == 3:
                try:
                    self.__first_name = raw[0].capitalize()
                    self.__middle_init = raw[1].capitalize()[0]
                    self.__last_name = raw[2].capitalize()
                except IndexError:
                    self.__first_name = raw[0].capitalize()
                    self.__last_name = raw[2].capitalize()
            elif len(raw) == 2:
                self.__first_name = raw[0].capitalize()
                self.__last_name = raw[1].capitalize()
            else:
                self.__first_name = raw[0].capitalize()


class Contact(object):
    __raw_string = ''
    __name = Name('', '')
    __email_address = EmailAddress('')
    __redacted_string = ''
    __has_email = True
    __has_name = True
    __sanitize = True

    def __init__(self, raw_string, redacted_string):
        """
        Creates a contact object from the field provided. Breaks it up into name and email (if they exist).

        :param raw_string: The raw string that represents the field. Can take strings like:
                - First M Last <firstmlast@example.com>
                - Last, M First firstmlast@example.com
                - Last, First
                - First Last firstmlast@example.com
                - firstmlast@example.com
        :param redacted_string: The string to show if an item has been redacted.
        :return: None.
        """
        self.__raw_string = raw_string
        self.__redacted_string = redacted_string
        self._run()

    def is_redacted(self):
        """
        Checks if the name and email are redacted.

        :return: True if both are redacted, false if not.
        """
        return self.__name.get_redacted() and self.__email_address.get_redacted()

    def get_name(self):
        """
        Gets the name object associated with this contact.

        :return: The name object associated with this contact. Empty object if there is not one.
        """
        return self.__name

    def is_mangled(self):
        """
        Checks if the contact has likely parsing problems.

        :return: Boolean, True if it is mangled, False if it is not.
        """
        pass

    def is_empty(self):
        """
        Checks to see if the string is empty or not.

        :return: The boolean representing if it is empty or not.
        :rtype: bool
        """
        stripped_string1 = self.__raw_string.strip()
        if stripped_string1 is "":
            return True
        return False

    def has_email_address(self):
        """
        Checks if the contact has an email associated with it.

        :return: Boolean. True if it has an email, False if not.
        """
        return self.__has_email

    def set_sanitize(self, sanitize):
        """
        Sanitize the raw input.

        :param sanitize: True for sanitation, False for none.
        :type sanitize: bool
        :return: None.
        :rtype: None
        """
        self.__sanitize = sanitize

    def get_sanitize(self):
        """
        Gets the current sanitation state.

        :return: The sanitation state.
        """
        return self.__sanitize

    def has_name(self):
        """
        Checks if the contact has a name associated with it.

        :return: Boolean. True if it has a name, False if not.
        """
        return self.__name != ''

    def get_email_address(self):
        """
        Gets the email address associated with the contact.

        :return: The email object associated with the contact.
        """
        return self.__email_address

    def get_raw(self):
        """
        Gets the raw string provided at the objects instantiation.

        :return: The raw string provided at the objects instantiation.
        """
        return self.__raw_string

    def __repr__(self):
        """
        What to print when called in the python console.

        :return: The formatted name.
        """
        to_return = str(self.__name.get_full_name(1) + " <" + self.__email_address.get_whole() + ">")
        if self.__sanitize:
            to_return = "".join(ch for ch in str(to_return) if ord(ch) < 128)
        return to_return

    def __str__(self):
        """
        What to print when called in a print statement.

        :return: The formatted name.
        """

        to_return = str(self.__name.get_full_name(1) + " <" + self.__email_address.get_whole() + ">")
        if self.__sanitize:
            to_return = "".join(ch for ch in str(to_return) if ord(ch) < 128)
        return to_return

    def _run(self):
        """
        Called when the object is instantiated.

        :return: None.
        """
        raw = self.__raw_string
        # sanitize the input from common ocr'ing mistakes
        raw = raw.replace("›", ">")
        raw = raw.replace("‹", "<")
        raw = raw.replace("©", "@")
        # raw = raw.replace("", "")
        # identify email address
        try:
            email_address = re.search(r'[\w\.-]+@[\w\.-]+', raw)
            self.__email_address = EmailAddress(email_address.group(0).strip())
        except AttributeError:
            # No email found
            self.__has_email = False
            if self.__redacted_string in raw:
                self.__email_address.set_redacted(True)
        # Identify name
        if fuzz.ratio(self.__redacted_string, raw) < 90:
            name = raw.replace(self.__email_address.get_whole(), '')
            name = re.sub(r'<.*?>', "", name)
            name = re.sub(r'\[mailto:.*?:', "", name)
            name = re.sub(r'\[mailto:\]', "", name)
            self.__name = Name(name.strip(), self.__redacted_string)
        else:
            self.__has_name = False
            self.__name.set_redacted(True)


class EmptyCollectionException(Exception):
    pass


if __name__ == "__main__":
    con_test = Contact("sobelcm (This info has been redacted) .", "(This info has been redacted)")
    print con_test.get_email_address().get_whole()
