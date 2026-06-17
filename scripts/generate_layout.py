import json
layout={}
# positions
x_positions={'A':294,'B':331,'C':375,'D':419}
bubble_width=30
bubble_height=30
for q in range(1,26):
    group=(q-1)//5
    within=(q-1)%5
    y_base=606 + within*29 + group*77
    layout[str(q)]={}
    for choice, x in x_positions.items():
        layout[str(q)][choice]=[x,y_base,bubble_width,bubble_height]
with open('layout.json','w') as f:
    json.dump(layout,f,indent=2)
print('layout written to layout.json')
