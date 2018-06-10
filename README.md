# django-shift

Lightweight REST app for Django that allows you to make small date-based versions with a bundle of changes without maintaining each version. Rather, you always mantain the most recent version and make ```migrations``` for each change, so effectively the API renders the latest version and migrates it backwards to the version you want to use.
