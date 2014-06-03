##Force.com Metadata Client

This is a simple command line application to allow mass creation of custom fields defined by a CSV file.
This application is still in development and has not yet been fully tested. 

##Usage
1. Use the template CSV file to enter information about the fields you would like to create. 
2. Save a copy of your org's partner and metadata wsdl files somewhere. 
3. Run client.py and follow the prompts to enter information about your wsdl files, username, password, security token, input file, and output file.
4. After execution is complete, your output file will contain status information about each field.

##Notes
Currently does not support Encrypted Text fields.

Currently does not support modifying field level security.