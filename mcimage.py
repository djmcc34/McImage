#!/usr/bin/env python3

import sys
import requests
import bs4
import os
import urllib
import logging
import shutil
import zipfile
from time import gmtime, strftime
from os.path import expanduser
from optparse import OptionParser


class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"



def main(opener):
    VERSION = '1.0 Beta'
    try:

        

        usage = '''
%prog url [options] -d -f -n -m -s -v -q --nuke --zip --cbz
'''

        parser = OptionParser(usage=usage, version='%prog {0}'.format(VERSION))
        
        parser.add_option('-d', '--directory', action='store', type='string', dest='loc', help='allows user to enter filepath for desired local download direcory.\n')
        parser.add_option('-f', '--folder', action='store', type='string', dest='folder', help='allows user to specify a folder/directory name for downloads.\n')
        parser.add_option('-n', '--filename', action='store', type='string', dest='filename', help='allows user to specify how images will be named.\n')
        parser.add_option('--4chan', action='store_true', dest='shitchan', help='Set to 4chan mode, hint: use this if you are retrieving images from 4chan.\n')
        parser.add_option('-s', '--save', action='store', type='string', dest='save', help='allows the user to select different ways to save file(overwrite, erase=filename, preserve=filename).\n')
        parser.add_option("-v", action="store_true", dest="verbose", default=True, help='Turns verbose mode on(default).\n')
        parser.add_option("--nuke", action="store_true", dest="nuke", default=False, help='removes all files in directory trying to be saved to unless preserved with -s preserve=filename.\n')
        parser.add_option("-q", action="store_false", dest="verbose", help='Turns verbose mode off.\n')
        parser.add_option("--zip", action='store_true', dest="zip1", help='Store contents of image retrieval in .zip archive.\n')
        parser.add_option("--cbz", action='store_true', dest="cbz", help='Store contents of image retrieval in .cbz(comic book) archive.\n')
        
        (options, args) = parser.parse_args()
        loc=options.loc
        folder=options.folder
        filename=options.filename
        nuke=options.nuke
        zip1=options.zip1
        cbz=options.cbz
        archive = True if zip1 or cbz else False
        if filename is None:
            filename = 'image' 
        shitchan=options.shitchan
        save=options.save
        verbose = options.verbose
        if verbose:
            def vprint(*args):
                for arg in args:
                   print(arg),
                print()
        else:   
            vprint = lambda *a: None
        if os.path.isdir(expanduser('~/Pictures')):
            HOME = expanduser('~/Pictures') 
        else:
            if os.path.isdir(os.path.join(os.environ["HOME"], 'Pictures')):
                HOME = os.path.join(os.environ["HOME"], 'Pictures')
            else:
                if os.path.isdir(os.path.join(expanduser('~'),'Pictures')):
                    HOME = os.path.join(expanduser('~'),'Pictures')
                else:
                    if os.path.isdir(expanduser('~')):
                        os.mkdir(os.path.join(expanduser('~'), 'Pictures'))
                        if os.path.isdir(os.path.join(expanduser('~'),'Pictures')):
                            vprint('Pictures directory created.')
                            HOME = os.path.join(expanduser('~'),'Pictures')
                    else:
                        if os.path.isdir(os.environ["HOME"]):
                            os.mkdir(os.path.join(os.environ["HOME"], 'Pictures'))
                            if os.path.isdir(os.path.join(os.environ["HOME"], 'Pictures')):
                                vprint('Pictures directory created.')
                                HOME = os.path.join(os.environ['HOME'], 'Pictures')
        
        if not os.path.isdir(os.path.join(HOME, 'McImage')):
            vprint('McImage directory not found, creating McImage directory')
            os.mkdir(os.path.join(HOME, 'McImage'))
            if os.path.isdir(os.path.join(HOME, 'McImage')):
                PATH = os.path.join(HOME, 'McImage')
                vprint('McImage download directory created ({0})'.format(PATH))
        else:
            PATH = os.path.join(HOME, 'McImage')
                             
        if len(args) >=1:
            urls = []
            for arg in args:
                if 'http://' in(arg) or 'https://' in(arg):
                    urls.append(arg)
                else:
                    logging.error('Please enter the full url including the "http:// or https://"')
                    sys.exit(2)
            
        else:
            vprint('''
McImage launched in manual mode, either no arguments were given or the program executable was launched manually.
Manual mode only allows for basic usage of the McImage software. For more information run 'mcimage -h' from command line.''')
            url = input('please enter the url of the site you would like to download images from: ').strip(' ')
            
        
         
            
        
        
        vprint('\nGetting current time')
        time = strftime("%b-%d-%y-%H-%M-%S", gmtime())
        vprint(time)
        vprint('\nSetting save path')
        if loc is None:
            loc = PATH
        else:
            if os.path.isdir(loc):
                pass
            else:
                logging.error('Directory given({0}) is not a directory, changing directory to {1}.'.format(loc, PATH))
                loc = PATH
        if folder is None:
            os.mkdir('{0}/{1}'.format(loc, time))
            folder = '{0}/{1}'.format(loc, time)
        else:
            if not os.path.isdir('{0}'.format(os.path.join(loc, folder))):
                os.mkdir('{0}'.format(os.path.join(loc, folder)))
                if os.path.isdir('{0}'.format(os.path.join(loc, folder))):
                    vprint('Directory set \n{0}'.format(os.path.join(loc, folder)))

        
            
        start = requests.Session()
        
        
        Derrors = 0
        downs = []
        ranonce = False
        savestate = False
        for url in urls:
            urlpre = ['', 'http:', url, 'https:', 'http:/','http://', 'https:/', 'https://']
            again = start.get(url)
            res = requests.get(url, cookies=again.cookies, verify=False)
            soups = bs4.BeautifulSoup(res.text, 'html.parser')
            imgs = soups.select('img[src*="//i.4cdn.org/"]') if shitchan else soups.select('img[src]')
            dirLen = len([name for name in os.listdir(os.path.join(loc, folder)) if os.path.isfile(os.path.join(loc, folder, name)) and filename in name])
            if not ranonce:
                if save is None:
                    pass
                elif save == 'overwrite':
                    vprint('\nSave type is overwrite')
                    dirLen = 0
                elif save.startswith('preserve='):
                    save = save.replace('preserve=', '')
                    savestate = True
                elif save.startswith('erase='):
                    vprint('\nSavetype is erase with keyword {0}'.format(save.replace('erase=', '')))
                    vprint('\nRemoving files')
                    dirpath = os.path.join(loc, folder)

                    for filers in os.listdir(dirpath):
                        if save.replace('erase=', '') in filers:
                            filepath = os.path.join(dirpath, filers)
                            try:
                                shutil.rmtree(filepath)
                            except OSError:
                                os.remove(filepath)
                    vprint('\nFiles removed')
                
                else:
                    logging.error('unexpected value entered for save type, saving with default save values')
                if nuke:
                    vprint('\nSavetype is nuke\ndeleting contents of save path')
                    dirLen = 0
                    dirpath = os.path.join(loc, folder)
                    if savestate:
                        for filers in os.listdir(dirpath):
                            if not save in filers:
                                filepath = os.path.join(dirpath, filers)
                                try:
                                    shutil.rmtree(filepath)
                                except OSError:
                                    os.remove(filepath)
                            else:
                                pass
                    else:
                        for filers in os.listdir(dirpath):
                            filepath = os.path.join(dirpath, filers)
                            try:
                                shutil.rmtree(filepath)
                            except OSError:
                                os.remove(filepath)
                            
                    vprint('\nContents removed')
                
                
                                 
            vprint('\nStarting image retrieval')
            for image in range(len(imgs)):

                urllib.request.urlcleanup()
                try:
                        
                    

                    img = imgs[image].find_previous('a')    
                    for i in range(len(urlpre)+1):
                        if i == 8:
                            logging.error('\nerror downloading '+(imgs[image]['src']).lstrip('.'))
                            
                            for i in range(len(urlpre)+1):
                                if i == 8:
                                    logging.error('\nerror downloading '+(imgs[image]['src']).lstrip('.'))
                                    Derrors+=1
                                
                                else:
                                    try:                           
                                        vprint('\nTrying: '+urlpre[i]+(imgs[image]['src']).lstrip('.'))
                                        opener.retrieve(urlpre[i]+(imgs[image]['src']).lstrip('.'), '{0}{1}.jpg'.format(os.path.join(loc, folder, filename), image+dirLen))
                                        vprint('Retrieved: '+urlpre[i]+imgs[image]['src']+' image saved as {0}{1}.jpg'.format(os.path.join(loc, folder, filename), image+dirLen))
                                        downs.append('{0}{1}.jpg'.format(os.path.join(filename), image+dirLen).strip("'"))
                                        break
                                    except Exception:
                                        pass
                                    
                                    
                            
                        else:
                            try:                                                               
                                vprint('\nTrying: '+urlpre[i]+(imgs[image]['src']).lstrip('.'))
                                opener.retrieve(urlpre[i]+(img['href']).lstrip('.'), '{0}{1}.jpg'.format(os.path.join(loc, folder, filename), image+dirLen))
                                vprint('Retrieved: '+urlpre[i]+imgs[image]['src']+' image saved as {0}{1}.jpg'.format(os.path.join(loc, folder, filename), image+dirLen))
                                downs.append('{0}{1}.jpg'.format(os.path.join(filename), image+dirLen).strip("'"))
                                break
                            except Exception:
                                pass
                
                            
                                
                                
                            
                                

                    
                        
                            
                        
                            
                    
                except Exception as e:
                    Derrors += 1
                    logging.error('{0} \nerror downloading http:'.format(e)+imgs[image]['src'])
                ranonce = True
                
        vprint('\nImage retrieval complete')
        if Derrors:
            vprint('\n{0} image(s) downloaded successfully'.format(len(downs)))
            vprint('{0} image(s) not downloaded'.format(Derrors))
        else:
            vprint('\nAll image(s) downloaded successfully, image(s) retrieved: {0}'.format(len(downs)))
        os.chdir(os.path.join(loc, folder))
        curdir = os.getcwd()
        if archive:
            formatz = 'cbz' if cbz else 'zip'
            print('Creating archive')
            cbznum = 0
            while os.path.isfile(os.path.join(curdir, '{0}{1}.{2}'.format(filename, cbznum, formatz))):
                cbznum +=1               
            with zipfile.ZipFile('{0}{1}.{2}'.format(filename, cbznum, formatz), 'w') as myzip:
                
                for file in os.listdir(curdir):
                    
                    if file in downs:
                        try:
                            myzip.write(file)
                            try:
                                shutil.rmtree(file)
                            except OSError:
                                os.remove(file)
                        except Exception as e:
                            print(e)
                            pass
                        
                    else:
                        pass
                print('Archive created')

    except KeyboardInterrupt:
        vprint('\nCtrl-C')
        vprint('Operation halted')
        sys.exit
    except Exception as e:
        logging.error('{0} \nSomething went wrong!!'.format(e))





if __name__ == "__main__":
    opener = AppURLopener()
    main(opener)

