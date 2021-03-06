# -*- coding: utf-8 -*-
"""
This module is meant to implement all functions described at:

    #1) http://dev.mendeley.com/methods/
    #
    #   Shows request parameters a bit more clearly    
    
    #2) https://api.mendeley.com/apidocs/apis
    #
    #   Testing interface, nicer organization
    

General Usage
-------------
from mendeley import API
user_api = API()
public_api = API()


Request Options
---------------
In addition to the options of a given function, the following options are also
supported:

    TODO: fill this in: example _return_type

TODO: Create an options class that can be given to the request (e.g. for return type)

Method Types (from Mendeley)
----------------------------
Annotations
Academic Statuses
Catalog Documents
Catalog Search
Datasets
Disciplines
Documents
Documents Metadata Lookup
Files
File Content
Folders
Groups
Identifier Types
Locations
Profiles
Trash
Errors

"""

#Standard Library
import sys
import mimetypes
from os.path import basename
from datetime import datetime
import json

#Third party
import requests

#Local Imports
from . import auth
from . import models
from . import utils
from .errors import *

PY2 = int(sys.version[0]) == 2

if PY2:
    from urllib import quote as urllib_quote
else:
    from urllib.parse import quote as urllib_quote

BASE_URL = 'https://api.mendeley.com'

# For each view, specify which object type should be returned
catalog_fcns = {None: models.CatalogDocument,
                'bib': models.BibCatalogDocument,
                'stats': models.StatsCatalogDocument,
                'client': models.ClientCatalogDocument,
                'all': models.AllCatalogDocument
                }

document_fcns = {None: models.Document,
                 'bib': models.BibDocument,
                 'client': models.ClientDocument,
                 'tags': models.TagsDocument,
                 'patent': models.PatentDocument,
                 'all': models.AllDocument,
                 'deleted': models.DeletedDocument
                 }

#==============================================================================
class API(object):
    """
    This is a shared superclass for both the public and private API classes.
    
    Attributes
    ----------
    default_return_type : {'object','json','raw','response'}
        This is the default type to return from methods.
        
    last_response : 
    last_params : 
        
    """

    def __init__(self, user_name=None):
        """
        Parameters
        ----------
        user_name : string (default None)
            - None : then the default user is loaded via config.DefaultUser
            - 'public' : then the public API is accessed
        
        """

        self.s = requests.Session()
        if user_name == 'public':
            self.public_only = True
            token = auth.retrieve_public_authorization()
            self.user_name = 'public'
        else:
            self.public_only = False
            token = auth.retrieve_user_authorization(user_name, session=self.s)
            self.user_name = token.user_name

        # Options ... (I might change this ...)
        self.default_return_type = 'object'

        self.access_token = token
        self.last_response = None
        self.last_params = None

        #TODO: Eventually I'd like to trim this based on user vs public
        self.annotations = Annotations(self)
        self.definitions = Definitions(self)
        self.documents = Documents(self)
        self.folders = Folders(self)
        self.files = Files(self)
        self.trash = Trash(self)

    def __repr__(self):
        # TODO: Finish all of these ..
        pv = ['public_only', self.public_only, 'user_name', self.user_name]
        return utils.property_values_to_string(pv)

    def make_post_request(self, url, object_fh, params, response_params=None, headers=None, files=None):

        #
        # http://docs.python-requests.org/en/latest/user/advanced/#streaming-uploads

        if params is not None:
            return_type = params.pop('_return_type', self.default_return_type)
        else:
            return_type = self.default_return_type

        if files is None:
            params = json.dumps(params)

        r = self.s.post(url, data=params, auth=self.access_token, headers=headers, files=files)

        if not r.ok:
            # if r.status_code != good_status:
            print(r.text)
            print('')
            # TODO: This should be improved
            raise CallFailedException('Call failed with status: %d' % (r.status_code))

        return self.handle_return(r, return_type, response_params, object_fh)

    def make_get_request(self, url, object_fh, params, response_params=None):
        """

        Parameters:
        -----------          
        url : str
            URL to make request from.
        object_fh: function handle

        params : dict (default {})
            Dictionary of parameters to place in the GET query. Values may be
            numbers or strings.
        good_status : int (default 200)
            The status to check for as to whether or not the request 
            was successful.
        return_type : {'object','json','raw','response'}
            object - indicates that the result class object should be created.
                This is the slowest option but provides the most functionality.
            json   - 
            
        See Also:
        ---------
        .auth.UserCredentials.__call__()
        .auth.PublicCredentials.__call__()
        """

        # TODO: extract good_status = 200, return_type = None from params

        if params is None:
            params = {}
        else:
            if PY2:
                params = dict((k, v) for k, v in params.iteritems() if v)
            else:
                params = dict((k, v) for k, v in params.items() if v)

        return_type = params.pop('_return_type', self.default_return_type)

        # This was newly introduced, apparently? Each dev token is only good for 90 days
        # https://development-tokens.mendeley.com/
        dev_token = utils.dev_token
        header = {'Development-Token' : dev_token}

        # NOTE: We make authorization go through the access token. The request
        # will call the access_token prior to sending the request. Specifically
        # the __call__ method is called.
        r = self.s.get(url, params=params, auth=self.access_token, headers=header)

        self.last_url = url
        self.last_response = r
        self.last_params = params

        if not r.ok:
            # if r.status_code != good_status:
            print(r.text)
            print('')
            # TODO: This should be improved
            raise Exception('Call failed with status: %d' % (r.status_code))

        return self.handle_return(r, return_type, response_params, object_fh)

    def make_patch_request(self, url, object_fh, params, response_params=None, headers=None, files=None):
        #
        # http://docs.python-requests.org/en/latest/user/advanced/#streaming-uploads

        if params is not None:
            return_type = params.pop('_return_type', self.default_return_type)
        else:
            return_type = self.default_return_type

        if files is None:
            params = json.dumps(params)

        r = self.s.patch(url, data=params, auth=self.access_token, headers=headers, files=files)

        if not r.ok:
            # if r.status_code != good_status:
            print(r.text)
            print('')
            # TODO: This should be improved
            raise Exception('Call failed with status: %d' % (r.status_code))

        return self.handle_return(r, return_type, response_params, object_fh)

    def handle_return(self, req, return_type, response_params, object_fh):
        if return_type is 'object':
            if response_params is None:
                return object_fh(req.json(), self)
            else:
                return object_fh(req.json(), self, response_params)
        elif return_type is 'json':
            return req.json()
        elif return_type is 'raw':
            return req.text
        elif return_type is 'response':
            return req
        else:
            raise Exception('No match found for return type')

    def catalog(self, **kwargs):

        """
        
        TODO: This should probably be moved ...        
        
        Parameters
        ----------
        arxiv
        doi
        isbn
        issn
        pmid
        scopus
        filehash
        view
         - bib
         - stats
         - client - this option doesn't make much sense
         - all
        id : string
            Short for Catalog ID. Mendeley's catalog id. The only way I know of
            getting this is from a previous Mendeley search.
        
        Examples
        --------
        from mendeley import API
        m = API()
        c = m.catalog(pmid='11826063')
        c = m.catalog(pmid='11826063',view='bib')
        c = m.catalog(cid='f631d7ed-9926-34ed-b56e-0f5bb236b87b')
        """

        """
        Internal Note: Returns a list of catalog entries that match a 
        given query 
        #TODO: Is this the case for a given id? NO - only returns signle entry
        #TODO: Build this into tests
        """

        url = BASE_URL + '/catalog'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id

        view = kwargs.get('view')
        response_params = {'fcn': catalog_fcns[view]}

        return self.make_get_request(url, models.DocumentSet.create, kwargs, response_params)


class Definitions(object):
    """
    TODO: These values should presumably only be queried once ...
    """

    def __init__(self, parent):
        self.parent = parent

    def academic_statuses(self, **kwargs):
        """
        
        https://api.mendeley.com/apidocs#!/academic_statuses/get
        
        Example
        -------        
        from mendeley import API
        m = API()
        a_status = m.definitions.academic_statuses()
        """
        url = BASE_URL + '/academic_statuses'

        return self.parent.make_get_request(url, models.academic_statuses, kwargs)

    def subject_areas(self, **kwargs):
        """
        Examples
        --------
        from mendeley import API
        m = API()
        d = m.definitions.disciplines()
        """
        url = BASE_URL + '/subject_areas'

        return self.parent.make_get_request(url, models.subject_areas, kwargs)

    def document_types(self, **kwargs):
        """
        
        https://api.mendeley.com/apidocs#!/document_types/getAllDocumentTypes
        
        Examples
        --------
        from mendeley import API
        m = API()
        d = m.definitions.document_types()
        """
        url = BASE_URL + '/document_types'

        return self.parent.make_get_request(url, models.document_types, kwargs)


class Annotations(object):
    def __init__(self, parent):
        self.parent = parent

    def get(self):
        # https://api.mendeley.com/apidocs#!/annotations/getAnnotations
        pass

    def delete(self):
        pass


class Files(object):
    def __init__(self, parent):
        self.parent = parent

    def get_single(self, **kwargs):
        """
        # https://api.mendeley.com/apidocs#!/annotations/getFiles

        THIS DOESN'T REALLY DO ANYTHING RIGHT NOW.

        Parameters
        ----------
        id :
        document_id :
        catalog_id :
        filehash :
        mime_type :
        file_name :
        size :

        Returns
        -------

        """

        url = BASE_URL + '/files'

        doc_id = kwargs.get('document_id')

        # Not sure what this should be doing
        response_params = {'document_id': doc_id}

        # Didn't want to deal with make_get_request
        response = self.parent.s.get(url, params=kwargs, auth=self.parent.access_token)
        json = response.json()[0]

        file_id = json['id']

        file_url = url + '?id=' + file_id

        file_response = self.parent.s.get(file_url, auth=self.parent.access_token)

        return file_id

        pass

    def link_file(self, file, params, file_url=None):
        """

        Parameters
        ----------
        file : dict
            Of form {'file' : Buffered Reader for file}
            The buffered reader was made by opening the pdf using open().
        params : dict
            Includes the following:
            'title' = paper title
            'id' = ID of the document to which
            the file will be attached
            (optional) '_return_type': return type of API.make_post_request
            (json, object, raw, or response)

        Returns
        -------
        Object specified by params['_return_type'].
            Generally models.LinkedFile object

        """
        base_url = 'https://api.mendeley.com'
        url = base_url + '/files'

        # Extract info from params
        title = params['title']
        doc_id = params['id']
        object_fh = models.File

        # Get rid of spaces in filename
        filename = urllib_quote(title) + '.pdf'
        filename = filename.replace('/', '%2F')

        headers = dict()
        headers['Content-Type'] = 'application/pdf'
        headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        headers['Link'] = '<' + base_url + '/documents/' + doc_id + '>; rel="document"'

        API.make_post_request(API(), url, object_fh, params, headers=headers, files=file)

    def link_file_from_url(self, file, params, file_url):
        """

        Parameters
        ----------
        file : dict
            Of form {'file' : Buffered Reader for file}
            The buffered reader was made by opening the pdf using open().
        params : dict
            Includes paper title, ID of the document to which
            the file will be attached, and return type.
        file_url : str
            Direct URL to a pdf file.

        Returns
        -------
        Object specified by params['_return_type'].
            Generally models.LinkedFile object

        """
        base_url = 'https://api.mendeley.com'
        url = base_url + '/files'

        # Extract info from params
        title = params['title']
        doc_id = params['id']
        object_fh = models.LinkedFile

        # Get rid of spaces in filename
        filename = title.replace(' ', '_') + '.pdf'

        headers = dict()
        headers['Content-Type'] = 'application/pdf'
        headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        headers['Link'] = '<' + base_url + '/documents/' + doc_id + '>; rel="document"'

        API.make_post_request(API(), url, object_fh, params, headers=headers, files=file)

    def delete(self):
        # TODO: make this work
        pass


class Folders(object):
    def __init__(self, parent):
        self.parent = parent

    def create(self, name):
        url = BASE_URL + '/folders'

        # Clean up name
        name = name.replace(' ', '_')
        name = urllib_quote(name)
        params = {'name' : name}

        headers = {'Content-Type' : 'application/vnd.mendeley-folder.1+json'}

        return self.parent.make_post_request(url, models.Folder, params, headers=headers)


class Trash(object):
    def __init__(self, parent):
        self.parent = parent

    def get(self, **kwargs):
        """        
        Parameters
        ----------
        id : 
        group_id : string
            The id of the group that the document belongs to. If not supplied 
            returns users documents.
        modified_since : string
            Returns only documents modified since this timestamp. Should be 
            supplied in ISO 8601 format.
        limit : string or int (default 20)
            Largest allowable value is 500. This is really the page limit since
            the iterator will allow exceeding this value.
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order            
        view : 
            - 'bib'
            - 'client'
            - 'tags' : returns user's tags
            - 'patent'
            - 'all'
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'
        """

        url = BASE_URL + '/trash'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id

        view = kwargs.get('view')

        limit = kwargs.get('limit', 20)
        response_params = {'fcn': document_fcns[view], 'view': view, 'limit': limit}

        # TODO: When returning deleted_since, the format changes and the fcn
        # called should change

        return self.parent.make_get_request(url, models.DocumentSet.create, kwargs, response_params)


class Documents(object):
    def __init__(self, parent):
        self.parent = parent

    def get(self, **kwargs):
        """
        https://api.mendeley.com/apidocs#!/documents/getDocuments
        
        Parameters
        ----------
        id : 
        group_id : string
            The id of the group that the document belongs to. If not supplied 
            returns users documents.
        modified_since : string or datetime
            Returns only documents modified since this timestamp. Should be 
            supplied in ISO 8601 format.
        deleted_since : string or datetime
            Returns only documents deleted since this timestamp. Should be 
            supplied in ISO 8601 format.
        profile_id : string
            The id of the profile that the document belongs to, that does not 
            belong to any group. If not supplied returns users documents.
        authored :
            TODO
        starred : 
        limit : string or int (default 20)
            Largest allowable value is 500. This is really the page limit since
            the iterator will allow exceeding this value.
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order            
        view : 
            - 'bib'
            - 'client'
            - 'tags' : returns user's tags
            - 'patent'
            - 'all'
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'

        Examples
        --------
        from mendeley import API
        m = API()
        d = m.documents.get(limit=1)
        
        """

        url = BASE_URL + '/documents'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id

        convert_datetime_to_string(kwargs, 'modified_since')
        convert_datetime_to_string(kwargs, 'deleted_since')

        view = kwargs.get('view')

        if 'deleted_since' in kwargs:
            view = 'deleted'

        limit = kwargs.get('limit', 20)
        response_params = {'fcn': document_fcns[view], 'view': view, 'limit': limit}

        return self.parent.make_get_request(url, models.DocumentSet.create, kwargs, response_params)

    def get_single(self, **kwargs):
        """
        https://api.mendeley.com/apidocs#!/documents/getDocuments

        Parameters
        ----------
        id :
        group_id : string
            The id of the group that the document belongs to. If not supplied
            returns users documents.
        modified_since : string or datetime
            Returns only documents modified since this timestamp. Should be
            supplied in ISO 8601 format.
        deleted_since : string or datetime
            Returns only documents deleted since this timestamp. Should be
            supplied in ISO 8601 format.
        profile_id : string
            The id of the profile that the document belongs to, that does not
            belong to any group. If not supplied returns users documents.
        authored :
            TODO
        starred :
        limit : string or int (default 20)
            Largest allowable value is 500. This is really the page limit since
            the iterator will allow exceeding this value.
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order
        view :
            - 'bib'
            - 'client'
            - 'tags' : returns user's tags
            - 'patent'
            - 'all'
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'

        Examples
        --------
        from mendeley import API
        m = API()
        d = m.documents.get(limit=1)

        """

        url = BASE_URL + '/documents'
        if 'id' in kwargs:
            id = kwargs.pop('id')
            url += '/%s/' % id

        convert_datetime_to_string(kwargs, 'modified_since')
        convert_datetime_to_string(kwargs, 'deleted_since')

        view = kwargs.get('view')

        if 'deleted_since' in kwargs:
            view = 'deleted'

        limit = kwargs.get('limit', 20)
        response_params = {'fcn': document_fcns[view], 'view': view, 'limit': limit}

        return self.parent.make_get_request(url, models.DocumentSet.create, kwargs, response_params)

    def deleted_files(self, **kwargs):
        """
        Parameters
        ----------
        since
        group_id
        
        
        """
        convert_datetime_to_string(kwargs, 'since')

        url = BASE_URL + '/deleted_documents'
        return self.parent.make_get_request(url, models.deleted_document_ids, kwargs)

    def create(self, doc_data):
        """
        https://api.mendeley.com/apidocs#!/documents/createDocument

        Request URL: https://api.mendeley.com/documents

        Parameters
        ----------
        body : str? dict?
            Enter values for the identifying dict probably?

        Location of DOI in dict:
            'identifiers' key has value which is its own dict.
                Within that dict, DOI has key 'doi'.

        From entering {"identifiers": {"doi": "10.1177/1073858414541484"}}
        as input on the interactive "try it out" Mendeley API implementation,
        it looks like "title" and "type" are required fields.

        "title" = article title
        "type" = 'journal', 'book', etc. Not data types.

        Ex: {"title": "Motor Planning", "type": "journal", "identifiers": {"doi": "10.1177/1073858414541484"}}

        """

        url = BASE_URL + '/documents'

        headers = dict()
        headers['Content-Type'] = 'application/vnd.mendeley-document.1+json'

        return self.parent.make_post_request(url, models.Document, doc_data, headers=headers)


    def create_from_file(self, file_path):
        """
        TODO: We might want some control over the naming
        TODO: Support retrieval from another website

        https://api.mendeley.com/apidocs#!/document-from-file/createDocumentFromFileUpload
        
        """
        filename = basename(file_path)
        headers = {
            'content-disposition': 'attachment; filename=%s' % filename,
            'content-type': mimetypes.guess_type(filename)[0]}

        # TODO: This needs futher work
        pass

    def delete(self):
        """
        https://api.mendeley.com/apidocs#!/documents/deleteDocument
        """
        pass

    def update(self, doc_id, new_data):
        """
        https://api.mendeley.com/apidocs#!/documents/updateDocument
        """
        url = BASE_URL + '/documents/' + doc_id

        headers = dict()
        headers['Content-Type'] = 'application/vnd.mendeley-document.1+json'

        return self.parent.make_patch_request(url, models.Document, new_data, headers=headers)

    def move_to_trash(self, doc_id):

        url = BASE_URL + '/documents/' + doc_id + '/trash'

        headers = dict()
        headers['Content-Type'] = 'application/vnd.mendeley-document.1+json'

        resp =  self.parent.s.post(url, headers=headers, auth = self.parent.access_token)
        return


class MetaData(object):
    # https://api.mendeley.com/apidocs#!/metadata/getDocumentIdByMetadata
    pass


class UserMethods(API):
    """
    This class exposes API calls that are specific to a user.
        
    Example:
    --------
    #TODO: Explain how to get user credentials
    
    #The example below assumes the user credentials have already been acquired
    #and thata default user is specified in the configuration file.
    
    from mendeley import api
    um = api.UserMethods()
    lib_ids = um.docs_get_library_ids(items=100)
    
    """

    def profile_get_info(self, profile_id='me'):
        """
        
        TODO: This may no longer be specific to the user. We should
        write 2 methods, 1 for public and 1 for user
        
        Returns information about a user.
        
        http://dev.mendeley.com/methods/#profiles
        
        Parameters
        ----------
        profile_id : string (default 'me')
            The string 'me' can be used to request information about the
            user whose access token we are using. A numeric value can be used
            to get someone else's contact info.        
        """

        url = self.BASE_URL + '/profiles/' + (profile_id)

        params = {}

        return self.make_get_request(url, models.ProfileInfo, params)

    def docs_get_details(self, **kwargs):
        """
        
        Parameters
        ----------
        view
            - 'bib'
            - 'client'
            - 'tags'
            - 'patent'
            - 'all'
        profile_id : string
            The id of the profile that the document belongs to, that does not 
            belong to any group. If not supplied returns users documents.
        group_id : string
            The id of the group that the document belongs to. If not supplied 
            returns users documents.
        modified_since : string
            Returns only documents modified since this timestamp. Should be 
            supplied in ISO 8601 format.
        deleted_since : string
            Returns only documents deleted since this timestamp. Should be 
            supplied in ISO 8601 format.
        limit : string or int (default 20)
            Largest allowable value is 500
        order :
            - 'asc' - sort the field in ascending order
            ' 'desc' - sort the field in descending order
        sort : string
            Field to sort on. Avaiable options:
            - 'created'
            - 'last_modified'
            - 'title'
            
        Examples
        --------
        from mendeley import api as mapi
        um  = mapi.UserMethods()
        
        1) No options
        docs = um.docs_get_details()


        
        """
        # TODO: Add on more usage examples
        url = self.BASE_URL + '/documents/'

        params = kwargs

        return self.make_get_request(url, models.DocumentSet, params)

    def __repr__(self):
        return \
            'Current User: %s\n' % self.user_name + \
            'Methods:\n' + \
            '   profile_get_info\n' + \
            '   docs_get_details\n'


def convert_datetime_to_string(d, key):
    if key in d and isinstance(d[key], datetime):
        d[key] = d[key].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
