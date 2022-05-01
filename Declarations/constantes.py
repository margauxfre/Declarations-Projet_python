from warnings import warn

RESULTATS_PAR_PAGE = 10

SECRET_KEY = "C'est la clef secrète !"

if SECRET_KEY == "C'est la clef secrète !":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)
