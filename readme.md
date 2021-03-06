# Mendeley Code For Python #
This repo implements the Mendeley API in Python. It also implements a client library. It will also implement library analysis code.

##Motivation##

The focus is on developing scripting access to my Mendeley data, particularly user data. As a simple example, one might wish to know which of their Mendeley entries are missing valid Pubmed IDs, and remedy this by adding them. Doing this would help to ensure higher quality meta data. As another example, one might wish to know which of the references from a paper they are reading are in their library or not. By writing code we can make a query to the API for this information.

Mendeley provides a [Python SDK](https://github.com/Mendeley/mendeley-python-sdk). This version is meant to provide tighter support (specifically integration of methods into response objects) for further analysis.  This version does not yet implement all available [API methods] (https://api.mendeley.com/apidocs/docs) although they are slowly being added. Additionally, adding new methods is relatively straightforward.


##Current Plans##

(as of May 30, 2016)

We are currently working on building in support for a reference retrieval program. Steps in this program include:

1. Retrieving references for a paper (via the pypub and reference_resolver repositories)
2. Determining which references are in the user library.
3. Adding missing references (on demand) via a GUI along with the main file (article).

## Getting Started ##

1. Copy the config_template into a file config.py and fill in the appropriate values. This will require signing up for a [Mendeley API account](https://mix.mendeley.com/portal#/register). Importantly, the redirect API should be: **https://localhost**
2. Your library can then be loaded as:

```python
from mendeley import client_library
c = client_library.UserLibrary()
#c.docs will contain a pandas dataframe of your library
```

##Contributing##

We welcome contributions. If you are interested please email Jim.

## Requirements ##

TODO: This is out of date

This needs some work but relies heavily on:
1. **Requests**
2. **Pandas**