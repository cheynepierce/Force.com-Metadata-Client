from base import BaseClient

class MetadataClient(BaseClient):
    _supportedFieldTypes = [
                            'AutoNumber',
                            'Checkbox',
                            'Currency',
                            'Date',
                            'DateTime',
                            'Email',
                            'Lookup',
                            'MasterDetail',
                            'MultiselectPicklist',
                            'Number',
                            'Percent',
                            'Phone',
                            'Picklist',
                            'Text',
                            'TextArea',
                            'LongTextArea',
                            'Url',
                            'EncryptedText']
    
    '''Some default values'''
    _apiVersion = 30.0
    _defaultCheckboxVal = False
    _defaultTextLength = 255
    _defaultLongTextAreaLength = 32768
    _defaultVisibleLines = 4
    _defaultCurrencyScale = 2
    _defaultNumberScale = 0
    _defaultPercentScale = 0
    _defaultCurrencyPrecision = 18
    _defultNumberPrecision = 18
    _defaultPercentPrecision = 3
    
    def __init__(self, partnerWsdl, metadataWsdl):
        super(MetadataClient, self).__init__(partnerWsdl, metadataWsdl)
    
    '''
    Retrieves property information on metadata components
    
    metadataType => the type of metadata component that you want property information for
    e.g. CustomObject
    '''
    def listMetadata(self, metadataType):
        query = self._metadata.factory.create('ListMetadataQuery')
        query.type = metadataType
        return self._metadata.service.listMetadata(query, self._apiVersion)
        
    '''
    Creates a custom object in Salesforce.
    
    Object properties are passed in through key word arguments.
    
    Returns a save result object.
    '''
    def createObject(self, **kwargs):
        obj = self._metadata.factory.create('CustomObject')
        obj.fullName = kwargs.get('Full Name')
        obj.label = kwargs.get('Label')
        obj.pluralLabel = kwargs.get('Plural Label')
        
        deploymentStatus = self._metadata.factory.create('DeploymentStatus')
        obj.deploymentStatus = deploymentStatus.Deployed
        
        sharingModel = self._metadata.factory.create('SharingModel')
        obj.sharingModel = sharingModel.ReadWrite
        
        nameField = self._metadata.factory.create('CustomField')
        fieldType = self._metadata.factory.create('FieldType')
        nameField.type = fieldType.Text
        nameField.label = obj.label + ' Name'
        obj.nameField = nameField
        
        return self._metadata.service.createMetadata(obj)
    
    '''
    Creates a custom field in Salesforce.
    
    fieldType => A string containing the field type. 
        Must match an option in _supportedFieldTypes.
    Field properties are passed in through key word arguments.
    
    Returns the field.
    '''
    def createField(self, **kwargs):
        field = self._metadata.factory.create('CustomField')
        
        fieldType = kwargs.get('Field Type', None)
        field.type = self._getFieldType(fieldType)
        field.fullName = kwargs.get('Object Name', '') + '.' + kwargs.get('Label', '').replace(' ', '_') + '__c'
        field.label = kwargs.get('Label', '')
        field.description = kwargs.get('Description', None)
        field.inlineHelpText = kwargs.get('Inline Help Text', None)
        field.externalId = kwargs.get('External Id', False)
        field.required = kwargs.get('Required', False)
        field.unique = kwargs.get('Unique', False)
        
        field.length = kwargs.get('Length', None)
        if field.type in ('Text', 'EncryptedText') and field.length == None:
            field.length = self._defaultTextLength
        if field.type == 'TextArea' and field.length != None:
            field.length = None
        if field.length == '':
            field.length = None
        
        field.visibleLines = kwargs.get('Visible Lines', None)
        if field.type == 'LongTextArea' and field.length == None:
            field.length = self._defaultTextAreaLength
        if field.type in ('LongTextArea', 'MultiselectPicklist') and field.visibleLines == None:
            if field.visibleLines == None:
                field.visibleLines = self._defaultVisibleLines
            
        field.defaultValue = kwargs.get('Default Value', None)
        if field.defaultValue == None:
            if field.type == 'Checkbox':
                field.defaultValue = self._defaultCheckboxVal
        
        field.scale = kwargs.get('Scale', None)
        if field.type == 'Currency' and field.scale == None:
            field.scale = self._defaultCurrencyScale
        if field.type == 'Number' and field.scale == None:
            field.scale = self._defaultNumberScale
        if field.type == 'Percent' and field.scale == None:
            field.scale = self._defaultPrecisionScale
        field.precision = kwargs.get('Precision', None)
        if field.type == 'Currency' and field.precision == None:
            field.precision = self._defaultCurrencyPrecision
        if field.type == 'Number' and field.precision == None:
            field.precision = self._defaultNumberPrecision
        if field.type == 'Percent' and field.precision == None:
            field.precision = self._defaultPercentPrecision
        
        if field.type == 'EncryptedText':
            field.maskType = self._getMaskType(kwargs.get('Mask Type', None))
            field.maskChar = self._getMaskChar(kwargs.get('Mask Char', None))
        
        if field.type in ('Picklist', 'MultiselectPicklist'):
            field.picklist = self._getPicklist(
                kwargs.get('Picklist Values', ''), 
                kwargs.get('Is Sorted', False))
        
        if field.type in ('Lookup', 'MasterDetail'):
            field.referenceTo = kwargs.get('Reference To')
            field.relationshipLabel = kwargs.get('Relationship Label', '')
            field.relationshipName = kwargs.get('Relationship Label', '').replace(' ', '')
        
        if field.type == 'AutoNumber':
            field.startingNumber = kwargs.get('Starting Number', 1)
            
        return field
    
    '''
    Create a field type object.
    
    fieldType => A string containing the field type. 
        Must match an option in _supportedFieldTypes.
        
    Returns a field type object. Returns None if it can't 
    find a field type that matches the input string.
    '''
    def _getFieldType(self, fieldType):
        fieldTypes = self._metadata.factory.create('FieldType')
        for t in fieldTypes:
            if t[0] == fieldType and t[0] in self._supportedFieldTypes:
                return t[1]
        return None
    
    '''
    Create the picklist values available for the field. 
    Currently does not support dependent picklists or modifying the default value.
    
    values => A semicolon delimited list of picklist values.
    isSorted => A boolean to determine whether the values should be 
        sorted alphabetically or displayed in the order entered.
        
    Returns a picklist object.
    '''
    def _getPicklist(self, values, isSorted):
        picklist = self._metadata.factory.create('Picklist')
        picklist.sorted = isSorted
        picklistValues = []
        for value in values.split(';'):
            picklistValue = self._metadata.factory.create('PicklistValue')
            picklistValue.fullName = value
            picklistValue.default = False
            picklistValues.append(picklistValue)
        picklist.picklistValues = picklistValues
        return picklist
    
    '''
    Get an encrypted text mask type: e.g. SSN, credit card, etc.
    
    maskType => The mask type name.
    
    Returns a mask type object. Defaults to masking all characters 
    if it can't find a match with the requested mask type.
    '''
    def _getMaskType(self, maskType):
        maskTypes = self._metadata.factory.create('EncryptedFieldMaskType')
        for t in maskTypes:
            if t[0] == maskType:
                return t[1]
        return maskTypes.all
    
    '''
    Get an encrypted text mask char: either * or X.
    
    maskChar => The desired masking character.
    
    Returns a mask char object. Defaults to asterisk if it 
    can't find a mask character that matches the input string.
    '''
    def _getMaskChar(self, maskChar):
        maskChars = self._metadata.factory.create('EncryptedFieldMaskChar')
        for m in maskChars:
            if m[0] == maskChar:
                return m[1]
        return maskChars.asterisk
    
    '''
    Deploy list of fields to Salesforce.com.
    
    fields => A list of field objects to be deployed.
    
    Returns a list of SaveResult objects.
    '''
    def deployFields(self, fields):
        return self._metadata.service.createMetadata(fields)