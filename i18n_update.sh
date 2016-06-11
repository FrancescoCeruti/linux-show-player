#!/bin/sh

# Locales of which generate translation files
LOCALES=("it_IT")

# Cleanup python cache
echo ">>> CLEAN PYTHON CACHE"
find . -name "__pycache__" -exec rm -rf {} \;

echo "UPDATE TRANSLATIONS FOR APPLICATION"
# Main application .ts files (one for locale)
TS_FILES=()
for locale in ${LOCALES[@]}
do
    TS_FILES+=("lisp/i18n/lisp_"$locale".ts")
done

pylupdate5 -verbose -noobsolete \
    $(./search_source_files.py -r lisp -e lisp/modules lisp/plugins -x py) \
    -ts ${TS_FILES[@]}

echo "#########################################"
echo ">>> UPDATE TRANSLATIONS FOR MODULES"
MODULES=$(find lisp/modules/ -mindepth 1 -maxdepth 1 -type d)

for module in $MODULES
do
    # Module .ts files (one for locale)
    TS_FILES=()
    for locale in ${LOCALES[@]}
    do
        TS_FILES+=($module"/i18n/"$(basename $module)"_"$locale".ts")
    done

    if [ -a $module"/i18n/" ];
    then
        pylupdate5 -verbose -noobsolete \
            $(./search_source_files.py -r $module -x py) \
            -ts ${TS_FILES[@]}
    fi
done

echo "#########################################"
echo ">>> UPDATE TRANSLATIONS FOR PLUGINS"
PLUGINS=$(find lisp/plugins/ -mindepth 1 -maxdepth 1 -type d)

for plugin in $PLUGINS
do
    # Plugin .ts files (one for locale)
    TS_FILES=()
    for locale in ${LOCALES[@]}
    do
        TS_FILES+=($plugin"/i18n/"$(basename $plugin)"_"$locale".ts")
    done

    if [ -a  $plugin"/i18n/" ];
    then
        pylupdate5 -verbose -noobsolete \
            $(./search_source_files.py -r $plugin -x py) \
            -ts ${TS_FILES[@]}
    fi
done

