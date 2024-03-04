import numpy
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QAction, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QLineEdit, QGridLayout, QListWidget, QGraphicsRectItem
from IO_Image import IO_Image
import sys
from Processing_Correction import Processing_Correction
from ImagePreview import ImageDisplayWidget
from PyQt5.QtGui import  QPixmap, QPainter
from PyQt5.QtCore import QRectF, pyqtSignal, QPoint
from image_segmentation import SegConnectedThreshold
from volume_meshing import MarchingCube, save_mesh
from Morphological_Operations import closing, dilate
import yaml
import glob
import numpy as np
from datetime import datetime
import time

class MainWindow(QMainWindow):

    MovedOnVisualizer = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.Data = {}
        self.current_im_display = ''
        self._createMenuBar()
        self.readConfigFile()
        print(self.config)



        mainLayout = QGridLayout()

        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 3)

        self.imageSelection = QListWidget()
        self.imageVisu = ImageDisplayWidget('')


        mainLayout.addWidget(self.imageSelection,0,0)
        mainLayout.addWidget(self.imageVisu,0,1)
        self.imageSelection.itemClicked.connect(self._DisplayData)


        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)
        self.show()

    def readConfigFile(self):
        with open("saveParameters.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def writeConfigFile(self):

        with open("saveParameters.yaml", "w") as stream:
            try:
                yaml.dump(self.config, stream)
            except yaml.YAMLError as exc:
                print(exc)

    def _DisplayData(self):
        self.current_selection = self.imageSelection.currentItem().text()

        if self.current_selection != self.current_im_display:
            self.imageVisu._setDataVolume(self.Data[self.current_selection])
            self.current_im_display = self.current_selection

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        self.OpenAction = QAction('Open',self)
        fileMenu.addAction(self.OpenAction)
        self.ImportSequenceAction = QAction('Import Image Sequence', self)
        fileMenu.addAction(self.ImportSequenceAction)
        self.SaveAction = QAction('Save', self)
        fileMenu.addAction(self.SaveAction)


        # Creating menus using a title
        processingMenu = menuBar.addMenu("&Processing")
        CorrectionMenu = processingMenu.addMenu('Correction')
        self.NormalizationAction = QAction('Normalization',self)
        CorrectionMenu.addAction(self.NormalizationAction)

        SegmentationMenu = processingMenu.addMenu('Region Growing Segmentation')
        self.SegmentationAction = QAction('Segmentation')
        SegmentationMenu.addAction(self.SegmentationAction)

        DoubleThresholdMenu = processingMenu.addMenu('Double Threshold Segmentation')
        self.DoubleThresholdAction = QAction('Set Thresholds')
        DoubleThresholdMenu.addAction(self.DoubleThresholdAction)

        SimpleThresholdMenu = processingMenu.addMenu('Simple Threshold Segmentation')
        self.SimpleThresholdAction = QAction('Set Threshold')
        SimpleThresholdMenu.addAction(self.SimpleThresholdAction)

        MorphologicalOperationMenu = processingMenu.addMenu('Morphologial operations')
        self.ClosingAction = QAction('Binary Closing Image Filter')
        self.DilateAction = QAction ('Binary Dilate Image Filter')
        MorphologicalOperationMenu.addAction(self.ClosingAction)
        MorphologicalOperationMenu.addAction(self.DilateAction)

        ImageOperationMenu = processingMenu.addMenu('Image Operations')
        self.OperationAction = QAction('Select Operations')
        ImageOperationMenu.addAction(self.OperationAction)

        MeshingMenu = processingMenu.addMenu('Meshing')
        self.MeshingAction = QAction('Create mesh')
        MeshingMenu.addAction(self.MeshingAction)



        self.movieMenu = menuBar.addMenu("&Movie")
        self.MakeMovieAction = QAction('Make Movie', self)
        self.movieMenu.addAction(self.MakeMovieAction)

        self.OpenAction.triggered.connect(self._OpenImage)
        self.SaveAction.triggered.connect(self._SaveImageSequenceGUI)
        self.ImportSequenceAction.triggered.connect(self._ImportImageSequence)
        self.NormalizationAction.triggered.connect(self._DisplayNormalization)
        self.SegmentationAction.triggered.connect(self._DisplaySegmentation)
        self.MakeMovieAction.triggered.connect(self._MovieMaker)
        self.OperationAction.triggered.connect(self._DisplayImageOperations)
        self.MeshingAction.triggered.connect(self._DisplayMeshing)
        self.ClosingAction.triggered.connect(self._DisplayMorphologicalOperations)
        self.DilateAction.triggered.connect(self._DisplayDilateOperation)
        self.DoubleThresholdAction.triggered.connect(self._DisplayDoubleThreshold)
        self.SimpleThresholdAction.triggered.connect(self._DisplaySimpleThreshold)

    def _DisplaySimpleThreshold(self):
        self.param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        row1_label = QLabel('Select Images')
        self.row1_im_sel = QComboBox()
        self.row1_im_sel.addItems(self.Data.keys())

        row2_label = QLabel('Threshold Value')
        self.row2_value = QLineEdit()


        button = QPushButton('OK')

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(button)
        row1.addWidget(row1_label)
        row1.addWidget(self.row1_im_sel)
        row2.addWidget(row2_label)
        row2.addWidget(self.row2_value)


        self.param.setLayout(layout)
        self.param.show()

        button.clicked.connect(self._RunSimpleThreshold)

    def _RunSimpleThreshold(self):

        data = np.copy(self.Data[self.row1_im_sel.currentText()])
        value = float(self.row2_value.text())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        data[data < value] = 1
        data[data > value] = 0

        self.Data['Threshold Segmentation_' + current_time + self.row1_im_sel.currentText()] = data
        self.imageSelection.addItem('Threshold Segmentation_' + current_time + self.row1_im_sel.currentText())



    def _DisplayDoubleThreshold(self):
        self.param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        row1_label = QLabel('Select Images')
        self.row1_im_sel = QComboBox()
        self.row1_im_sel.addItems(self.Data.keys())

        row2_label = QLabel('Min/Max Threshold Values')
        self.row2_minvalue = QLineEdit()
        self.row2_maxvalue = QLineEdit()

        button = QPushButton('OK')

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(button)
        row1.addWidget(row1_label)
        row1.addWidget(self.row1_im_sel)
        row2.addWidget(row2_label)
        row2.addWidget(self.row2_minvalue)
        row2.addWidget(self.row2_maxvalue)

        self.param.setLayout(layout)
        self.param.show()

        button.clicked.connect(self._RunDoubleThreshold)

    def _RunDoubleThreshold(self):

        data = np.copy(self.Data[self.row1_im_sel.currentText()])
        min = float(self.row2_minvalue.text())
        max = float(self.row2_maxvalue.text())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        data[data < min] = 0
        data[data > max] = 1



        self.Data['Threshold Segmentation_' + current_time + self.row1_im_sel.currentText()] = data
        self.imageSelection.addItem('Threshold Segmentation_' + current_time + self.row1_im_sel.currentText())

    def _DisplayDilateOperation(self):
        self.closing_param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()



        row1_label = QLabel('Image to segment:')
        self.row1_im_sel = QComboBox()
        self.row1_im_sel.addItems(self.Data.keys())

        row2_label = QLabel('Radius')
        self.row2_edit_1 = QLineEdit()

        button = QPushButton('OK')


        row1.addWidget(row1_label)
        row1.addWidget(self.row1_im_sel)
        row2.addWidget(row2_label)
        row2.addWidget(self.row2_edit_1)



        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(button)
        self.closing_param.setLayout(layout)
        self.closing_param.show()

        button.clicked.connect(self.RunDilate)

    def RunDilate(self):
        data = self.Data[self.row1_im_sel.currentText()]
        radius = int(self.row2_edit_1.text())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        output_volume = dilate(data,radius)

        self.Data['Dilated Volume_' + current_time + self.row1_im_sel.currentText()] = output_volume
        self.imageSelection.addItem('Dilated Volume_' + current_time + self.row1_im_sel.currentText())



    def _DisplayMorphologicalOperations(self):
        self.closing_param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()



        row1_label = QLabel('Image to segment:')
        self.row1_im_sel = QComboBox()
        self.row1_im_sel.addItems(self.Data.keys())

        row2_label = QLabel('Radius')
        self.row2_edit_1 = QLineEdit()

        button = QPushButton('OK')


        row1.addWidget(row1_label)
        row1.addWidget(self.row1_im_sel)
        row2.addWidget(row2_label)
        row2.addWidget(self.row2_edit_1)



        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(button)
        self.closing_param.setLayout(layout)
        self.closing_param.show()

        button.clicked.connect(self.RunClosing)

    def RunClosing(self):
        data = self.Data[self.row1_im_sel.currentText()]
        radius = int(self.row2_edit_1.text())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        output_volume = closing(data,radius)

        self.Data['Closed Volume_' + current_time + self.row1_im_sel.currentText()] = output_volume
        self.imageSelection.addItem('Closed Volume_' + current_time + self.row1_im_sel.currentText())


    def _DisplayMeshing(self):
        self.meshing_param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()
        row4 = QHBoxLayout()

        row_1_label = QLabel('Volume to mesh:')
        self.row_1_im_sel = QComboBox()
        self.row_1_im_sel.addItems(self.Data.keys())

        row_2_label = QLabel('Threshold value:')
        self.row_2_value = QLineEdit()


        row4_folder = QPushButton('FOLDER')
        row4_click = QPushButton('MESH & SAVE')

        row1.addWidget(row_1_label)
        row1.addWidget(self.row_1_im_sel)
        row2.addWidget(row_2_label)
        row2.addWidget(self.row_2_value)

        row4.addWidget(row4_folder)
        row4.addWidget(row4_click)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(row3)
        layout.addLayout(row4)

        self.meshing_param.setLayout(layout)
        self.meshing_param.show()


        row4_folder.clicked.connect(self._Select_folder)

        row4_click.clicked.connect(self._RunMeshing)


    def _RunMeshing(self):
        vol = self.Data[self.row_1_im_sel.currentText()]
        threshold = float(self.row_2_value.text())
        self.outputpath_movie += '/mesh.ply'
        print(self.outputpath_movie)

        MarchingCube(vol, threshold, self.outputpath_movie)



    def _DisplaySegmentation(self):
        self.segmentation_param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()


        row1_label = QLabel('Image to segment:')
        self.row1_im_sel = QComboBox()
        self.row1_im_sel.addItems(self.Data.keys())

        row2_label = QLabel('Value x,y,z')
        self.row2_edit_1 = QLineEdit()
        self.row2_edit_2 = QLineEdit()
        self.row2_edit_3 = QLineEdit()
        row3_thresold = QLabel('Segmentaion min/max threshold')
        self.row3_min = QLineEdit()
        self.row3_max = QLineEdit()
        button = QPushButton('OK')


        row1.addWidget(row1_label)
        row1.addWidget(self.row1_im_sel)
        row2.addWidget(row2_label)
        row2.addWidget(self.row2_edit_1)
        row2.addWidget(self.row2_edit_2)
        row2.addWidget(self.row2_edit_3)
        row3.addWidget(row3_thresold)
        row3.addWidget(self.row3_min)
        row3.addWidget(self.row3_max)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(row3)
        layout.addWidget(button)
        self.segmentation_param.setLayout(layout)
        self.segmentation_param.show()

        button.clicked.connect(self._RunSegmentation)

    def _RunSegmentation(self):
        vol = self.Data[self.row1_im_sel.currentText()]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        val_min = float( self.row3_min.text())
        val_max = float(self.row3_max.text())
        seedListToSegment = [[int(self.row2_edit_1.text()), int(self.row2_edit_2.text()), int(self.row2_edit_3.text())]]
        print(seedListToSegment)

        self.Data['Segmented Volume_' + current_time + self.row1_im_sel.currentText()] = SegConnectedThreshold(vol, val_min, val_max, seedListToSegment)
        self.imageSelection.addItem('Segmented Volume_' +current_time + self.row1_im_sel.currentText())



    def _DisplayImageOperations(self):
        self.imageop_param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        row1_label_1 = QLabel('Image 1:')
        self.row1_im_sel_1 = QComboBox()
        self.row1_im_sel_1.addItems(self.Data.keys())
        im_op_list = ['Multiplication', 'Mask Inversion', 'Substraction', 'Addition']
        row1_label_2 = QLabel('Operation:')
        self.row1_op_sel = QComboBox()
        self.row1_op_sel.addItems(im_op_list)
        row1_label_3 = QLabel('Image 2:')
        self.row1_im_sel_2 = QComboBox()
        self.row1_im_sel_2.addItems(self.Data.keys())
        row2_button = QPushButton('OK')

        row1.addWidget(row1_label_1)
        row1.addWidget(self.row1_im_sel_1)
        row1.addWidget(row1_label_2)
        row1.addWidget(self.row1_op_sel)
        row1.addWidget(row1_label_3)
        row1.addWidget(self.row1_im_sel_2)
        row2.addWidget(row2_button)

        layout.addLayout(row1)
        layout.addLayout(row2)
        self.imageop_param.setLayout(layout)
        self.imageop_param.show()
        row2_button.clicked.connect(self._RunOperations)

    def _RunOperations(self):
        vol1 = self.Data[self.row1_im_sel_1.currentText()]
        vol2 = self.Data[self.row1_im_sel_2.currentText()]
        print(self.row1_op_sel.currentIndex())
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        if self.row1_op_sel.currentIndex() == 0:
            self.Data['Multiplied result_' + current_time] = np.multiply(vol1, vol2)
            self.imageSelection.addItem('Multiplied result_' + current_time)
        elif self.row1_op_sel.currentIndex() == 1:
            self.Data['Inverted mask_' + current_time] = np.invert(vol1)-254
            self.imageSelection.addItem('Inverted mask_' + current_time)
        elif self.row1_op_sel.currentIndex() == 2:
            self.Data['Substracted result_' + current_time] = np.abs(np.subtract(vol1, vol2))
            self.imageSelection.addItem('Substracted result_' + current_time)
        elif self.row1_op_sel.currentIndex() == 3:
            vol =  np.add(vol1, vol2)
            vol[vol>1] = 1
            self.Data['Added result_' + current_time] = vol
            self.imageSelection.addItem('Added result_' + current_time)

    def _OpenImage (self):
        fileDialog = QFileDialog()
        mainPath = fileDialog.getOpenFileName(self, 'Select an Image')[0]
        importer = IO_Image(mainPath)
        self.Data[mainPath] = importer.readOneImage()
        self.imageSelection.addItem(mainPath)
        print(self.Data)

    def _ImportImageSequence (self):
        self.ImportImageSequenceWindow = QWidget()
        layout = QHBoxLayout()
        self.label_frame_skip = QLabel('Open every x image:')
        self.text_enter = QLineEdit('1')
        self.flag_label = QLabel('Open full folder')
        self.FLag_full_folder = QCheckBox()


        self.button = QPushButton('Load')
        layout.addWidget(self.label_frame_skip)
        layout.addWidget(self.text_enter)
        layout.addWidget(self.flag_label)
        layout.addWidget(self.FLag_full_folder)
        layout.addWidget(self.button)
        self.ImportImageSequenceWindow.setLayout(layout)
        self.button.clicked.connect(self._RunImageImport)
        self.ImportImageSequenceWindow.show()

    def _RunImageImport (self):
        frame_skip = int(self.text_enter.text())
        fileDialog = QFileDialog()

        if  self.FLag_full_folder.isChecked():
            mainPath = fileDialog.getExistingDirectory(self, 'Select Folder')
            mainPath = glob.glob(mainPath+'/*')
            mainPath.sort()
        else:
            mainPath = fileDialog.getOpenFileNames(self, 'Select Images')[0]

        importer = IO_Image(mainPath)
        self.Data[mainPath[0]] = importer.readAllImages(frame_skip)
        self.imageSelection.addItem(mainPath[0])


    def _SaveImageSequenceGUI (self):
        self.SaveImageSequenceWindow = QWidget()
        layout = QHBoxLayout()
        self.select_image = QComboBox()
        self.select_image.addItems(self.Data.keys())
        button = QPushButton('Save')
        layout.addWidget(self.select_image)
        layout.addWidget(button)
        self.SaveImageSequenceWindow.setLayout(layout)
        button.clicked.connect(self._SaveImageSequenceRun)
        self.SaveImageSequenceWindow.show()

    def _SaveImageSequenceRun (self):
        fileDialog = QFileDialog()
        mainPath = fileDialog.getSaveFileName(self, 'Select Folder')[0]
        print(mainPath)
        importer = IO_Image(mainPath)
        importer.SaveAllImages(self.Data[self.select_image.currentText()])


    def _DisplayNormalization (self):

        self.normalization_param = QWidget()
        layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()
        row4 = QHBoxLayout()

        row1_label = QLabel('Projection:')
        self.row1_im_sel = QComboBox()
        self.row1_im_sel.addItems(self.Data.keys())

        row2_label = QLabel('Reference:')
        self.row2_im_sel = QComboBox()
        self.row2_im_sel.addItems(self.Data.keys())
        self.row2_check = QCheckBox()

        row3_label = QLabel('Dark:')
        self.row3_im_sel = QComboBox()
        self.row3_check = QCheckBox()
        self.row3_im_sel.addItems(self.Data.keys())

        row4_button = QPushButton('Compute')

        row1.addWidget(row1_label)
        row1.addWidget(self.row1_im_sel)
        row1.addSpacing(10)
        row2.addWidget(row2_label)
        row2.addWidget(self.row2_im_sel)
        row2.addWidget(self.row2_check)
        row3.addWidget(row3_label)
        row3.addWidget(self.row3_im_sel)
        row3.addWidget(self.row3_check)
        row4.addWidget(row4_button)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.addLayout(row1)
        main_vertical_layout.addLayout(row2)
        main_vertical_layout.addLayout(row3)
        main_vertical_layout.addLayout(row4)
        self.normalization_param.setLayout(main_vertical_layout)
        row4_button.clicked.connect(self._RunNormalization)
        self.normalization_param.show()

    def _RunNormalization (self):

        Normalize_function = Processing_Correction()

        if self.row2_check.isChecked():
            vol_proj = self.Data[self.row1_im_sel.currentText()]
            vol_ref = self.Data[self.row2_im_sel.currentText()]
            if self.row3_check.isChecked():
                vol_dark = self.Data[self.row3_im_sel.currentText()]
            else:
                vol_dark = []
            self.Data['Normalized Volume'] = Normalize_function.normalizationAllImages(vol_proj, vol_ref, vol_dark=[])

        else:
            vol_proj = self.Data[self.row2_im_sel.currentText()]

            self.Data['Normalized Volume ' + self.row1_im_sel.currentText()] =Normalize_function.createReferences(vol_proj,10,50, True)

        self.imageSelection.addItem('Normalized Volume ' + self.row1_im_sel.currentText())

    def display_scalebar(self):
        checked_status = self.row3_add_scale_bar_check.isChecked()
        if checked_status == True:
            pixel_size = float(self.row3_magnification.text())
            data_size = self.Data[self.current_selection].shape[2]
            FoV = int((data_size/10.0)*pixel_size/1000)

            if FoV < 1 :
                flag_micro = True
                FoV = int((data_size / 10.0) * pixel_size)
                if FoV > 100:
                    FoV = int(FoV/100.0)*100
                FoV1 = FoV / pixel_size


            else:
                flag_micro = False
                FoV1 = FoV / pixel_size * 1000


            self.imageVisu.imageVisualizer.flagtxt1 = True
            self.imageVisu.imageVisualizer.sizeScaleBar = FoV1
            if flag_micro:
                self.imageVisu.imageVisualizer.textstr1 = str(FoV) + ' \u03BCm'
            else:
                self.imageVisu.imageVisualizer.textstr1 = str(FoV) + ' mm'
            label_x_pos = float(self.row3_xpos_label_val.text())
            label_y_pos = float(self.row3_ypos_label_val.text())
            bar_x_pos = float(self.row3_xpos_bar_val.text())
            bar_y_pos = float(self.row3_ypos_bar_val.text())
            self.imageVisu.imageVisualizer.Item1Pos = QPoint(label_x_pos,label_y_pos)
            self.imageVisu.imageVisualizer.scaleBarPos = QPoint(bar_x_pos, bar_y_pos)
            self.imageVisu.imageVisualizer.display_image()

        else:
            self.imageVisu.imageVisualizer.flagtxt1 = False
            self.imageVisu.imageVisualizer.display_image()


    def display_text(self):
        checked_status = self.row4_add_text_check.isChecked()
        if checked_status == True:
            self.imageVisu.imageVisualizer.flagtxt2 = True
            self.imageVisu.imageVisualizer.textstr2 = self.row4_givetext.text()
            title_pos_x = float(self.row4_xpos.text())
            title_pos_y = float(self.row4_ypos.text())
            self.imageVisu.imageVisualizer.Item2Pos = QPoint(title_pos_x,title_pos_y)
            self.imageVisu.imageVisualizer.display_image()

        else:
            self.imageVisu.imageVisualizer.flagtxt2 = False
            self.imageVisu.imageVisualizer.display_image()

    def display_time(self):
        checked_status = self.row5_add_time_check.isChecked()
        fps = float(self.row2_box1.text())
        self.imageVisu.imageVisualizer.frame_rate = fps

        if checked_status == True:
            self.imageVisu.imageVisualizer.flagtxt3 = True
            pos_time_x = float(self.row5_xpos.text())
            pos_time_y = float(self.row5_ypos.text())
            starting_time = self.row5_starting_time.text()
            self.imageVisu.imageVisualizer.starting_time = float(starting_time)
            self.imageVisu.imageVisualizer.Item3Pos = QPoint(pos_time_x,pos_time_y)
            self.imageVisu.imageVisualizer.display_image()
        else:
            self.imageVisu.imageVisualizer.flagtxt3 = False
            self.imageVisu.imageVisualizer.display_image()

    def _MovieMaker (self):
        self.movie_popup = QWidget()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()
        row4 = QHBoxLayout()
        row5 = QHBoxLayout()
        row5b = QHBoxLayout()
        row6 = QHBoxLayout()

        row1_label = QLabel('Select Image Sequence:')
        row1_im_select = QComboBox()
        row1_im_select.addItems(self.Data.keys())

        row2_given_fr = QLabel('Frame Rate:')
        frame_rate = str(self.config['Movie Parameter']['Frame_Rate'])
        self.row2_box1 = QLineEdit(frame_rate)
        row2_select_fr = QLabel('Set Movie Frame Rate:')
        frame_rate_saved = str(self.config['Movie Parameter']['Frame_Rate_Saved'])
        self.row2_box2 = QLineEdit(frame_rate_saved)

        row3_add_scale_label = QLabel('Add Scale Bar to Movie?')
        self.row3_add_scale_bar_check = QCheckBox()
        self.row3_add_scale_bar_check.clicked.connect(self.display_scalebar)
        row3_magnification_label = QLabel('Pixel size [um]:')
        pixel_size = str(self.config['Movie Parameter']['Pixel_Size'])
        self.row3_magnification = QLineEdit(pixel_size)

        row3_xpos_label_label = QLabel('X-position-Label')
        pos_x_bar_label = str(self.config['Movie Parameter']['Pos_Label_Scale_Bar'][0])
        self.row3_xpos_label_val = QLineEdit(str(pos_x_bar_label))
        row3_ypos_label_label = QLabel('Y-position-Label')
        pos_y_bar_label = str(self.config['Movie Parameter']['Pos_Label_Scale_Bar'][1])
        self.row3_ypos_label_val = QLineEdit(str(pos_y_bar_label))
        row3_xpos_bar_label = QLabel('X-position-Bar')
        pos_x_bar = str(self.config['Movie Parameter']['Pos_Scale_Bar'][0])
        self.row3_xpos_bar_val = QLineEdit(str(pos_x_bar))
        row3_ypos_bar_label = QLabel('Y-position-Bar')
        pos_y_bar = str(self.config['Movie Parameter']['Pos_Scale_Bar'][1])
        self.row3_ypos_bar_val = QLineEdit(str(pos_y_bar))


        row4_add_text_label = QLabel('Add Text to Movie?')
        self.row4_add_text_check = QCheckBox()
        self.row4_add_text_check.clicked.connect(self.display_text)
        row4_text_label = QLabel('Text:')
        title = str(self.config['Movie Parameter']['Title'])
        self.row4_givetext = QLineEdit(title)
        row4_xpos_label = QLabel('X-position')
        pos_x_title = str(self.config['Movie Parameter']['Pos_Title'][0])
        self.row4_xpos = QLineEdit(str(pos_x_title))
        pos_y_title = str(self.config['Movie Parameter']['Pos_Title'][1])
        row4_ypos_label = QLabel('Y-position')
        self.row4_ypos = QLineEdit(str(pos_y_title))

        row5_add_time_label = QLabel('Add Time to Movie?')
        self.row5_add_time_check = QCheckBox()
        self.row5_add_time_check.clicked.connect(self.display_time)
        row5_add_start_time_label = QLabel('Starting Time')
        start_time = str(self.config['Movie Parameter']['Starting_time'])
        self.row5_starting_time = QLineEdit(start_time)
        row5_xpos_label = QLabel('X-position')
        pos_x_time = str(self.config['Movie Parameter']['Pos_Time'][0])
        self.row5_xpos = QLineEdit(str(pos_x_time))
        row5_ypos_label = QLabel('Y-position')
        pos_y_time = str(self.config['Movie Parameter']['Pos_Time'][1])
        self.row5_ypos = QLineEdit(str(pos_y_time))


        row5b_contrast_start =QLabel('Contrast Values Start [min, max]')
        row5b_contrast_end = QLabel('Contrast Values End [min, max]')
        min_contrast_start = str(self.config['Movie Parameter']['Pos_Contrast'][0])
        max_contrast_start = str(self.config['Movie Parameter']['Pos_Contrast'][1])
        min_contrast_end = str(self.config['Movie Parameter']['Pos_Contrast'][2])
        max_contrast_end = str(self.config['Movie Parameter']['Pos_Contrast'][3])
        self.row5b_min_start = QLineEdit(min_contrast_start)
        self.row5b_max_start = QLineEdit(max_contrast_start)
        self.row5b_min_end = QLineEdit(min_contrast_end)
        self.row5b_max_end = QLineEdit(max_contrast_end)
        self.imageVisu.toolBar.doubleSlider.minSlider.setValue(float(min_contrast_start))
        self.imageVisu.toolBar.doubleSlider.maxSlider.setValue(float(max_contrast_start))

        row6_folder = QPushButton('FOLDER')
        row6_click = QPushButton('SAVE')

        row1.addWidget(row1_label)
        row1.addWidget(row1_im_select)
        row2.addWidget(row2_given_fr)
        row2.addWidget(self.row2_box1)
        row2.addWidget(row2_select_fr)
        row2.addWidget(self.row2_box2)
        row3.addWidget(row3_add_scale_label)
        row3.addWidget(self.row3_add_scale_bar_check)
        row3.addWidget(row3_magnification_label)
        row3.addWidget(self.row3_magnification)
        row3.addWidget(row3_xpos_label_label)
        row3.addWidget(self.row3_xpos_label_val)
        row3.addWidget(row3_ypos_label_label)
        row3.addWidget(self.row3_ypos_label_val)
        row3.addWidget(row3_xpos_bar_label)
        row3.addWidget(self.row3_xpos_bar_val)
        row3.addWidget(row3_ypos_bar_label)
        row3.addWidget(self.row3_ypos_bar_val)
        row4.addWidget(row4_add_text_label)
        row4.addWidget(self.row4_add_text_check)
        row4.addWidget(row4_text_label)
        row4.addWidget(self.row4_givetext)
        row4.addWidget(row4_xpos_label)
        row4.addWidget(self.row4_xpos)
        row4.addWidget(row4_ypos_label)
        row4.addWidget(self.row4_ypos)

        row5.addWidget(row5_add_time_label)
        row5.addWidget(self.row5_add_time_check)
        row5.addWidget(row5_add_start_time_label)
        row5.addWidget(self.row5_starting_time)
        row5.addWidget(row5_xpos_label)
        row5.addWidget(self.row5_xpos)
        row5.addWidget(row5_ypos_label)
        row5.addWidget(self.row5_ypos)
        row5b.addWidget(row5b_contrast_start)
        row5b.addWidget(self.row5b_min_start)
        row5b.addWidget(self.row5b_max_start)
        row5b.addWidget(row5b_contrast_end)
        row5b.addWidget(self.row5b_min_end)
        row5b.addWidget(self.row5b_max_end)

        row6.addWidget(row6_folder)
        row6.addWidget(row6_click)


        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.addLayout(row1)
        main_vertical_layout.addLayout(row2)
        main_vertical_layout.addLayout(row3)
        main_vertical_layout.addLayout(row4)
        main_vertical_layout.addLayout(row5)
        main_vertical_layout.addLayout(row5b)
        main_vertical_layout.addLayout(row6)
        self.movie_popup.setLayout(main_vertical_layout)
        row6_click.clicked.connect(self._Save_Display)
        row6_folder.clicked.connect(self._Select_folder)

        self.movie_popup.show()

    def _Select_folder(self):

        self.outputpath_movie = QFileDialog.getExistingDirectory()


    def _Save_Display (self):


        self.config['Movie Parameter']['Pos_Scale_Bar'][0] = self.imageVisu.imageVisualizer.scaleBarPos.x()
        self.config['Movie Parameter']['Pos_Scale_Bar'][1] = self.imageVisu.imageVisualizer.scaleBarPos.y()

        self.config['Movie Parameter']['Pos_Label_Scale_Bar'][0] = self.imageVisu.imageVisualizer.Item1Pos.x()
        self.config['Movie Parameter']['Pos_Label_Scale_Bar'][1] = self.imageVisu.imageVisualizer.Item1Pos.y()


        self.config['Movie Parameter']['Title'] = self.row4_givetext.text()
        self.config['Movie Parameter']['Pos_Title'][0] = self.imageVisu.imageVisualizer.Item2Pos.x()
        self.config['Movie Parameter']['Pos_Title'][1] = self.imageVisu.imageVisualizer.Item2Pos.y()

        self.config['Movie Parameter']['Pos_Time'][0] = self.imageVisu.imageVisualizer.Item3Pos.x()
        self.config['Movie Parameter']['Pos_Time'][1] = self.imageVisu.imageVisualizer.Item3Pos.y()

        self.config['Movie Parameter']['Frame_Rate'] = self.row2_box1.text()
        self.config['Movie Parameter']['Frame_Rate_Saved'] = self.row2_box2.text()
        self.config['Movie Parameter']['Pixel_Size'] = self.row3_magnification.text()

        min_value_start = float(self.row5b_min_start.text())
        max_value_start = float(self.row5b_max_start.text())
        min_value_end = float(self.row5b_min_end.text())
        max_value_end = float(self.row5b_max_end.text())

        self.config['Movie Parameter']['Pos_Contrast'][0] = min_value_start
        self.config['Movie Parameter']['Pos_Contrast'][1] = max_value_start
        self.config['Movie Parameter']['Pos_Contrast'][2] = min_value_end
        self.config['Movie Parameter']['Pos_Contrast'][3] = max_value_end

        nr_of_slice = self.Data[self.current_selection].shape[0]

        totalRect = QRectF(0,0,self.imageVisu.imageVisualizer.scene.width(),self.imageVisu.imageVisualizer.scene.height())

        pix = QPixmap(int(totalRect.width()), int(totalRect.height()))
        painter = QPainter(pix)

        mean_start = np.mean(self.Data[self.current_selection][0])
        mean_end = np.mean(self.Data[self.current_selection][-1])

        if mean_start != mean_end:
            flag_correction = True

            Bmin = (mean_start * min_value_end - min_value_start * mean_end)/(mean_start - mean_end)
            Amin = (min_value_start - Bmin)/mean_start
            Bmax = (mean_start * max_value_end - max_value_start * mean_end)/(mean_start - mean_end)
            Amax = (max_value_start - Bmax)/mean_start

        else:
            flag_correction = False


        for i in range (0, nr_of_slice):
            try:
                self.imageVisu.imageVisualizer.display_image()
                self.imageVisu.imageVisualizer.sliceSlider.slider.setValue(i)

                if flag_correction:
                    self.minimumValueS = (self.imageVisu.imageVisualizer.mean_value * Amin) + Bmin
                    self.maximumValueS = (self.imageVisu.imageVisualizer.mean_value * Amax) + Bmax
                    #self.minimumValueS = (self.imageVisu.imageVisualizer.mean_value * 1.9167) - 0.07
                    #self.maximumValueS = (self.imageVisu.imageVisualizer.mean_value * -0.479) + 0.11
                    self.imageVisu.toolBar.doubleSlider.maxSlider.setValue(self.maximumValueS)
                    self.imageVisu.toolBar.doubleSlider.minSlider.setValue(self.minimumValueS)
                self.imageVisu.imageVisualizer.display_image()
                self.imageVisu.imageVisualizer.scene.render(painter, totalRect)

                print(self.imageVisu.imageVisualizer.current_time)
                time.sleep(0.05)

                self.config['Movie Parameter']['Starting_time'] = float(self.imageVisu.imageVisualizer.current_time) + 1.0/float(self.row2_box1.text())
                self.writeConfigFile()
                self.readConfigFile()
                print(self.imageVisu.imageVisualizer.starting_time)
                print(self.row2_box1.text())
                pix.save(self.outputpath_movie + '/' + str(i+int(float(self.imageVisu.imageVisualizer.starting_time)*float(self.row2_box1.text()))).zfill(6)+ ".png", "PNG")
            except:
                print('Failed image n '+str(i))
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    state_window = MainWindow()
    app.exec()