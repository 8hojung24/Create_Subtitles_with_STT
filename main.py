from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPalette
from PyQt5.uic import loadUi
from media import CMultiMedia
import ffmpeg
import sys
import os
import datetime
import wavtosrt
from time import sleep
# import cleanwav
# from google.cloud import translate


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
 
class CWidget(QWidget):

    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)
 
        # Multimedia Object
        self.mp = CMultiMedia(self, self.view)
      
        # video background color
        pal = QPalette()        
        pal.setColor(QPalette.Background, Qt.black)
        self.view.setAutoFillBackground(True)
        self.view.setPalette(pal)
         
        # volume, slider
        self.vol.setRange(0,100)
        self.vol.setValue(50)
 
        # play time
        self.duration = ''
        self.filename=''
        self.wavname=''
        self.srtname=''
 
        # sfignal
        self.btn_add.clicked.connect(self.clickAdd)
        self.btn_add2.clicked.connect(self.clickAdd2)
        self.btn_del.clicked.connect(self.clickDel)
        self.btn_del2.clicked.connect(self.clickDel2)
        self.btn_play.clicked.connect(self.clickPlay)
        self.btn_stop.clicked.connect(self.clickStop)
        self.btn_pause.clicked.connect(self.clickPause)
        self.btn_forward.clicked.connect(self.clickForward)
        self.btn_prev.clicked.connect(self.clickPrev)
 
        self.list.itemDoubleClicked.connect(self.dbClickList)
        self.list_2.itemDoubleClicked.connect(self.dbClickList2)
        self.vol.valueChanged.connect(self.volumeChanged)
        self.bar.sliderMoved.connect(self.barChanged)       
        

        self.btn_ExtractVoices.clicked.connect(self.extractvoices)
        self.btn_ExtractSubtitles.clicked.connect(self.extractsubtitles)
        self.btn_MergeSRT.clicked.connect(self.mergesrt)
        self.btn_ModifySubtitles.clicked.connect(self.modifysubtitles)
        self.btn_translate.clicked.connect(self.translate)


 
    def clickAdd(self):
        files, ext = QFileDialog.getOpenFileNames(self
                                             , 'Select one or more files to open'
                                             , ''
                                             , 'Video (*.mp4 *.mpg *.mpeg *.avi *.wma)') 
         
        if files:
            cnt = len(files)       
            row = self.list.count()
            self.filename=''        
            for i in range(row, row+cnt):
                self.list.addItem(files[i-row])
                self.filename+=files[i-row]
            self.list.setCurrentRow(0)
 
            self.mp.addMedia(files)

    def clickAdd2(self):
        files, ext = QFileDialog.getOpenFileNames(self
                                             , 'Select one or more files to open'
                                             , ''
                                             , 'Subtitles (*.srt)') 
         
        if files:
            cnt = len(files)       
            row = self.list_2.count()
            self.srtname=''        
            for i in range(row, row+cnt):
                self.list_2.addItem(files[i-row])
                self.srtname+=files[i-row]
            self.list_2.setCurrentRow(0)
            
            self.mp.addMedia2(files)
 


    def clickDel(self):
        row = self.list.currentRow()
        self.list.takeItem(row)
        self.mp.delMedia(row)

    def clickDel2(self):
        row = self.list_2.currentRow()
        self.list_2.takeItem(row)
        self.mp.delMedia2(row)
 
    def clickPlay(self):
        index = self.list.currentRow()        
        self.mp.playMedia(index)
        print(self.filename)
        print(index)
 
    def clickStop(self):
        self.mp.stopMedia()
 
    def clickPause(self):
        self.mp.pauseMedia()
 
    def clickForward(self):
        cnt = self.list.count()
        curr = self.list.currentRow()
        if curr<cnt-1:
            self.list.setCurrentRow(curr+1)
            self.mp.forwardMedia()
        else:
            self.list.setCurrentRow(0)
            self.mp.forwardMedia(end=True)
 
    def clickPrev(self):
        cnt = self.list.count()
        curr = self.list.currentRow()
        if curr==0:
            self.list.setCurrentRow(cnt-1)    
            self.mp.prevMedia(begin=True)
        else:
            self.list.setCurrentRow(curr-1)    
            self.mp.prevMedia()
 
    def dbClickList(self, item):
        row = self.list.row(item)
        self.mp.playMedia(row)
    
    def dbClickList2(self, item):
        row = self.list_2.row(item)
        return row
 
    def volumeChanged(self, vol):
        self.mp.volumeMedia(vol)
 
    def barChanged(self, pos):   
        print(pos)
        self.mp.posMoveMedia(pos)    
 
    def updateState(self, msg):
        self.state.setText(msg)
 
    def updateBar(self, duration):
        self.bar.setRange(0,duration)    
        self.bar.setSingleStep(int(duration/10))
        self.bar.setPageStep(int(duration/10))
        self.bar.setTickInterval(int(duration/10))
        td = datetime.timedelta(milliseconds=duration)        
        stime = str(td)
        idx = stime.rfind('.')
        self.duration = stime[:idx]

    def updatePos(self, pos):
        self.bar.setValue(pos)
        td = datetime.timedelta(milliseconds=pos)
        stime = str(td)
        idx = stime.rfind('.')
        stime = f'{stime[:idx]} / {self.duration}'
        self.playtime.setText(stime)

    def extractvoices(self):
        if(self.list.currentRow()<0):
            QMessageBox.warning(self,'Warning','영상파일을 추가하세요.')
            self.clickAdd()
        if(self.list.currentRow()>=0):
            stream = ffmpeg.input("%s" %(self.filename))
            sf = (self.filename).rstrip(".mp4")
            self.wavname=sf+'.wav'
            stream = ffmpeg.output(stream, '%s.wav'%(sf), ac='1', ar='16000', format='wav')
            ffmpeg.run(stream)

    
    def extractsubtitles(self):
        if self.list.currentRow()<0:
            QMessageBox.warning(self,'Warning','영상파일을 추가하세요.')
            self.clickAdd()

        if(self.list.currentRow()>=0):
            stream = ffmpeg.input("%s" %(self.filename))
            sf = (self.filename).rstrip(".mp4")

            if(os.path.isfile(sf+'.wav')):
                if self.wavname=='':
                    self.wavname=sf+'.wav'
            else:
                self.extractvoices()
            
            wavtosrt.main(self.wavname)
            
            self.srtname='{}.srt'.format(self.wavname.rstrip('.wav'))
            self.list_2.addItem(self.srtname)
                  
    
    def mergesrt(self):
        if(self.list.currentRow()<0):
            QMessageBox.warning(self,'Warning','영상파일을 추가하세요.')
            self.clickAdd()
        if(self.list_2.currentRow()<0):
            reply = QMessageBox.question(self,'Message', 'srt파일을 추출하겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.extractvoices()
                self.extractsubtitles()
                self.list_2.setCurrentRow(0)
                self.mp.addMedia2(self.srtname)
                
            else:
                QMessageBox.warning(self,'Warning','srt파일을 추가하세요.')
                self.clickAdd2()
        
        if(self.list.currentRow()>=0 &self.list_2.currentRow()>=0):
            self.filename=self.list.currentItem().text()
            self.srtname=self.list_2.currentItem().text()
            self.srtname=self.srtname.replace(':','\\\\:')
            self.srtname=self.srtname.replace("/","\\\\\\\\")

            fn='output' #파일명 고정값
            file_ext='.mp4' #파일 형식
            outpath="C:/Users/8hoju/OneDrive/바탕 화면/College/인터루드/23.01 영상자막/영상example/%s%s" %(fn,file_ext)
            uniq=1
            while os.path.exists(outpath):  #동일한 파일명이 존재할 때
                outpath='C:/Users/8hoju/OneDrive/바탕 화면/College/인터루드/23.01 영상자막/영상example/%s(%d) %s' % (fn,uniq,file_ext) #파일명(1) 파일명(2)...
                uniq+=1
            os.system(f'ffmpeg -i "{self.filename}" -vf subtitles="{self.srtname}" "{outpath}"')

            print(outpath+"로 Merge 되었습니다.")
            sleep(1)
            self.mp.addMedia(outpath)
            # self.clickPlay()


    def modifysubtitles(self):
        if self.list.currentRow()<0:
            print("선택된 srt파일이 없습니다.")
            self.clickAdd2()
        else:
            self.clickDel2()
            self.clickAdd2()

    def translate(self):
        if(self.list_2.currentRow()<0):
            QMessageBox.warning(self,'Warning','srt파일을 추가하세요.')
            self.clickAdd2()
        
        if(self.list_2.currentRow()>=0):
            import translate_txt
            #srt파일은 안돌아감 일단 srt파일명을 인자로 주고 안에서 txt로 바꿔주기
            if self.comboBox.currentText()=="Korean":
                translate_txt.main(self.srtname,"ko") 
            elif self.comboBox.currentText()=="English":
                translate_txt.main(self.srtname,"en")
            elif self.comboBox.currentText()=="Janpanese":
                translate_txt.main(self.srtname,"ja")
            elif(self.comboBox.currentText()=="Chinese"):
                translate_txt.main(self.srtname,"zh-CN")
            elif(self.comboBox.currentText()=="Spanish"):
                translate_txt.main(self.srtname,"es")
            else:
                translate_txt.main(self.srtname,"ar")

            import txt2srt
            txt2srt.main(self.srtname)
            self.list_2.addItem(txt2srt.newsrtname)
            self.srtname=txt2srt.newsrtname
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    w.show()
    sys.exit(app.exec_())