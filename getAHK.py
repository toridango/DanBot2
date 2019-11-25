# -*- coding: utf-8 -*-
def move(dx, dy, tabs = 1):

    return tabs*"\t"+"MouseGetPos, xpos, ypos\n"+tabs*"\t"+"MouseMove, xpos"+dx+", ypos"+dy+"\n"+tabs*"\t"+"Sleep, 10\n"

def pack(d):
    return "+("+d+")*A_Index"

def help():
    print('''
right, down, left, up: take 1 argument: number of pixels of the screen to move ! Don't use negative signs here
diag: 2 arguments: x and y num of pixels
for: 1 argument: number of iterations ! REQUIRES END
end: close loop ! REQUIRES PREVIOUS FOR
*i: index of iteration. place after number. asterisk necessary
''')

def getAHK(code, clickFrame = "on"):

    if clickFrame not in "on off":
        clickFrame = "on"

    clean = code.replace(" ","").replace("\n","").replace("\t","").split(";")

    if clean[-1] == "":
        del clean[-1]

    # print clean

    dx = 0
    dy = 0
    tabs = 1
    ahk = {"on":"\tClick down\n", "off":""}[clickFrame]

    for elem in clean:
        elem = elem.split(":")
        call = elem[0]
        if call not in "end pon poff":
            args = elem[1].split(",")
        # print call, args

        if call in "right down left up":
            try:
                if "*i" in args[0]:
                    dist = args[0].replace("*i", "*A_Index")
                else:
                    dist = args[0]
                dx = {"right":"+"+dist,"down":"","left":"-"+dist,"up":""}[call]
                dy = {"right":"","down":"+"+dist,"left":"","up":"-"+dist}[call]
            except:
                print("Wrong arguments for function "+call+".")

            ahk += move(dx, dy, tabs)

        elif call == "diag":
            try:
                if "*i" in args[0]:
                    dx = args[0].replace("*i", "")
                else:
                    dx = args[0]

                if "*i" in args[1]:
                    dy = str(-1*int(args[1].replace("*i","")))
                else:
                    dy = str(-1*int(args[1]))

                dx = pack(dx)
                dy = pack(dy)

            except:
                print("Wrong arguments for function diag.\nUse: diag: x,y")

            ahk += move(dx, dy, tabs)

        elif call == "for":
            try:
                ahk += tabs*"\t"+"Loop, "+str(args[0])+"\n"+tabs*"\t"+"{\n"
                tabs += 1
            except:
                print("Wrong arguments for function for.\nUse: for: N_iterations;")

        elif call == "end":
            ahk += (tabs-1)*"\t"+"}\n"
            tabs -= 1

        elif call == "pon": # Pencil ON
            ahk += tabs*"\t"+"Click down\n"

        elif call == "poff": # Pencil OFF
            ahk += tabs*"\t"+"Click up\n"


    return ahk+{"on": tabs*"\t"+"Click up", "off":""}[clickFrame]



if __name__ == '__main__':
    # cod = '''
    #         for:20;
    #         right:30;
    #         down:30;
    #         left:30;
    #         up:30;
    #         diag:15,15;
    #         end
    #         '''

    # cod = '''diag:60,60;
    #         diag:60,-60;
    #         left:120;
    #         poff;
    #         diag:30,30;
    #         pon;
    #         right:60;
    #         diag:-30,-30;
    #         diag:-30,30
    #         '''

    # cod = '''
    #         for:5;
    #         up:20*i;
    #         right:20*i;
    #         down:30*i;
    #         left:30*i;
    #         end
    #         '''

    cod = "up:5;"

    print getAHK(cod)
