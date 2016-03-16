#using python 3.5 verison

import os
from time import time

#variables
freestart, freeend,root_block, max_block  = 0,0,0,0
DevId = 20
blocksize = 4096
rootstr_blck = str(root_block)
root_path = 'FS/fusedata.' + rootstr_blck
default_path = 'FS/fusedata.'
entry_path = 'FS/fusedata.0'
usedblock_list = []
new_list, block_list = [], []
freeblock_list, notfullblocks = [], []



# Check whether DevID is right
def check_DevId(file):
    global freestart, freeend,root_block, max_block,usedblock_list
    try:
        f = open(file,'r')
        items = f.read()
        f.close()
        devid_stp = items.find('"devId":')
        devid_edp = items.find(',',devid_stp)
        devid_value = items [devid_stp+8:devid_edp]
        devID = int(devid_value)
        if devID != DevId:
            print ('DevId for the file system is wrong. It should be 20')
        else:
            print ('Qns 1')
            print ('The devID is right!')
            fs_stp = items.find('"freeStart":')
            fs_edp = items.find(',',fs_stp)
            fs_value = items [fs_stp+12:fs_edp]
            freestart = int(fs_value)
            print ('FreeStart Block Num: {}'.format(fs_value))
            fe_stp = items.find('"freeEnd":')
            fe_edp = items.find(',',fe_stp)
            fe_value = items [fe_stp+10:fe_edp]
            freeend = int(fe_value)
            print ('FreeEnd Block Num: {} '.format(fe_value))
            root_stp = items.find('"root":')
            root_edp = items.find(',',root_stp)
            root_value = items [root_stp+7:root_edp]
            root_block = int(root_value)
            print ('Root Block Num: {}'.format(root_value))
            maxb_stp = items.find('"maxBlocks":')
            maxb_edp = items.find(',',maxb_stp)
            maxb_value = items [maxb_stp+12:maxb_edp]
            max_block = int(maxb_value)
            print ('Max Block Num: {}'.format(maxb_value))
            usedblock_list = list(range(0,root_block))
            print(' ')
    except:
        print ('Unable to Open the File')

#to get the used list of blocks
def get_usedblock_list(block):
        f = open(default_path+str(block), 'r')
        item= f.read()
        f.close()
        counter = 0
        fcount = 0
        #traverse through the directories
        while True:
            tp = int(item.find('type":"d"', counter))
            stp = item.find('location":',tp)
            edp = item.find('}',stp)
            sname = item.find('name":"',tp)
            ename = item.find('",',sname)
            location = item[stp+10:edp]
            if tp > 0:
                get_directory( location, item[sname+7:ename], block)
                counter = (tp+1)
            else:
                break
        #traverse through the files
        while True:
            tp = int(item.find('type":"f"', fcount))
            stp = item.find('location":',tp)
            edp = item.find('}',stp)
            location = item[stp+10:edp]
            if tp > 0:
                get_file( location, block)
                fcount = (tp+1)
            else:
                break

            
#directory informations
def get_directory(block, name, pwd):
    #present working directory
    if name == '.':
        usedblock_list.append(int(pwd))
        if int(block) == int(pwd):
        	print ('Correct . directory for block {}'.format(pwd))
        else:
            print ('Error! the block {} does not contain the correct location of  . directory'.format(pwd))
    #parent working directory
    elif name == '..':
        f = open(default_path+str(block), 'r')
        content = f.read()
        f.close()
        if pwd == root_block:
            val = content.find('name":"..","location":'+str(pwd))
        else:
            val = content.find('"location":'+str(pwd))
        if val != -1:
            print ('Correct .. directory for block {}'.format(pwd))
        else:
            print ('Error! the block {} does not contain the correct location of  .. directory'.format(pwd))
    #other directories
    else:
        get_usedblock_list(block)


#file informations
def get_file(block, pwd):
    if (block not in usedblock_list):
        usedblock_list.append(int(block))
    f = open(default_path+str(block), 'r')
    item = f.read()
    f.close()
    indirect_stp = item.find('indirect":')
    indirect_etp = item.find(',',indirect_stp)
    indirect_loc = int(item[indirect_stp+10: indirect_etp])
    loc_stp = item.find('location":')
    loc_etp= item.find(',',loc_stp)
    loc = int(item[loc_stp+10:loc_etp])
    usedblock_list.append(loc)
    if indirect_loc != 0:
        if indirect_loc == 1:
            #location pointer points to an array?
            f = open(default_path+str(loc), 'r')
            item = f.read()
            f.close()
            block_list = item.split(',')
            new_list = [j.strip('[') for j in block_list]
            new_list = [j.strip(']') for j in new_list]
            len_of_array = len(new_list)
            print (' ')
            print ('Qns 5')
            try:
                for i in new_list:
                    f = int(i)
                print ('the data in the block {} pointed to, by location pointer is an array'.format(block))
                usedblock_list.append(int(i))
            except:
                print ('Not a valid array in the location {}'.format(block))
                print (' ')
        size_of_file = 0
        for i in new_list:
            size_of_file += os.path.getsize(default_path+new_list.pop(0))

        #indirection check
        if size_of_file < (400*len_of_array) or size_of_file > (400*(len_of_array-1)):
            if size_of_file < 400:
                print ('Error! Could be stored in single block with indirect = 0 as the size of file is {} '.format(size_of_file))
            else:
                print ('File having Indirect = 1 correct and size is Valid')
        else:
            print ('Error! We are dealing with only One Indirection')
    else:
        usedblock_list.append(loc)
        size_of_file = os.path.getsize(default_path+str(loc))
        if size_of_file > 0 and size_of_file < 400:
            print ('Size is valid for file at {} Block'.format(pwd))
        else:
            print ('Error! Invalid size of file. beyond the capacity of a block.')


#to get the free list of blocks
def get_freeblock_list(usedblock_list):
    global freeblock_list
    for i in range(freestart, freeend+1):
        try: 
            f = open(default_path+str(i), 'r')
            items = f.read()
            f.close()
            block_list = items.split(',')
            new_list = [j.strip('[') for j in block_list]
            new_list = [j.strip(']') for j in new_list]
            if len(new_list) < 400:
                notfullblocks.append(i)
            for k in new_list:
                c = int(k)
                if c not in usedblock_list:
                    freeblock_list.append(int(k))
        except(e):
            print ('Unable to Open the File coz {}'.format(e))
    print ('Length of freeblocks list: {}'.format(len(freeblock_list)))



#validating the free block list
def validate_freeblock_list(f,u):
    print ('Qns 3')
    value = ''
    notlisted_block = []
    totalblock_list = [int(i) for i in range(root_block, max_block)]
    freeblocks_list = list(set(totalblock_list).difference(u))
    for i in freeblocks_list:
        if i not in f:
            notlisted_block.append(i)                         
    if len(notlisted_block):
        print('3. i) Error!, The free block list does not contains ALL of the free blocks')
        print ('The blocks that are not listed are: {}'. format(notlisted_block))
        if len(notfullblocks):
            temp_filenum = str(notfullblocks.pop(0))
            file = open(default_path + temp_filenum,  'r' )
            items = file.read()
            file.close()
            block_list = items.split(',')
            new_list = [j.strip('[') for j in block_list]
            new_list = [j.strip(']') for j in new_list]
            if len(new_list) + len(notlisted_block) <= 400:
                v = items[:-1]
                val = ''
                counter = 0
                for i in notlisted_block:
                    val +=','+str(i)
                    counter+=1
                    freeblock_list.append(i)
                result = v+val+']'
                print ('After update, the length of Free Block List is: {}'.format(len(freeblock_list)))
                write_file = open(default_path + temp_filenum,  'w' )
                print ('check on file {}'.format(temp_filenum))
                write_file.write(result)
                write_file.close()
            else:
                print ('unable to append the free list in single block')              
    else:
        print('3. i) The free block list contains ALL of the free blocks')
    flag = False    
    for i in u:
        if i in f:
            print('3. ii) Error!, The Block {} is actually used but its available in Free list Blocks'.format(i))
            flag = True
    if flag == False:
        print('3. ii) All used block are not available in the Free list Blocks')



# Time check only in the used blocks and will skip the blocks that don't have time fields            
def check_Time(l):
    for i in l:
        try:
            f = open(default_path+str(i), 'r')
            flag = True
            item = f.read()
            f.close()
            if (item.find('"atime":') != -1 or item.find('"ctime":') != -1 or item.find('"mtime":') != -1):
                atime_stp = item.find('"atime":')
                atime_edp = item.find (',',atime_stp)
                atime_value = item[atime_stp+8:atime_edp]
                if int(atime_value) < int(time()):
                    atime_value = int(time())
                    flag = False

                ctime_stp = item.find('"ctime":')
                ctime_edp = item.find (',',ctime_stp)
                ctime_value = item[ctime_stp+8:ctime_edp]
                if int(ctime_value) < int(time()):
                    ctime_value = int(time())
                    flag = False

                mtime_stp = item.find('"mtime":')
                mtime_edp = item.find (',',mtime_stp)
                mtime_value = item[mtime_stp+8:mtime_edp]
                if int(mtime_value) < int(time()):
                    mtime_value = int(time())
                    flag = False
                
                if flag == False:
                    f = open(default_path+str(i), 'w+')
                    print ('Updating the Time for Block Num: {}'.format(i))
                    chngd_item = item[:atime_stp+8]+str(atime_value)+item[atime_edp:ctime_stp+8]+str(ctime_value)+item[ctime_edp:mtime_stp+8]+str(mtime_value)+item[mtime_edp:]
                    f.write(chngd_item)
            else:
                pass
        except(e):
            print ('2. Unable to open the file coz{}'.format(e))


#main function call 
def main():
    print ('Started')
    print (' ')
    check_DevId(entry_path)
    print ('Qns 4')
    get_usedblock_list(root_block)
    print (' ')
    print ('Used Block List')
    print (usedblock_list)
    print (' ')
    print ('Free Block List')
    get_freeblock_list(usedblock_list)
    print (' ')
    validate_freeblock_list(freeblock_list, usedblock_list)
    print (' ')
    print ('Qns 2')
    check_Time(usedblock_list)
    print (' ')
    print ('Done!')



if __name__ == '__main__':main()
