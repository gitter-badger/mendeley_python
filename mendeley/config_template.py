# -*- coding: utf-8 -*-
"""

This module stores user parameters. The _template
version is only meant as an example. A new user should
copy this version into "config.py" and fill in the values
as appropriate.

The "config.py" file is ignored from GIT commits so as to not be public


"""

#Required. This can be obtained from Mendeley.
#
#   http://dev.mendeley.com/
#
class Oauth2Credentials(object):
    client_secret = '' #e.g. 'FfrRTSTasdfasdfasdfasdfsdfasdf3u'
    client_id     = '' #e.g. '200'
    redirect_url  = 'https://localhost'
    
#Optional but recommended for personal methods
class DefaultUser(object):
    user_name = '' #e.g. bob@smith.com
    password = ''  #e.g. 'password123'

#This is needed for other users        
class User(object):
    
    def __init__(self,user_name,password):
        self.user_name = user_name
        self.password = password
   
#The key is an alias     
other_users = {'testing':User('jim@smith.com','my_testing_pass')}

#Fill this in to save the data in a location other than the "data" folder
#in the root of this repository.
default_save_path = 'C:/box_sync/mendeley_data'
