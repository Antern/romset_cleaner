from subprocess import call
import os
import re

tmp = 'temp_rom_dir'
out = '../clean_romset'
ltmp = './' + tmp

f_mark = '\[f\]'
a_mark = '\[a\]'
good_mark = '\[\!\]'
over_mark = '\[o\]'

usa = '\(U\)'
eu = '\(E\)'

devnull = open(os.devnull, 'w')

def exists(it):
    return (it is not None)

def filter_by_good_codes(good, country, lst):
    return filter(lambda rom: re.search(good, rom) and re.search(country, rom), lst)

def filter_by_good_no_country(good, lst):
    return filter(lambda rom: re.search(good, rom) and not re.search('\(\w{1,2}\)', rom), lst)

def store(filename):
    call(['mv', ltmp + '/' + filename, './' + out + '/'])

def store1(filename, x):
    ech = '"' + x + ': ' + ' '.join(['mv', ltmp + '/' + filename, './' + out + '/']) + '"'
    call(['echo', ech])

def handle_rom_lst(rom_dir):
    romlst = os.listdir(rom_dir)
    # check [f] or [!] with (u)
    lst = filter_by_good_codes(f_mark, usa, romlst) \
            or filter_by_good_codes(a_mark, usa, romlst) \
            or filter_by_good_codes(good_mark, usa, romlst)
    if (len(lst) > 0):
        return lst[0]
    # check f or ! without (x) and (xx)
    lst = filter_by_good_no_country(f_mark, romlst) \
            or filter_by_good_no_country(a_mark, romlst) \
            or filter_by_good_no_country(good_mark, romlst)
    if (len(lst) > 0):
        return lst[0]
    # check [f] or [!] with (e)
    lst = filter_by_good_codes(f_mark, eu, romlst) \
            or filter_by_good_codes(a_mark, eu, romlst) \
            or filter_by_good_codes(good_mark, eu, romlst)
    if (len(lst) > 0):
        return lst[0]
    # check [o] with (u) or (e)
    lst = filter_by_good_codes(over_mark, usa, romlst) \
            or filter_by_good_codes(over_mark, eu, romlst)
    if (len(lst) > 0):
        return lst[0]
    return ''

def prepare_archive(arch_filename, handle_lst, num, total):
    os.system('rm -rf ' + ltmp + '/*') # clean temp dir
    print 'Working on file', num + 1, 'of', total, ':', arch_filename
    call(['7za', 'x', arch_filename, '-o' + tmp], stdout=devnull)
    toX = handle_lst(ltmp)
    if (len(toX) > 0):
        store(toX)
        return
    else:
        # print 'err: Good not found'
        return arch_filename

call(['mkdir', tmp], stdout=devnull)
call(['mkdir', out], stdout=devnull)
dirList = filter(lambda f: os.path.isfile(f) and f.endswith('.7z'), os.listdir('.'))
dirListLen = len(dirList)
err_lst = filter(exists, \
            map(lambda (idx, filename): \
                prepare_archive(filename, handle_rom_lst, idx, dirListLen), enumerate(dirList)))
if (len(err_lst) > 0):
    logfile = open('../missing_in_clean.txt', 'w')
    for err in err_lst:
        print>>logfile, err
    logfile.close()
call(['rm', '-r', ltmp], stdout=devnull)