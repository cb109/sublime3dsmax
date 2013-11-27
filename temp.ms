mult=10
for x=1 to 10 by 2 do
    for y=1 to 10 by 2 do
        for z=1 to 10 by 2 do
            sphere radius:5 segments:8 pos:[x*mult,y*mult,z*mult]\
                wirecolor:(random black white)