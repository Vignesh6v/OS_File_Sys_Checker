
from time import time

freestart, freeend,ROOT_BLOCK, MAX_BLOCK_NUM  = 0,0,0,0
DevId = 20
blocksize = 4096
current_time = int(time())
rootstr_blck = str(ROOT_BLOCK)
root_path = 'FS/fusedata.' + rootstr_blck
default_path = 'FS/fusedata.'
superblock_path = 'FS/fusedata.0'
used_block_list = [ROOT_BLOCK]
file_data_block_list = []
new_list, block_list = [], []
freeblock_list = []
free_temp_list = []


# Check whether DevID is right
def check_DevId(file):
    global freestart, freeend,ROOT_BLOCK, MAX_BLOCK_NUM
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
    except:
        print ('Unable to Open the File')

def get_freeblock_list():
    for i in range(freestart, freeend+1):
        try: 
            f = open(default_path+str(i), 'r')
            items = f.read()
            f.close()
            block_list = items.split(',')
            new_list = [j.strip('[') for j in block_list]
            new_list = [j.strip(']') for j in new_list]
            for k in new_list:
                freeblock_list.append(k)
        except:
            print ('Unable to Open the File')
    print ('Length of freeblocks list: {}'.format(len(freeblock_list)))
        

def main():
    print ('Started')
    check_DevId(superblock_path)
    get_freeblock_list()


if __name__ == '__main__':main()
