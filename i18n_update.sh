#!/bin/sh

# Locales of which generate translation files
LOCALES=("it_IT")

echo "UPDATE TRANSLATIONS FOR APPLICATION"
./generate_pro_files.py -r lisp \
                         -e lisp/modules lisp/plugins \
                         -x py \
                         -l ${LOCALES[@]}

pylupdate5 -verbose -noobsolete "lisp/lisp.pro"

echo "#########################################"
echo ">>> UPDATE TRANSLATIONS FOR MODULES"
MODULES=$(find lisp/modules/ -mindepth 1 -maxdepth 1 -type d)

for module in $MODULES
do
    if [ -a $module"/i18n/" ];
    then
        ./generate_pro_files.py -r $module -x py -l ${LOCALES[@]}

        pylupdate5 -verbose -noobsolete $module"/"$(basename $module)".pro"
    fi
done

echo "#########################################"
echo ">>> UPDATE TRANSLATIONS FOR PLUGINS"
PLUGINS=$(find lisp/plugins/ -mindepth 1 -maxdepth 1 -type d)

for plugin in $PLUGINS
do
    if [ -a $plugin"/i18n/" ];
    then
        ./generate_pro_files.py -r $plugin -x py -l ${LOCALES[@]}

        pylupdate5 -verbose -noobsolete $plugin"/"$(basename $plugin)".pro"
    fi
done
