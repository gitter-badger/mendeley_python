# -*- coding: utf-8 -*-
"""

"""

from mendeley import auth
from mendeley import api as mapi


#1 Retrieval of a user token
#-----------------------------
#I've rewritten UserMethods to call this automatically
#
#   ut = auth.get_user_credentials_no_prompts()

#2 Loading a token from disk
#------------------------------
#NOTE: I'd like to expose load via a module method
#at = auth.UserAccessToken.load()

#3 Making a function call
#------------------------------
um  = mapi.UserMethods()
wtf = um.docs_get_details()
import pdb
pdb.set_trace()
wtf = um.profile_get_info()
#wtf = um.docs_get_library_ids(get_all=True)



#4 Public Testing
#-------------------------------
#pc = auth.get_public_credentials()
#pm = mapi.PublicMethods()
#ta = pm.get_top_authors()

import pdb
pdb.set_trace()

#
##wtf = pm.get_entry_details(10461217,'pmid')
##wtf = pm.get_entry_details(12345,'pmid')
#import pdb
#pdb.set_trace()
#
#pm.search_Mendeley_catalog('Year:2007 Author:Grill') #Nothing :/




#pdb.set_trace()