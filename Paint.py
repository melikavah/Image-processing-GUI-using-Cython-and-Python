#######################################################
################ Paint Project  100 % #################
############# Fatemeh Khormizi 9223030 ################
############### Melika Vahdat 9223085 #################
#######################################################
from PyQt5.QtCore import QDir, QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from Image_processing import *
from PIL import Image
from pylab import *
from PyQt5 import QtGui, QtCore, QtWidgets
from copy import copy
from PyQt5.QtGui import *
import cProfile 
import pstats


#####################################################################
########## Function used for converting an array to QImage ##########
#####################################################################
def toQImage(im, copy=False):
    if im is None:
        return QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 2:
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim.copy() if copy else qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                return qim.copy() if copy else qim
            elif im.shape[2] == 4:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                return qim.copy() if copy else qim

    raise NotImplementedException


##############################################################
###################### PaintArea Class #######################
##############################################################

class PaintArea(QtWidgets.QLabel, QGraphicsView):
    def __init__(self, parent=None):
        super(PaintArea, self).__init__(parent)
        QWidget.__init__(self, parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.painting = False
        self.cropping = False
        self.rectangling = False
        self.ellipsing = False
        self.modified = False
        self.myPenWidth = 1
        self.myPenColor = Qt.blue
        self.image = QImage()
        self.lastPoint = QPoint()
        self.qle = QLineEdit(self)
        self.qle.hide()
        
############################################################
### Four below functions are used for "Type Text" option ###
############################################################

    def type_text(self):
        self.qle.setText("")
        self.Type_Text()

    def Type_Text(self):
        self.qle.show()
        self.qle.setGeometry(0, 0, 2000, 100)
        palette = QtGui.QPalette()
        self.color = QColorDialog.getColor(Qt.blue)
        palette.setColor(QtGui.QPalette.Text, self.color)
        self.font = QtGui.QFont("Times", 30, QtGui.QFont.Bold)
        self.qle.setPalette(palette)
        self.qle.setFont(self.font)

    def end_text(self):
        text = self.qle.text()
        self.qle.hide()
        self.onChanged(text)  


    def onChanged(self, text):
        painter = QPainter(self.image)
        painter.setFont(self.font)
        painter.setPen(self.color)
        painter.drawText(self.lastPoint, text)
        self.modified = True
        self.update()       
############################################################        

    def openImage(self, fileName):
        loadedImage = QImage()
        if not loadedImage.load(fileName):
            return False

        newSize = loadedImage.size().expandedTo(self.size())
        self.resizeImage(loadedImage, newSize)
        self.image = loadedImage
        self.modified = False
        self.update()
        return True

#############################################################
################# Colorful Effect function ##################
#############################################################

    def eff_img(self, fileName):
        loadedImage = array(Image.open(fileName))
        loadedImage = effect(loadedImage)
        loadedImage = toQImage(loadedImage)
        newSize = loadedImage.size().expandedTo(self.size())
        self.resizeImage(loadedImage, newSize)
        self.image = loadedImage
        self.modified = True
        self.update()
        return True

#############################################################
################## Black & White Function ###################
#############################################################

    def black_white_img(self, fileName):
        loadedImage = array(Image.open(fileName))
        loadedImage = black_white(loadedImage)
        loadedImage = toQImage(loadedImage)
        newSize = loadedImage.size().expandedTo(self.size())
        self.resizeImage(loadedImage, newSize)
        self.image = loadedImage
        self.modified = True
        self.update()
        return True

############################################################
##################### Picaso Effect ########################
############################################################

    def Picaso(self):
        newImage = QImage(self.image.size(), QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.translate(0, -500)
        painter.rotate(30)
        painter.drawImage(QPoint(0, 0), self.image)
        self.image = newImage
        painter.drawImage(QPoint(500, 500), self.image)
        self.modified = True
        self.update()

############################################################
#################### Rotation function #####################
############################################################

    def Rotate(self):
        newImage = QImage(self.image.size(), QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.rotate(90)
        painter.translate(0, -self.image.size().height())
        painter.drawImage(QPoint(0, 0), self.image)
        self.image = newImage
        self.modified = True
        self.update()

############################################################        
###################  Cropping Function #####################
############################################################

    def crop_img(self, fileName, event):
        self.cropping = True
        self.setPixmap(QtGui.QPixmap(fileName))

    def Cancel_Crop(self):
        self.cropping = False

############################################################
################### Erasing Function #######################
############################################################

    def erase_img(self):
        self.myPenColor = Qt.white
        endPoint = self.lastPoint
        self.drawLineTo(endPoint)
        self.modified = True
        self.update()

############################################################        

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

############################################################

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

############################################################

    def clearImage(self):
        self.image.fill(qRgb(255, 255, 255))
        self.modified = True
        self.update()

############################################################

    def paintEvent(self, event):
        painter = QPainter(self)
        dirtyRect = event.rect()
        painter.drawImage(dirtyRect, self.image, dirtyRect)

#############################################################    

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width() + 128, self.image.width())
            newHeight = max(self.height() + 128, self.image.height())
            self.resizeImage(self.image, QSize(newWidth, newHeight))
            self.update()

        super(PaintArea, self).resizeEvent(event)

############################################################
############# Function used for drawing line ###############
############################################################

    def drawLineTo(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine,
                            Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)

############################################################
################## Drawing Rectangle #######################
############################################################

    def draw_Rect(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine,
                            Qt.RoundCap, Qt.RoundJoin))
        x1 = self.lastPoint.x()
        y1 = self.lastPoint.y()
        x2 = endPoint.x()
        y2 = endPoint.y()
        width = x2 - x1
        height = y2 - y1
        painter.drawRect(x1, y1, width, height)
        self.modified = True
        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)
        self.modified = True

    def rect_draw(self):
        self.rectangling = True        

############################################################
##################### Drawing Ellipse ######################
############################################################

    def draw_Ellipse(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine,
                            Qt.RoundCap, Qt.RoundJoin))
        x1 = self.lastPoint.x()
        y1 = self.lastPoint.y()
        x2 = endPoint.x()
        y2 = endPoint.y()
        width = x2 - x1
        height = y2 - y1
        painter.drawEllipse(x1, y1, width, height)
        self.modified = True
        rad = self.myPenWidth / 2 + 2
        self.update(QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QPoint(endPoint)
        self.modified = True

    def ellipse_draw(self):
        self.ellipsing = True

############################################################
######### canceling drawing rectangle and ellipse ##########
############################################################        

    def Cancel_Shape(self):
        self.rectangling = False
        self.ellipsing = False        

############################################################
################ Rotating image 180 degree #################
############################################################

    def Mirror(self):
        self.image = self.image.mirrored()
        self.update()

############################################################

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QImage(newSize, QImage.Format_RGB32)
        newImage.fill(qRgb(255, 255, 255))
        painter = QPainter(newImage)
        painter.drawImage(QPoint(0, 0), image)
        self.image = newImage

############################################################
###################### Print Function ######################
############################################################       

    def print_(self):
        printer = QPrinter(QPrinter.HighResolution)
        printDialog = QPrintDialog(printer, self)
        if printDialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

############################################################
################ Copy and Paste functions ##################
############################################################

    def Copy(self):
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.setImage(self.image)  

    def Paste(self):
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.image =  self.clipboard.image()
        self.update()
        self.modified = True

############################################################

    def isModified(self):
        return self.modified

############################################################        

    def penColor(self):
        return self.myPenColor

############################################################

    def penWidth(self):
        return self.myPenWidth

############################################################
########## Three functions for mouse movements #############
############################################################

    def mousePressEvent(self, eventQMouseEvent):
        if self.cropping:
            self.originQPoint = eventQMouseEvent.pos()
            self.currentQRubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
            self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, QtCore.QSize()))
            self.currentQRubberBand.show()

        elif self.rectangling or self.ellipsing and eventQMouseEvent.button() == Qt.LeftButton:
            self.lastPoint = eventQMouseEvent.pos()
            self.painting = True

        elif eventQMouseEvent.button() == Qt.LeftButton:
            self.lastPoint = eventQMouseEvent.pos()
            self.painting = True


    def mouseMoveEvent(self, eventQMouseEvent):
        if self.cropping:
            self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint,
                                         eventQMouseEvent.pos()).normalized())

        elif (eventQMouseEvent.buttons() & Qt.LeftButton) and \
                                        self.painting and not(self.rectangling or self.ellipsing):
            self.drawLineTo(eventQMouseEvent.pos())


    def mouseReleaseEvent(self, eventQMouseEvent):
        if self.cropping:
            self.currentQRubberBand.hide()
            currentQRect = self.currentQRubberBand.geometry()
            self.currentQRubberBand.deleteLater()
            cropQPixmap = self.pixmap().copy(currentQRect)
            cropQPixmap.save("crop_img.jpg")

        elif self.rectangling and eventQMouseEvent.button() == Qt.LeftButton and self.painting:
            self.draw_Rect(eventQMouseEvent.pos())
            self.painting = False

        elif self.ellipsing and eventQMouseEvent.button() == Qt.LeftButton and self.painting:
            self.draw_Ellipse(eventQMouseEvent.pos())
            self.painting = False

        elif eventQMouseEvent.button() == Qt.LeftButton and self.painting:
            self.drawLineTo(eventQMouseEvent.pos())
            self.painting = False
         
############################################################
################### MainWindow Class #######################
############################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        QMainWindow.__init__(self)

        
        self.saveAsActs = []
        self.paintArea = PaintArea()
        self.setCentralWidget(self.paintArea)
        self.createActions()
        self.createMenus()     

        self.setWindowTitle("Paint")
        self.resize(500, 500)

############################################################
##################### Menu's settings ######################
############################################################

        self.setStyleSheet("""
        QMenuBar {
            background-color: rgb(255, 192, 203);
            color: rgb(255,192,203);
            border: 1px solid #000;
        }

        QMenuBar::item {
            background-color: rgb(255,192,203);
            color: rgb(49,49,49);
        }

        QMenuBar::item::selected {
            background-color: rgb(255,160,122);
        }

        QMenu {
            background-color: rgb(255,192,203);
            color: rgb(49,49,49);
            border: 1px solid #000;           
        }

        QMenu::item::selected {
            background-color: rgb(255,160,122);
        }
    """)

############################################################        

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

############################################################            

    def open(self):
        if self.maybeSave():
            self.fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                                                      QDir.currentPath())
            if self.fileName:
                self.paintArea.openImage(self.fileName)
                self.colorfulAct.setEnabled(True)
                self.Black_WhiteAct.setEnabled(True)
                self.CropAct.setEnabled(True)
                self.CancelCropAct.setEnabled(True)
                self.printAct.setEnabled(True)
                self.zoomInAct.setEnabled(True)
                self.zoomOutAct.setEnabled(True)
                self.rotateAct.setEnabled(True)
                self.mirrorAct.setEnabled(True)
                self.PicasoAct.setEnabled(True)
                return self.fileName

############################################################
####### Function called by Colorful Effect Action ##########
############################################################

    def eff(self):
        if self.maybeSave():
             self.paintArea.eff_img(self.fileName)

############################################################
######## Function called by Black & White Action ###########
############################################################

    def B_w(self):
        if self.maybeSave():
             self.paintArea.black_white_img(self.fileName)

############################################################
############ Function called by cropping action ############
############################################################

    def crop(self):
        if self.maybeSave():
            self.paintArea.crop_img(self.fileName, self.event)

    def cancelcrop(self):
        if self.maybeSave():
            self.paintArea.Cancel_Crop()

#############################################################
############# Function called for erasing action ############
#############################################################

    def erase(self):
        if self.maybeSave():
            self.paintArea.erase_img() 

############################################################
######## Function called for drawing rect action ###########
############################################################

    def Rect(self):
        if self.maybeSave():
            self.paintArea.rect_draw()

############################################################
####### Function called for drawing ellipse action #########
############################################################

    def Ellipse(self):
        if self.maybeSave():
            self.paintArea.ellipse_draw()

############################################################
####### Function for canceling drawing shape action ########
############################################################

    def cancelshape(self):
        self.paintArea.Cancel_Shape()

############################################################
####### Functions called for zoom in and out actions #######
############################################################

    def zoomIn(self):
        size = self.paintArea.image.size() * 1.25
        self.paintArea.image = self.paintArea.image.scaled(size)
        self.paintArea.update()

    def zoomOut(self):
        height = self.paintArea.image.size() * 0.8
        self.paintArea.image = self.paintArea.image.scaled(height)
        self.paintArea.update()

############################################################

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)

############################################################

    def penColor(self):
        newColor = QColorDialog.getColor(self.paintArea.penColor())
        if newColor.isValid():
            self.paintArea.setPenColor(newColor)

############################################################

    def penWidth(self):
        newWidth, ok = QInputDialog.getInt(self, "Paint",
                                           "Select pen width:", self.paintArea.penWidth(), 1, 50, 1)
        if ok:
            self.paintArea.setPenWidth(newWidth)

############################################################
############ Function called for mirroring action ##########
############################################################

    def mirror(self):
        self.paintArea.Mirror()

############################################################
######### Functions called for Typing Text action ##########
############################################################

    def TypeText(self):
        self.paintArea.type_text()  
    def EndText(self):
        self.paintArea.end_text()

############################################################
############ Function called for about action ##############
############################################################

    def about(self):
        QMessageBox.about(self, "About Paint",
                          "<p> This Project is done by Fatemeh Khormizi & Melika Vahdat"
                          " under supervision of Dr.Jahanshahi as the course project of "
                          "Advanced Programming.</p>"
                          "<p>The <b>Paint</b> project shows how to use "
                          "QMainWindow as the base widget for an application, and how "
                          "to reimplement some of QWidget's event handlers to receive "
                          "the events generated for the application's widgets:</p>"
                          "<p> We reimplement the mouse event handlers to facilitate "
                          "drawing, the paint event handler to update the application "
                          "and the resize event handler to optimize the application's "
                          "appearance. In addition we reimplement the close event "
                          "handler to intercept the close events before terminating "
                          "the application.</p>"
                          "<p> The Project also demonstrates how to use QPainter to "
                          "draw an image in real time, as well as to repaint "
                          "widgets.</p>")

############################################################
############ Function   for     Actions  ###################
############################################################      

    def createActions(self):

        #####################################################
        ############### File Menu's Actions #################
        #####################################################

        self.openAct = QAction(QIcon("Pictures\Open-icon.png"), "&Open...", self,
                                shortcut="Ctrl+O",triggered=self.open)

        for format in QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.printAct = QAction(QIcon("Pictures\print.jpg"), "&Print...", self,
                                triggered=self.paintArea.print_)

        self.exitAct = QAction(QIcon("Pictures\exit.jpg"),"&Exit", self, shortcut="Ctrl+Q",
                               triggered=self.close)

        ####################################################
        ############# Options Menu's Actions ###############
        ####################################################

        self.penColorAct = QAction(QIcon("Pictures\pencolor.jpg"),"&Pen Color...", self,
                                triggered=self.penColor)

        self.penWidthAct = QAction(QIcon("Pictures\penwidth.png"), "Pen &Width...", self,
                                triggered=self.penWidth)

        self.EraseAct = QAction(QIcon("Pictures\eraser.jpg"),"&Erase", self, 
                                triggered=self.erase)

        self.CopyAct = QAction(QIcon("Pictures\copy.png"), "&Copy", self, 
                              triggered=self.paintArea.Copy)

        self.PasteAct = QAction(QIcon("Pictures\paste.ico"), "&Paste", self, 
                              triggered=self.paintArea.Paste)

        self.clearScreenAct = QAction(QIcon("Pictures\clear.jpg"),"&Clear Screen", self,
                                 shortcut="Ctrl+L",triggered=self.paintArea.clearImage)

        ###################################################
        ######## Image Processing Menu's Actions ##########
        ###################################################

        self.colorfulAct = QAction(QIcon("Pictures\effect.png"),"&Colorful Effect", self,
                                 enabled=False, triggered=self.eff)

        self.Black_WhiteAct = QAction(QIcon("Pictures\BW.png"),"&Black and White", self,
                                 enabled=False, triggered=self.B_w)

        self.mirrorAct = QAction(QIcon("Pictures\mirror.png"),"&Mirroring", self,
                                enabled=False, triggered=self.mirror)

        self.rotateAct = QAction(QIcon("Pictures\Rotate.png"), "&Rotate", self, 
                                enabled=False, triggered=self.paintArea.Rotate)

        self.PicasoAct = QAction(QIcon("Pictures\Picaso-icon.png"),"&Picaso effect", self,
                              enabled=False, triggered=self.paintArea.Picaso)

        self.textAct = QAction(QIcon("Pictures\\type.png"),"&Type Text", self,
                                triggered=self.TypeText)

        self.endTextAct = QAction(QIcon("Pictures\cancel.jpg"), "&End Type", self,
                               triggered=self.EndText)                                      

        self.CropAct = QAction(QIcon("Pictures\crop.png"),"&Crop", self,
                                 enabled=False,triggered=self.crop)

        self.CancelCropAct = QAction(QIcon("Pictures\cancel.jpg"),"&Cancel Crop", self,
                                 enabled=False, triggered=self.cancelcrop)

        #################################################
        ############## View Menu's Actions ##############
        #################################################

        self.zoomInAct = QAction(QIcon("Pictures\zoom_in.png"), "Zoom &In (25%)", self,
                                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction(QIcon("Pictures\zoom_out.png"),"Zoom &Out (25%)", self,
                                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        #################################################
        ############## Shape Menu's Actions #############
        #################################################

        self.DrawRectAct = QAction(QIcon("Pictures\\rectangle.png"),"&Rectangle", self,
                                triggered=self.Rect)

        self.DrawEllipseAct = QAction(QIcon("Pictures\ellipse.png"),"&Ellipse", self,
                                triggered=self.Ellipse)

        self.CancelShapeAct = QAction(QIcon("Pictures\cancel.jpg"),"&Cancel Shape", self,
                                triggered=self.cancelshape)

        ####################################################
        ############## Help Menu's Functions ###############
        ####################################################

        self.aboutAct = QAction(QIcon("Pictures\\about.png"),"&About", self,
                                 triggered=self.about)

        self.aboutQtAct = QAction(QIcon("Pictures\Qt.png"), "About &Qt", self,
                                triggered=QApplication.instance().aboutQt)

############################################################

    def createMenus(self):
        self.saveAsMenu = QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        self.effectMenu = QMenu("&Effect", self)
        self.effectMenu.addAction(self.colorfulAct)
        self.effectMenu.addAction(self.PicasoAct)

        fileMenu = QMenu("&File", self)
        fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addAction(self.printAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addAction(self.EraseAct)
        optionMenu.addAction(self.CopyAct)
        optionMenu.addAction(self.PasteAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)



        imgprocMenu = QMenu("&Image Processing", self)
        imgprocMenu.addMenu(self.effectMenu)
        imgprocMenu.addAction(self.Black_WhiteAct)
        imgprocMenu.addAction(self.mirrorAct)
        imgprocMenu.addAction(self.rotateAct)
        imgprocMenu.addSeparator()
        imgprocMenu.addAction(self.textAct)
        imgprocMenu.addAction(self.endTextAct)
        imgprocMenu.addSeparator()
        imgprocMenu.addAction(self.CropAct)
        imgprocMenu.addAction(self.CancelCropAct)       
        
        viewMenu = QMenu("&View", self)
        viewMenu.addAction(self.zoomInAct)
        viewMenu.addAction(self.zoomOutAct)

        shapeMenu = QMenu("&Shape", self)
        shapeMenu.addAction(self.DrawRectAct)
        shapeMenu.addAction(self.DrawEllipseAct)
        shapeMenu.addSeparator()
        shapeMenu.addAction(self.CancelShapeAct)

        helpMenu = QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(viewMenu)
        self.menuBar().addMenu(imgprocMenu)
        self.menuBar().addMenu(shapeMenu)
        self.menuBar().addMenu(helpMenu)

############################################################
####### This function is called if modified is True ########
############################################################

    def maybeSave(self):
        if self.paintArea.isModified():
            ret = QMessageBox.warning(self, "Paint",
                                      "The image has been modified.\n"
                                      "Do you want to save your changes?",
                                      QMessageBox.Save | QMessageBox.Discard |
                                      QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QMessageBox.Cancel:
                return False

        return True

############################################################

    def saveFile(self, fileFormat):
        initialPath = QDir.currentPath() + '/h/untitled.' + fileFormat

        fileName, _ = QFileDialog.getSaveFileName(self, "Save As", initialPath,
                            "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.paintArea.saveImage(fileName, fileFormat)

        return False

############################################################

if __name__ == '__main__':
    import sys
    pr = cProfile.Profile()
    pr.enable()
    app = QApplication(sys.argv)
    window = MainWindow()

    ########################################################
    ####### System Tray Icon  and Profiling the code #######
    ########################################################

    trayIcon = QSystemTrayIcon(QtGui.QIcon("Pictures\paint_Icon.png"), app)
    menu = QMenu()
    exitAction = menu.addAction("Exit")
    trayIcon.setContextMenu(menu)
    trayIcon.show()

    window.setWindowIcon(QIcon('Pictures\paint_Icon.png'))
    window.show()
    pr.disable()
    p = pstats.Stats(pr)
    p.strip_dirs().sort_stats('time').print_stats()
    sys.exit(app.exec_())
    
