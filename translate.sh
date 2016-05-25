#!/bin/sh

# Cleanup python cache
echo "Cleanup python cache"
find . -name "__pycache__" -exec rm -rf {} \;

# Generate the needed .pro files
echo "Generate qt project file for lisp ..."
./generate_qt_pro.py \
    -r lisp \
    -e lisp/modules/ lisp/plugins/ \
    -x py \
    -o linux-show-player.pro \
    -s lisp/plugins lisp/modules \
    -t lisp/i18n \
    -l lisp_it_IT.ts

echo "Generate qt project file for modules ..."
MODULES=$(find ./lisp/modules/ -mindepth 1 -maxdepth 1 -type d)

./generate_qt_pro.py \
    -r lisp/modules \
    -e lisp/modules \
    -x py \
    -o lisp/modules/modules.pro \
    -s $MODULES \

for plug in $MODULES
do
    echo "  > $(basename $plug)"
    ./generate_qt_pro.py \
        -r $plug \
        -x py \
        -o $plug"/"$(basename $plug)".pro" \
        -t $plug"/i18n" \
        -l $(basename $plug)"_it_IT.ts"
done

echo "Generate qt project file for plugins ..."
PLUGINS=$(find ./lisp/plugins/ -mindepth 1 -maxdepth 1 -type d)

./generate_qt_pro.py \
    -r lisp/plugins \
    -e lisp/plugins \
    -x py \
    -o lisp/plugins/plugins.pro \
    -s $PLUGINS \

for plug in $PLUGINS
do
    echo "  > $(basename $plug)"
    ./generate_qt_pro.py \
        -r $plug \
        -x py \
        -o $plug"/"$(basename $plug)".pro" \
        -t $plug"/i18n" \
        -l $(basename $plug)"_it_IT.ts"
done


# Update translation files
pylupdate5 -verbose -noobsolete linux-show-player.pro
