from PySide2 import QtPrintSupport
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QAction, QDialog, QSplitter, QGridLayout, QLineEdit, QPushButton, QWidget, QMessageBox
from PySide2.QtCore import QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView
#from shiboken2 import *
from subprocess import call, run, PIPE

ADD_WEBENGINE = True

#import tkinter

from pymarkup_fns import read_toml, merge, read_csv, render_html, load_css, get_subitems, render_pdf
'''
from pymarkup_fns import \
    read_csv, read_toml, merge, \
    render_html, render_pdf, \
    load_css, get_subitems, printdic, read_csv_adv, get_images
'''
from QCodeEditor import QCodeEditor

import toml
print('Toml OK')

from simpleeval import simple_eval
print('Eval OK')

import markdown2
print('Markdown2 OK')

import jinja2
print('Jinja2 OK')

#import xhtml2pdf
#print('Xhtml OK')

#from PyQt5 import QtWebEngineWidgets
print('PyQtWebEngine OK')

import sys
import os
import json




class Browser(QWebEngineView):

    def __init__(self, mw):
        super().__init__()

        # With QWebEnginePage.setHtml, the html is loaded immediately.
        # baseUrl is used to resolve relative URLs in the document.
        # For whatever reason, it seems like the baseUrl resolves to
        # the parent of the path, not the baseUrl itself.  As a
        # workaround, either append a dummy directory to the base url
        # or start all relative paths in the html with the current
        # directory.
        # https://doc-snapshots.qt.io/qtforpython-5.15/PySide2/QtWebEngineWidgets/QWebEnginePage.html#PySide2.QtWebEngineWidgets.PySide2.QtWebEngineWidgets.QWebEnginePage.setHtml
        
    def SetHTML(self,html):
        here = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
        base_path = os.path.join(os.path.dirname(here), 'dummy').replace('\\', '/')
        self.url = QtCore.QUrl('file:///' + base_path)
        self.page().setHtml(html, baseUrl=self.url)



class SettingsDialog(QDialog):
    def __init__(self,mw):
        super().__init__()

        self.mw = mw
        # self.setWindowIcon(mw.icon)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('Impostazioni')

        self.setup_layout()


    def FilePicker(self,key,filetypes='*.csv'):
        print('FilePicker',key)
        chosen_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Seleziona file', '', filetypes)
        # print(type(chosen_path),chosen_path)
        if chosen_path[0] != '':
            self.widgets[key].setText(chosen_path[0])
            self.mw.settings['paths'][key] = chosen_path[0]


    def FolderPicker(self,key):
        chosen_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Seleziona cartella')
        print(type(chosen_path),chosen_path)
        if chosen_path != '':
            self.widgets[key].setText(chosen_path)
            self.mw.settings['paths'][key] = chosen_path


    def setup_widgets(self):
        pass


    def setup_layout(self):

        self.widgets = {
            'table_products':   QLineEdit(),
            'table_macros':     QLineEdit(),
            'img_folder':       QLineEdit(), # QPlainTextEdit()
            'template_html':    QLineEdit(),
            'template_css':     QLineEdit(),
            'renderpdf':        QLineEdit(),
            'sysfolder':        QLineEdit(),
            'python':           QLineEdit(),
        }

        widget_labels = {
            'table_products':   "Tabella prodotti",
            'table_macros':     "Tabella note",
            'img_folder':       "Cartella immagini",
            'template_html':    "HTML per anteprima",
            'template_css':     "CSS per anteprima",
            'renderpdf':        "renderpdf.app",
            'sysfolder':        "Cartella di sistema",
            'python':           "Python3 full path",
        }

        widget_button_slots = {
            'table_products':   lambda: self.FilePicker('table_products'),
            'table_macros':     lambda: self.FilePicker('table_macros'),
            'img_folder':       lambda: self.FolderPicker('img_folder'),
            'template_html':    lambda: self.FilePicker('template_html','*.html'),
            'template_css':     lambda: self.FilePicker('template_css','*.css'),
            'renderpdf':        lambda: self.FilePicker('renderpdf','*.app'),
            'sysfolder':        lambda: self.FolderPicker('sysfolder'),
            'python':           lambda: self.FilePicker('python','*'),
        }

        #editable_fields = ['python']

        grid_layout = QGridLayout()

        for i,key in enumerate(self.widgets.keys()):
            label = QLabel(widget_labels[key])
            widget = self.widgets[key]
            #if key not in editable_fields:
            widget.setReadOnly(True)
            widget.setDisabled(True)
            button = QPushButton('Seleziona')
            button.pressed.connect(widget_button_slots[key])

            last_used_path = self.mw.settings['paths'].get(key,'')
            if os.path.exists(last_used_path):
                widget.setText(last_used_path)

            grid_layout.addWidget(label,i,0,1,1)
            grid_layout.addWidget(widget,i,1,1,1)
            grid_layout.addWidget(button,i,2,1,1)

        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(grid_widget)
        main_layout.addStretch()
        self.setLayout(main_layout)

        # settings_wh = self.mw.settings.get('settings_wh')
        # if settings_wh is not None:
        geometry = self.mw.settings.get('geometry_wh')
        if geometry:

            x,y,w,h = geometry
            # w,h = settings_wh
            # Position dialog at the center of the main window
            # g = self.mw.geometry()
            # x = g.x() + (g.width()-w) / 2
            # y = g.y() + (g.height()-h) / 2

            # self.setGeometry(x,y,w,h)
        else:
            self.resize(500,500)




class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, appctxt=None):
        super().__init__()
        
        self.appcontext = appctxt
        self.BASE_TITLE = 'PyMarkup'
        self.REFRESH_DELAY_MS = 200
        self.modified = False
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.setInterval(self.REFRESH_DELAY_MS)
        self.refresh_timer.timeout.connect(self.Refresh)

        self.settings = self.LoadSettings()
        
        self.init_widgets()
        self.init_layout()
        self.init_mainmenu()

        self.python_path = None
        
        try:
            self.css = load_css(self.settings['paths']['css'])
        except KeyError:
            self.css = ''

        self.LoadResources()

        print('Singles:',len(self.singles.keys()))
        # self.singles = {}
        
        # print('Macros:',len(self.macros.keys()))
        self.macros = {}

        # print('Images:',len(self.images.keys()))
        self.images = {}

        self.subitems = {}

        try: self.LoadFileFromPath(self.settings['paths']['lastopened'])
        except KeyError: pass

        self.Refresh()


    # Load two tables and images
    def LoadResources(self):
        self.singles = read_csv(self.settings['paths'].get('table_products',None))
        return
        self.subitems = get_subitems(self.singles)
        self.macros = read_csv_adv(self.settings['paths'].get('table_macros',None))
        self.images = get_images(self.settings['paths'].get('img_folder',None))
        self.ConsoleLog('Database aggiornato.')

    
    def ScheduleRefresh(self):
        # print('Refresh timer started for 100 ms')
        self.modified = True
        self.UpdateTitle()
        self.refresh_timer.start()


    def init_widgets(self):

        if ADD_WEBENGINE:
            self.browser = Browser(self)
            # self.browser.setZoomFactor(1.5) # Valid values: 0.25 to 5.0
            self.browser.setZoomFactor(self.settings['browserzoomfactor'])

        # self.texteditor = QtWidgets.QPlainTextEdit()
        self.texteditor = QCodeEditor()
        self.texteditor.setPlainText('cliente = "Asd"')
        # self.texteditor.setPlainText(self.settings['texteditor'])
        self.texteditor.zoomIn(self.settings['zoom_texteditor'])
        self.texteditor.textChanged.connect(self.ScheduleRefresh)

        self.console = QtWidgets.QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.zoomIn(self.settings['zoom_console'])


    def init_mainmenu(self):
        menubar = self.menuBar()
        # filemenu = menubar.addMenu('File')
        # viewmenu = menubar.addMenu('Visualizza')
        
        menus = {
            'File': [
                ['Nuovo file', 'Ctrl+N', self.NewFile],
                ['Apri...', 'Ctrl+O', self.ChooseFile],
                ['Salva', 'Ctrl+S', self.Save],
                ['Salva con nome...', 'Ctrl+Shift+S', self.SaveAs],
                [],
                ['Esporta PDF (preventivo)', 'Ctrl+E', self.RenderPDF_estimate],
                ['Esporta PDF (proforma)', 'Ctrl+T', self.RenderPDF_proforma],
                [],
                ['Aggiorna anteprima', 'Ctrl+R', self.Refresh],
                ['Aggiorna database', 'Ctrl+L',     self.LoadResources],
                ['Impostazioni...', 'Ctrl+I',          self.OpenSettingsDialog],
                # ['Print pwd', 'Ctrl+P',          self.PrintPwd],
                ['Subprocess', None, self.RunSubprocess],
                [],
                ['Chiudi', 'Ctrl+Shift+Q',          self.close],
            ],
            'Visualizza': [
                ['Ingrandisci editor',None,self.ZoomInEditor],
                ['Riduci editor',None,self.ZoomOutEditor],
                [],
                ['Ingrandisci anteprima',None,self.ZoomInBrowser],
                ['Riduci anteprima',None,self.ZoomOutBrowser],
            ]
        }

        for menu_name,entries in menus.items():
            menu = menubar.addMenu(menu_name)
            for data in entries:
                if len(data)>0:
                    label,shortcut,function = data
                    # label,shortcut,function = item
                    new_action = QAction(label,self)
                    if shortcut:
                        new_action.setShortcut(shortcut)
                    new_action.triggered.connect(function)
                    menu.addAction(new_action)
                else:
                    menu.addSeparator()


    def PrintPwd(self):
        path = os.path.abspath('./')
        self.ConsoleLog(path)


    def ZoomInEditor(self):
        self.texteditor.zoomIn()

    def ZoomOutEditor(self):
        self.texteditor.zoomOut()

    def ZoomInBrowser(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() + 0.1)

    def ZoomOutBrowser(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() - 0.1)


    def Dummy(self):
        return


    def GetPythonPath(self):
        cmd = 'which python3'
        response = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        return response.stdout.decode('utf-8')


    def RunSubprocess(self):

        self.ConsoleLog(self.GetPythonPath())

        return

        cmd1 = '/Users/pc/Dev/pymarkup_installer_redux/local/sys_folder/xhtml2pdf.command'
        cmd2 = 'pwd > /Users/pc/Dev/pymarkup_installer_redux/local/sys_folder/pwd.txt'
        cmd = 'which python3'

        response = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        #self.ConsoleLog(str(response))

        log = [cmd, response.returncode, response.stdout.decode('utf-8'), response.stderr]
        #log = [cmd, response]
        self.ConsoleLog('\n'.join([str(x) for x in log]))
        '''
        process = os.popen("which python")
        result = process.read()
        print(result)
        self.ConsoleLog(result)
        '''


    def ConfirmClose(self):
        # print('ConfirmClose')
        if self.modified:
            dialog = QMessageBox()
            # dialog.setIcon(QMessageBox.Question)
            dialog.setWindowTitle('Modifiche non salvate')
            dialog.setInformativeText(u"Abbandonare le modifiche in corso?")
            dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            choice = dialog.exec_()
            return choice == QMessageBox.Ok
        return True


    def ChooseFile(self):
        if self.ConfirmClose():
            chosen_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Apri file', '', '*.toml',)
            if chosen_path[0] != '':
                self.settings['paths']['lastopened'] = chosen_path[0]
                self.LoadFileFromPath(chosen_path[0])
                self.modified = False
                self.UpdateTitle()


    def LoadFileFromPath(self,path):
        if os.path.exists(path):
            with open(path, 'r+') as file:
                self.texteditor.setPlainText(file.read())
            self.modified = False
            self.UpdateTitle()


    def NewFile(self):
        if self.ConfirmClose():
            self.modified = False
            self.settings['paths']['lastopened'] = ''
            self.setWindowTitle(self.BASE_TITLE+' - senza titolo')
            self.texteditor.setPlainText('')
            self.Refresh()
            self.DisplayHTML('')
            self.ConsoleLog('Nuovo file creato.')


    def Save(self):
        path = self.settings['paths']['lastopened']
        if os.path.exists(path):
            try:
                with open(path,'w+') as file:
                    file.write(self.texteditor.toPlainText())
                self.ConsoleLog('File salvato:\n'+path)
                self.modified = False
                self.UpdateTitle()
            except Exception as e:
                self.ConsoleLog(e)


    def SaveAs(self):

        path,_ = QtWidgets.QFileDialog().getSaveFileName(self, "Salva file", '', "Toml (*.toml)")
        if path != '':
            try:
                with open(path,'w+') as file:
                    file.write(self.texteditor.toPlainText())
                self.settings['paths']['lastopened'] = path
                self.modified = False
                self.ConsoleLog('File salvato:\n'+path)
                self.UpdateTitle()

            except Exception as e:
                print(str(e))
                self.ConsoleLog(str(e))


    def UpdateTitle(self):
        path = self.settings['paths']['lastopened']
        new_title = '{} - {}'.format(self.BASE_TITLE,path)
        if self.modified:
            new_title += ' (modificato)'
        self.setWindowTitle(new_title)


    def init_layout(self):
        self.setWindowTitle(self.BASE_TITLE)

        '''
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.texteditor)
        left_layout.addWidget(self.console)
        left_layout_widget = QtWidgets.QWidget()
        left_layout_widget.setLayout(left_layout)
        '''
        
        self.layout_left_splitter = QSplitter()
        self.layout_left_splitter.setOrientation(QtCore.Qt.Vertical)
        self.layout_left_splitter.addWidget(self.texteditor)
        self.layout_left_splitter.addWidget(self.console)

        self.layout_panes = QSplitter()
        self.layout_panes.addWidget(self.layout_left_splitter)

        if ADD_WEBENGINE:
            self.layout_panes.addWidget(self.browser)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.layout_panes)

        # Set size for left splitter
        for settings_key,splitter in [
            ['left_splitter_sizes', self.layout_left_splitter],
            ['splitter_sizes',      self.layout_panes],
        ]:
            splitter_size = self.settings.get(settings_key)
            if splitter_size is not None:
                splitter.setSizes(splitter_size)

        # Set size for main splitter
        # splitter_sizes = self.settings.get('splitter_sizes')
        # if splitter_sizes is not None:
        #     self.layout_panes.setSizes(splitter_sizes)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.setGeometry(*self.settings['geometry'])


    def RenderHTML(self, **kwargs):
        
        toml_text = self.texteditor.toPlainText()
        toml_model = read_toml(toml_text, css=self.css)
        order_model = merge(toml_model, self.singles, self.subitems, self.macros, self.images)
        print('TOML merge OK')
        
        template_path = 'template.html'
        print('Template path:',template_path)
        path_html = self.settings['paths']['template_html']
        path_css  = self.settings['paths']['template_css']
        return render_html(order_model, path_html=path_html, path_css=path_css, **kwargs)


    def RenderPDF(self, **kwargs):

        folder,filename = os.path.split(self.settings['paths']['lastopened'])
        name,_ = os.path.splitext(filename)
        defaultpath = os.path.join(folder,name+'.pdf')
        print('Last opened folder/filename:',folder)

        savepath,_ = QtWidgets.QFileDialog().getSaveFileName(self, "Salva PDF", defaultpath, "PDF (*.pdf)")
        if savepath == '':
            return
        
        path_sys = self.settings['paths']['sysfolder']
        html = self.RenderHTML(**kwargs)

        # Save 'tmp.html'
        htmlpath = os.path.join(path_sys,'tmp.html')
        '''
        # TEMPORARILY DISABLED FOR DEBUGGING
        with open(htmlpath, 'w+', encoding='UTF-8') as file:
            file.write(html)
        '''

        sys_folder = self.settings['paths']['sysfolder']
        #path_script = os.path.join(self.settings['paths']['renderpdf'], 'Contents/MacOS/renderpdf')
        path_script = os.path.join(sys_folder, 'renderpdf.py')
        #self.ConsoleLog(html)

        print('-----')
        print('RenderPDF paths:')
        print(path_script, os.path.exists(path_script))
        print(htmlpath, os.path.exists(htmlpath))
        print(savepath)
        print('-----')

        #render_pdf(path_script,htmlpath,savepath)
        #python_path = '/Library/Frameworks/Python.framework/Versions/3.6/bin/python3'

        python_path = self.settings['paths']['python']
        command = f'{python_path} "{path_script}" --args "{savepath}"'
        
        #command = f'xhtml2pdf {htmlpath} {savepath}'

        '''
        cmd_lines = [
            'from xhtml2pdf import pisa',
            f'resultFile = open("{savepath}", "w+b")',
            f'htmlFile = open("{htmlpath}","r+")',
            f'pisa.CreatePDF(htmlFile.read(),dest=resultFile)',
            'resultFile.close()',
            'htmlFile.close()',
        ]
        command = "python3 -c '" + ';'.join(cmd_lines) + "'"
        '''

        #command = f'python3 "{path_script}" "{savepath}"'

        # Path to renderpdf.command (as a proxy to execute renderpdf.py)
        #command = os.path.join(sys_folder, 'xhtml2pdf.command')

        print('Calling command:')
        print(command)
        print('-----')
        try:
            #result = call(command,shell=True) # shell=True is needed because subprocess.call is just a wrapper for Popen
            result = call(command, shell=True)
            self.ConsoleLog(command)
            #self.ConsoleLog('Xhtml2 call result: '+str(result))
            #self.ConsoleLog('PDF salvato: '+savepath)
        except FileNotFoundError as e:
            print('Subprocess.call raised an exception:')
            print(e)
            self.ConsoleLog(str(e))
        except Exception as e:
            self.ConsoleLog(str(e))
            with open(os.path.join(sys_folder,'applog.txt'),'r+') as file:
                file.write(str(e))

        # os.startfile('rendered.pdf')


    def RenderPDF_estimate(self):
        self.RenderPDF(preview=False,render_estimate=True)

        
    def RenderPDF_proforma(self):
        self.RenderPDF(preview=False,render_proforma=True)


    def DisplayHTML(self, html):
        print('Display HTML')
        self.browser.SetHTML(html)


    def Refresh(self):
        # print('Refresh')
        try:
            html = self.RenderHTML(preview=True, render_estimate=True)
            self.DisplayHTML(html)
            self.ConsoleLog('OK')
            # self.ConsoleLog('Render HTML OK. Html length: {}\n{}'.format(len(html),html))
        except Exception as e:
            print(e)
            self.ConsoleLog(str(e))


    def ConsoleLog(self,msg):
        self.console.setPlainText(msg)


    def LoadSettings(self):
        default_settings = {
            'geometry': [500,300,1400,1000],
            # 'texteditor': '',
            'splitter_sizes': None,
            'left_splitter_sizes': None,
            'browserzoomfactor': 1,
            'paths': {
                'lastopened': '',
                'python': '/Library/Frameworks/Python.framework/Versions/3.6/bin/python3',
            },
            'zoom_texteditor': 2,
            'zoom_console': 2,
        }

        qsettings = QtCore.QSettings('Company','Appname')
        jsontext = qsettings.value('settings',None)
        # print('Json settings from QSettings:',jsontext)

        settings = json.loads(jsontext) if jsontext else {}
        for key in default_settings.keys():
            if key in settings:
                default_settings[key] = settings[key]

        # Check all paths and delete them if they are broken
        for key,path in default_settings['paths'].items():
            if not os.path.exists(path):
                default_settings['paths'][key] = ''

        return default_settings


    def SaveSettings(self):
        print('Saving settings')
        
        g = self.geometry()
        self.settings['geometry'] = [g.x(), g.y() ,g.width(), g.height()]
        # self.settings['texteditor'] = self.texteditor.toPlainText()
        self.settings['splitter_sizes'] = self.layout_panes.sizes()
        self.settings['left_splitter_sizes'] = self.layout_left_splitter.sizes()
        self.settings['browserzoomfactor'] = self.browser.zoomFactor()

        qsettings = QtCore.QSettings('Company','Appname')
        qsettings.setValue('settings', json.dumps(self.settings))


    def OpenSettingsDialog(self):
        dialog = SettingsDialog(self)
        dialog.exec_()


    def closeEvent(self,event):
        print('closeEvent')
        if self.ConfirmClose():
            event.ignore()
            self.SaveSettings()
            print('Closing program (settings saved)')
            event.accept()
        else:
            event.ignore()


    '''
    def load_finished(self, status):
        self.msg = QtWidgets.QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setWindowTitle('Load Status')
        self.msg.setText(f"It is {str(status)} that the page loaded.")
        self.msg.show()
    '''
    


def main_pymarkup():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    # window.resize(700, 500)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main_pymarkup()