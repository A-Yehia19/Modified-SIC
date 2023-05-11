import pandas as pd
import math

##############################
def index_2d(myList, v):
    for i, x in enumerate(myList):
        if v in x:
            return i
############################## create filler line for headers
src = open("in.txt", "r")
oline = src.readlines()
fline = ''
for fff in oline:
    fline = fff
    break
# fline = "5     COPY    START  1000     COPY FILE FROM INPUT TO OUTPUT\n"
# Here, we prepend the string we want to on first line
oline.insert(0, fline)
src.close()
src = open("in.txt", "w")
src.writelines(oline)
src.close()
###############################


df = pd.read_fwf("in.txt")


#############################################delete filler line
with open('in.txt', 'r') as fin:
    kkkk = fin.read().splitlines(True)
with open('in.txt', 'w') as fout:
    fout.writelines(kkkk[1:])
#################################################################

df.columns = ['lines', 'var', 'inst', 'value', 'comm']
df.drop(["lines", "comm"], axis=1, inplace=True)
df.fillna('     ', inplace=True)  # replaces all NaNs with spaces
intermed = open("intermediate.txt", 'w')
for x in range(df.shape[0]):  # byreturn number of rows w by loop 3leha kolaha
    var = df._get_value(x, 'var')
    inst = df._get_value(x, 'inst')
    value = df._get_value(x, 'value')
    line = var + ' \t' + inst + '   \t' + value + '\n'
    intermed.write(line)
intermed.close()
########################################location counter#######################################
instructions = [
    ['ADD', 3, '18'],
    ['AND', 3, '40'],
    ['COMP', 3, '28'],
    ['DIV', 3, '24'],
    ['J', 3, '3C'],
    ['JEQ', 3, '30'],
    ['JGT', 3, '34'],
    ['JLT', 3, '38'],
    ['JSUB', 3, '48'],
    ['LDA', 3, '00'],
    ['LDCH', 3, '50'],
    ['LDL', 3, '08'],
    ['LDX', 3, '04'],
    ['MUL', 3, '20'],
    ['OR', 3, '44'],
    ['RD', 3, 'D8'],
    ['RSUB', 3, '4C'],
    ['STA', 3, '0C'],
    ['STCH', 3, '54'],
    ['STL', 3, '14'],
    ['STSW', 3, 'E8'],
    ['STX', 3, '10'],
    ['SUB', 3, '1C'],
    ['TD', 3, 'E0'],
    ['TIX', 3, '2C'],
    ['WD', 3, 'DC'],
    ['FIX', 1, 'C4'],
    ['FLOAT', 1, 'C0'],
    ['HIO', 1, 'F4'],
    ['NORM', 1, 'C8'],
    ['SIO', 1, 'F0'],
    ['TIO', 1, 'F8']
]
address = []
counter = int(df._get_value(0, 'value'), base=16)                                    # convert hex to decimal to add
for x in range(df.shape[0]):
    inst = df._get_value(x, 'inst')
    address.append(hex(counter))
    if inst.upper() == 'BYTE'.upper():                                                # to not make it case sensitive
        length = 0
        chars = df._get_value(x, 'value').split(',')
        for i in chars:
            if i[0].upper() == 'C':
                length += len(i) - 3
            elif i[0].upper() == 'X':
                length += int((len(i) - 3) / 2)
        counter = counter + length
    elif inst.upper() == 'RESB'.upper():
        counter = counter + int(df._get_value(x, 'value'))
    elif inst.upper() == 'RESW'.upper():
        counter = counter + 3 * int(df._get_value(x, 'value'))
    elif inst.upper() == 'START'.upper():
        counter = counter  #mate3melsh 7aga
    elif inst.upper() == 'END'.upper():
        break
    elif inst.upper() == 'WORD'.upper():
        chars = df._get_value(x, 'value').split(',')
        counter = counter + 3*len(chars)
    else:
        index = index_2d(instructions, inst.upper())  # returns the index of instruction in array instruction
        ay7aga = instructions[index][1]  # to get the format of the instruction
        counter = counter + ay7aga

##################################create file with location counter##################################
df.insert(0, "location", address, True)
out1 = open("out_pass1.txt", 'w')
for x in range(df.shape[0]):  # byreturn number of rows w by loop 3leha kolaha
    loc = df._get_value(x, 'location')
    var = df._get_value(x, 'var')
    inst = df._get_value(x, 'inst')
    value = df._get_value(x, 'value')
    line = loc + '\t' + var + ' \t' + inst + '   \t' + value + '\n'
    out1.write(line)
out1.close()
#####################################symbol table##############################################
sym = []
address = []
for x in range(df.shape[0]):
    var = df._get_value(x, 'var')
    if var in sym:
        print("error in found multi symbol declaration of \'"+ var+'\'\n')
    if var != '     ' and var not in sym:
        loc = df._get_value(x, 'location')
        sym.append(var)
        address.append(loc)
##################################create file with symbol table##################################
symbol = open("symbTable.txt", 'w')
for x in range(len(address)):  # btloop 3ala el array kolo
    line = str(str(address[x]+ '\t' + sym[x])) + '\n'
    symbol.write(line)
symbol.close()

################################pass 2 (object codes)###########################################
obj = []
obj.append ('')
for x in range(1,df.shape[0]-1):  # btloop 3ala el array kolo
    inst=df._get_value(x,'inst')
    value=df._get_value(x, 'value') #el raqam ellygamb el instruction

    if inst.upper() != 'BYTE' and inst.upper() != 'WORD' and inst.upper() != 'RESW' and inst.upper() != 'RESB':
        index=index_2d(instructions,inst)   # search 3ala el instruction in the instruction list
        format=instructions[index][1]
        opcode=instructions[index][2]
        if inst.upper() == 'RSUB':
            obj.append('0x4c0000')
        elif format==1:
            obj.append('0x'+opcode)
            ##############
        elif format==3:
            if value[0] != '#':
                objectcode =bin(int(opcode, 16))[2:].zfill(8)     # da 3san ye7awel el hexa le binary
                temp=value.split(',')
                if len(temp)==2:
                    objectcode = objectcode+ '1'
                else:
                    objectcode = objectcode + '0'
                idx=sym.index(temp[0])                              #kda gebt el index bta3 el value gowa array el sym
                addr=bin(int(address[idx], 16))[2:].zfill(15)           # da 3san ye7awel el address elhexa le binary
                objectcode=objectcode+addr
                objectcode = hex(int(objectcode, 2))[2:].zfill(6)
                # if inst.upper() == 'LDA':
                #     objectcode = '0x00'+objectcode[2:]
                obj.append('0x'+objectcode)
            else:                                                 ####### immediate case#######
                objectcode = bin(int(opcode, 16))[2:].zfill(8)    # da 3san ye7awel el obcode el hexa le binary
                objectcode=objectcode[:7]                         #3shan asheel a5er bit (bits from 0 to 6)
                objectcode=objectcode+'1'
                temp = value.split(',')                           ##to search if there is x##
                if len(temp) == 2:                                  #
                    objectcode = objectcode + '1'                   #
                else:                                               #
                    objectcode = objectcode + '0'                 ##########################
                num=temp[0]
                num=num[1:]                                       # hy5aly el string yebda2 mn index 1 l7d el a5er (3shan asheel el #)
                addr=bin(int(num))[2:].zfill(15)
                objectcode=objectcode+addr
                obj.append('0x'+hex(int(objectcode,2))[2:].zfill(6))
    else:
        if inst.upper() == 'RESB' or inst.upper() == 'RESW':
            obj.append("")
        elif inst.upper() == 'WORD':   #1234,5678
            temp = value.split(',')    #[1234, 5678]
            objectttttt = '0x'
            for val in temp:
                objectttttt += hex(int(val))[2:].zfill(6)
            obj.append(objectttttt)
        elif inst.upper() == 'BYTE':
            chars = value.split(',')
            objectttttt = '0x'
            for i in chars:
                if i[0].upper() == 'C': #c'eof'
                    for let in range(2, len(i)-1):
                        objectttttt += hex(ord(i[let]))[2:].zfill(2)
                elif i[0].upper() == 'X':
                    objectttttt += i[2:-1]
            obj.append(objectttttt)

obj.append("")
df.insert(4, "object", obj, True)
pass2 = open("out_pass2.txt", 'w')
for x in range(df.shape[0]):  # btloop 3ala el array kolo
    loc = df._get_value(x, 'location')
    var = df._get_value(x, 'var')
    inst = df._get_value(x, 'inst')
    value = df._get_value(x, 'value')
    objectt = df._get_value(x, 'object')
    line = loc + '\t' + var + ' \t' + inst + '   \t' + value + ' \t\t' + objectt + '\n'
    pass2.write(line)
pass2.close()

######################################## HTE #############################################
hte = open("HTE.txt", 'w')
prog_name = df._get_value(0,'var').zfill(6)
stat_address = df._get_value(0,'location')[2:].zfill(6)
end_address = df._get_value(df.shape[0]-1,'location')[2:].zfill(6)
prog_len = int(end_address, base=16) - int(stat_address, base=16)  #convert to decimal to be able to subtract
prog_len = hex(prog_len)[2:].zfill(6)                                  #return it to hexa
line = 'H ' + prog_name +' '+ stat_address +' '+ prog_len+'\n'
hte.write(line)

#T records
start_record = stat_address                           #initial value of the address
object_code_Trecord = ''
for x in range(1,df.shape[0]):
    inst = df._get_value(x,'inst')
    current_address = df._get_value(x,'location')[2:].zfill(6)
    record_length = int(current_address, base=16) - int(start_record, base=16)

    if record_length >= 30 or inst.upper() == 'RESW' or inst.upper() == 'RESB' or x==df.shape[0]-1 or len(object_code_Trecord.split(' '))>10:
        record_end = df._get_value(x,'location')
        record_length = int(record_end, base=16) - int(start_record, base=16)
        record_length = hex(record_length)[2:].zfill(2)

        tline = 'T '+ start_record +" "+ record_length +" "+ object_code_Trecord + '\n'
        if len(tline.split(' '))>5:
            hte.write(tline)
        object_code_Trecord = ''
        object_code_Trecord += df._get_value(x, 'object')[2:]+" "

        if inst.upper() == 'RESW' or inst.upper() == 'RESB':
            continue
        else:
            start_record = current_address
    else:
        object_code_Trecord += df._get_value(x, 'object')[2:]+" "


line = 'E ' + stat_address.zfill(6)
hte.write(line)
hte.close()

input('Program finished. Press Enter to close...')