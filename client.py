from api.metadata import MetadataClient
import csv

'''
header => The header row from the input file.

Returns a dictionary mapping each column name to its index in the row.
'''
def getColumnDict(header):
    columnDict = {}
    for i in range(len(header)):
        columnDict[header[i]] = i
    return columnDict

'''
Connects to the metadata API using user-provided credentials, then 
reads a user specified file to create custom fields. 
Writes an output file containing SaveResult information for each field.
''' 
def main():
    connSuccess = False
    client = None
    while not connSuccess:
        partnerWsdl = raw_input('Enter the full path to your partner wsdl file: ')
        metadataWsdl = raw_input('Enter the full path to your metadata wsdl file: ')
        
        try:
            client = MetadataClient(partnerWsdl, metadataWsdl)
            connSuccess = True
            print 'Connection successful.'
        except:
            print 'Connection not successful. Please try again.'
            
    isLoggedIn = False
    while not isLoggedIn:
        username = raw_input('Enter your Salesforce username: ')
        password = raw_input('Enter your Salesforce password: ')
        token = raw_input('Enter your Salesforce security token: ')
        try:
            client.login(username, password, token)
            isLoggedIn = True
            print 'Log in successful.\n'
        except:
            print '\nInvalid username or password.\n'
     
    isValidFile = False
    f = None
    while not isValidFile:
        filename = raw_input('Enter the full path to your CSV file: ')
        try:
            f = open(filename, 'r')
            isValidFile = True
        except:
            print '\nInvalid filename.\n'
    
    isValidFile = False
    g = None
    while not isValidFile:
        filename = raw_input('Enter the full path to your output file: ')
        try:
            g = open(filename, 'wb')
            isValidFile = True
        except:
            print '\nInvalid filename.\n'
            
    reader = csv.reader(f)
    writer = csv.writer(g)
    
    header = reader.next()
    headerDict = getColumnDict(header)
    
    header.append('Success')
    header.append('Error')
    writer.writerow(header)
    
    for line in reader:
        args = {}
        for key in headerDict:
            index = headerDict[key]
            args[key] = line[index]
        field = client.createField(**args)
        saveRes = client.deployFields([field])
        isSuccess = saveRes[0].success
        line.append(isSuccess)
        if not isSuccess:
            line.append(saveRes[0].errors[0].message)
        writer.writerow(line)
    
    f.close()
    g.close()

if __name__ == '__main__':
    main()