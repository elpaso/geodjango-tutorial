NAME=$1
THEME=django
#THEME=default2
python rst-directive.py \
    --stylesheet=pygments.css \
    --theme-url=ui/${THEME} \
    ${NAME}.rst > ${NAME}.html
