import msvcrt

buf = ""

while True:
    c = msvcrt.getwch()

    if msvcrt.kbhit():
        buf+=c
    elif buf:
        buf+=c
        print(buf)
        buf = ""

    

        
    

