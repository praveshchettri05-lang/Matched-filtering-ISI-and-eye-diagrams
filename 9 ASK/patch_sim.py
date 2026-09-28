import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('ask_fsk_simulator.py', 'r', encoding='utf-8') as f:
    text = f.read()

old = 'import matplotlib.pyplot as plt'
new = 'import matplotlib\nmatplotlib.use("Agg")\nimport matplotlib.pyplot as plt'
text = text.replace(old, new, 1)

with open('ask_fsk_simulator.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Agg backend added.')
