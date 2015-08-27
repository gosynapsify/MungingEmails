# MungingEmails
---------------
Designed to scale for converting any input email format to a standard digital dictionary of each email's metadata for more sophisticated processing, such as Natural Language Processing, graph analysis, or other machine learning techniques.

## Check for new emails
Checks to see if there are new emails from a given source, can be adapded for other email sets.

#### Usage
---
```bash
python check_for_new.py <file_to_store_already_downloaded_emails alert_email directory_for_attachment>
```
## OCR'd Munging

A library to download and convert OCR'd pdf files to an easy to work with system of collections, documents, and emails.

##### Install pdftotext
---
**Important: Install version 3.03, as 3.04 does not correctly convert the layout of the PDFs.**

On OSX:
Move pdftotext executable to /usr/local/bin

On Linux:
Move pdftotext exectutable to /usr/local/bin

##### Usage
---

**Note:** This is just a quick getting started, for the documentation, either compile the docs yourself with the make script in the docs directory, or download [this zip](https://www.dropbox.com/s/hdrc7f9nsv6kkh1/docs.zip?dl=0) and open the html file.

- Doing everything:
    ```python
    from email_getter import FileCreator
    from email_datatypes import Collection

    file_creator = FileCreator(download_emails=True, pdf_list_file="where/the/list/file/is", where_to_download="where/to/download/files", convert=True, convert_output_dir="where/to/store/the/.txts", fix_files=True, fixing_chops=[8, 5, 5])

    # Create a collection object that represents every document with the .txt extension.
    collection = Collection(file_creator.get_convert_output_dir(), ".txt")

    # Loop through every doc, then through every email.
    for document in collection:
        for email in document:
            # This could also be any method in the Email class.
            print email.get_from()
    ```

    This code will download the PDFs, convert them to text, then scrape the data from those files.

- Without downloading:
    ```python
    from email_getter import FileCreator
    from email_datatypes import Collection

    # Create a FileCreator object that holds all of the file creation information.
    # We specify convert_output_dir because that is where we have already stored the converted files.
    file_creator = FileCreator(download_emails=False, where_to_download="where/pdfs/are/stored", convert=True, convert_output_dir="dir_here", fix_files=True, fixing_chops=[8, 5, 5])

    # Create a Collection object that represents every document with the .txt extension.
    collection = Collection(file_creator.get_converted_output_dir(), ".txt")

    # Loop through every doc, then through every email.
    for document in collection:
        for email in document:
            # This could also be any method in the Email class.
            print email.get_from()
    ```

    This code will only scrape the data from a given set of converted and fixed files.

- Without downloading or converting (Just using files you have already created):
    ```python
    from email_datatypes import Collection

    # Create a Collection object that represents every document
    collection = Collection("your/dir/here/", ".txt")

    # Loop through every doc, then through every email.
    for document in collection:
        for email in document:
            # This could also be any method in the Email class.
            print email.get_from()
    ```

    This code will only scrape the data from a given set of converted files.
