import os
import sys
from xhtml2pdf import pisa

def convertHtmlToPdf(sourceHtml, savepath):
    print('XHTML2PDF converting html')
    #print(savepath)
    #print(sourceHtml)
    try:
        with open(savepath, "w+b") as resultFile:
            pisaStatus = pisa.CreatePDF(sourceHtml, dest=resultFile, show_error_as_pdf=True)
            #for name in dir(pisaStatus):
            #    print(type(getattr(pisaStatus,name)),'\t',name)
            return pisaStatus.err # return True on success and False on errors
    except FileNotFoundError as e:
        print('Xhtml2pdf raise an error while creating pdf:')
        print(e)


def main():
    log = 'All arguments: '+', '.join(sys.argv)+'\n'

    args = [arg for arg in sys.argv if not arg.startswith('-')][1:]

    log += 'Filtered arguments: '+', '.join(args)+'\n'
    
    default_folder = '/Users/pc/Dev/pymarkup_installer_redux/local/sys_folder/'
    
    try:
        path_input = default_folder+'tmp.html'
        path_output = default_folder+'tmp_out.pdf'
        if len(args)==1:
            path_output = args[0]
        elif len(args) > 1:
            path_input = args[0]
            path_output = args[1]

        print('path_input:',path_input)
        print('path_output:',path_output)
        html = open(path_input,'r+',encoding='UTF-8').read()
        print('HTML length:',len(html))
        convertHtmlToPdf(html,path_output)
        log += 'Conversion OK. Args: '+','.join(args)+'\nPath output: '+path_output

    except Exception as e:
        print(e)
        log += str(e)

    '''
    except IndexError:
        print('Error: not enough arguments:',args)
        log = 'Not enough arguments: '+','.join(args)

    except FileNotFoundError:
        print('Error: filenotfound:',args)
        log = 'File not found: '+','.join(args)
    '''

    with open(default_folder+'renderpdflog.txt','w+') as file:
        file.write(log)

    return 0
    

if __name__ == '__main__':
    main()
    
