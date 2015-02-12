rm male_optimal.txt
rm female_optimal.txt

python marriage.py men women >> male_optimal.txt
python marriage.py women men >> female_optimal.txt
echo 'see male_optimal.txt and female_optimal.txt for results'