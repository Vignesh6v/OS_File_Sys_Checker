
from time import time

freestart, freeend,ROOT_BLOCK, MAX_BLOCK_NUM  = 0,0,0,0
DevId = 20
blocksize = 4096
rootstr_blck = str(ROOT_BLOCK)
root_path = 'FS/fusedata.' + rootstr_blck
default_path = 'FS/fusedata.'
superblock_path = 'FS/fusedata.0'
usedblock_list = []
file_data_block_list = []
new_list, block_list = [], []
freeblock_list, notfullblocks = [], []
free_temp_list = []


# Check whether DevID is right
def check_DevId(file):
    global freestart, freeend,ROOT_BLOCK, MAX_BLOCK_NUM,usedblock_list
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
            ROOT_BLOCK = int(root_value)
            print ('Root Block Num: {}'.format(root_value))
            maxb_stp = items.find('"maxBlocks":')
            maxb_edp = items.find(',',maxb_stp)
            maxb_value = items [maxb_stp+12:maxb_edp]
            MAX_BLOCK_NUM = int(maxb_value)
            print ('Max Block Num: {}'.format(maxb_value))
            usedblock_list = list(range(0,ROOT_BLOCK))
            print(' ')
    except:
        print ('Unable to Open the File')

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
                    freeblock_list.append(k)
        except(e):
            print ('Unable to Open the File coz {}'.format(e))
    print ('Length of freeblocks list: {}'.format(len(freeblock_list)))

def get_usedblock_list(block):
        f = open(default_path+str(block), 'r')
        item= f.read()
        f.close()
        counter = 0
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
        if pwd == ROOT_BLOCK:
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
        
    
        
def validate_freeblock_list(f,u):
    print ('Qns 3')
    value = ''
    notlisted_block = []
    totalblock_list = [str(i) for i in range(ROOT_BLOCK, MAX_BLOCK_NUM)]
    freeblocks_list = list(set(totalblock_list).difference(u))
    for i in freeblocks_list:
        if i not in f:
            notlisted_block.append(i)                         
    if len(notlisted_block):
        print('3. i) Error!, The free block list does not contains ALL of the free blocks')
        print ('The blocks that are not listed are: {}'. format(notlisted_block))
        if len(notfullblocks):
            file = open(default_path + str(notfullblocks.pop(0)),  'r' )
            items = file.read()
            block_list = items.split(',')
            new_list = [j.strip('[') for j in block_list]
            new_list = [j.strip(']') for j in new_list]
            if len(new_list) + len(notlisted_block) <= 400:
                for i in notlisted_block:
                    new_list.append(i)
                #file.write(value)
                file.close()
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
            
def check_Time(l):
    for i in l:
        try:
            f = open(default_path+str(i), 'r')
            flag = True
            item = f.read()
            f.close()
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
                print ('Qns 2')
                f = open(default_path+str(i), 'w+')
                print ('Updating the Time for Block Num: {}'.format(i))
                chngd_item = item[:atime_stp+8]+str(atime_value)+item[atime_edp:ctime_stp+8]+str(ctime_value)+item[ctime_edp:mtime_stp+8]+str(mtime_value)+item[mtime_edp:]
                f.write(chngd_item)
        except(e):
            print ('2. Unable to open the file coz{}'.format(e))

 
def main():
    print ('Started')
    check_DevId(superblock_path)
    print ('Qns 4')
    get_usedblock_list(ROOT_BLOCK)
    print (' ')
    print ('Used Block List')
    print (usedblock_list)
    print (' ')
    print ('Free Block List')
    get_freeblock_list(usedblock_list)
    print (' ')
    validate_freeblock_list(freeblock_list, usedblock_list)
    print (' ')
    check_Time([26])
    print (' ')
    print ('done')



if __name__ == '__main__':main()
