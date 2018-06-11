# django-shift

Lightweight REST app for Django that allows you to make small date-based versions with a bundle of changes without maintaining each version. Rather, you always mantain the most recent version and make ```migrations``` for each change, so effectively the API renders the latest version and migrates it backwards to the version you want to use.

# Coding style

The code base must be compatible with both python 2.7 as well as 3.6+ and we are using type annotations where it makes sense. The type annotations are used in testing with ```mypy``` but also enhances IDE experience.

After v1 we want to keep any API consistent so the project does not break in different ways when you upgrade.