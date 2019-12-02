#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import sys
import time
import random #to shuffle data and random value
from random import shuffle
import numpy as np
import pandas as pd
import math
import pandas.api.types as ptypes
from pandas import Series, DataFrame
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets

# for box or other graphs
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar,
                                                FigureCanvasQTAgg as FigureCanvas)

import matplotlib.pyplot as plt
from datetime import datetime
plt.rc('font', family='Malgun Gothic') #한글 깨짐 방지
plt.rc('axes', unicode_minus=False) #한글 깨짐 방지

#to import UI path
sys.path.append("./UI") # insert your path
sys.path.append("./PY_CODE")
import mplwidget

from PandasModel import PandasModel # for table model setting
#import window class
from ImportDataWin import ImportDataWindow
from PrivacyModel import PrivacyModel
from NonIdentifierWin import NonIdentifierWin


"""
미사용
global tab1_input # inputtable data from file, 원본 데이터
global tab2_output # 비식별화 결과 tab2_output에 저장
global Final_Output # Run 함수에서 프라이버시 모델 적용을 위해 필요

사용
self.originData: 원본데이터
self.deData: 비식별 데이터
self.Final_Output: run 함수에서 사용
"""


class MainWidget(QMainWindow):
    """
    TODO: 
    0. 비식별 클래스 / level 수정
        0. Swap(교환)
        param: 0 or 1, swap_values[]
        1. Shuffle(재배열: 랜덤하게 섞기)
        param: 0 or 1, numbsfer
        2. Suppression(범주화: 이항변수화, 이산형화)
        param: ??, ??, ??, ??
        3. Masking or Remove(마스킹 혹은 삭제)
        param: level
        4. Aggregation(통계값처리: 평균, 최빈, 최소, 최대)
        param: 통계처리인덱스(3), ??, ??, ??
        5. Rounding(라운딩: 올림, 내림, 반올림) #랜덤라운딩 삭제
        param: 라운딩기법인덱스(string), level, RandomN=0
    1. level별 처리
    2. 모델 결과
    3. progress 처리
    4. 결과 UI 및 구성 처리
    5. 기타
     - ModifyWin에서 완료버튼 수정하기
    """
    5
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./UI/NonIdentifierUI.ui") #insert your UI path
        self.ui.statusbar.showMessage("Start program") #statusbar text
        self.ui.show()        

        self.originData = [] #원본데이터
        self.deData = [] #비식별데이터
        self.InitializingGraphUI() #CorrelationGraph of tab2 초기화 

        self.ui.INPUTtable.clicked.connect(self.viewClicked) # cell 클릭 시 식별자, 준식별자 등 radio button checked 
        self.ui.actionimport_data.triggered.connect(self.ImportData) #importData from csv
        self.ui.actionsave_data.triggered.connect(self.SaveFileDialog) #export_data in menuBar, call save data event
        self.ui.actionEXIT.triggered.connect(self.CloseWindow) #exit in menuBar, call exit event

        self.ui.actionRun.triggered.connect(self.run) # TODO: 6. run 함수 구현 필요
        self.ui.actionNonIdentifier.triggered.connect(self.NonIdentifierWindow) # TODO: 3. 비식별화 함수 추가중

        #식별자 radio button change event
        self.id_dict = {}
        self.ui.ID.clicked.connect(self.radioButtonClicked) #식별자
        self.ui.QD.clicked.connect(self.radioButtonClicked) #준식별자
        self.ui.SA.clicked.connect(self.radioButtonClicked) #민감정보
        self.ui.GI.clicked.connect(self.radioButtonClicked) #일반정보

        #privacy model button event
        self.ui.privacyAdd.clicked.connect(self.PrivacyAdd)
        self.ui.privacyDelete.clicked.connect(self.PrivacyDelete)
        
        #for methodTableWidget
        self.methodCol_List = {}

        #applied method dictionary
        self.ApplyMethod = {}
        

    def ImportData(self):
        self.importwindow = ImportDataWindow(self)
        
    """
    TODO: 에러 수정
    - 데이터 없을 때 클릭하면 에러 발생 -> 수정완료
    - col = self.col -> active cell col index -> 수정중
        : col = self.ui.INPUTtable.selectionModel().selectedColumns()
    """
    def NonIdentifierWindow(self): 
        
        try:
            col = self.col
        except AttributeError as e:
            print("error")
        else:
            if(self.ui.typeTable.item(col, 1).text() != 'int64'): #int64만 수치데이터 method 사용
                type = 1
            else:
                type = 0
            
            print(self.originData[self.originData.columns[col]].to_frame())
            self.NonIdenfitierwindow = NonIdentifierWin(mainwindow, self.originData[self.originData.columns[col]].to_frame(),type)

    
    def viewClicked(self, item): #cell 클릭시 식별자 radio button checked
        self.col = item.column()
        self.row = item.row()

        print("_cellclicked... ", self.row, self.col) #클릭 cell 확인

        if(self.ui.typeTable.item(self.col,2).text() == '식별자'):
            print("식별자")
            self.ui.ID.setChecked(True)
            self.setTypeListWidget(self.id_dict['식별자'], self.col)
        elif(self.ui.typeTable.item(self.col,2).text() == '준식별자'):
            print("준식별자")
            self.ui.QD.setChecked(True)
            self.setTypeListWidget(self.id_dict['준식별자'], self.col)
        elif(self.ui.typeTable.item(self.col,2).text() == '민감정보'):
            print("민감정보")
            self.ui.SA.setChecked(True)
            self.setTypeListWidget(self.id_dict['민감정보'], self.col)
        elif(self.ui.typeTable.item(self.col,2).text() == '일반정보'):
            print("일반정보")
            self.ui.GI.setChecked(True)
            self.setTypeListWidget(self.id_dict['일반정보'], self.col)
    
    def setTables(self, types, combo_id, inputdata): #import 한 데이터 저장
        self.originData = inputdata.copy()
        self.deData = inputdata.copy()
        self.model = PandasModel(self.originData)
        self.ui.INPUTtable.setModel(self.model)

        rownum = len(self.originData.index)
        colnum = len(self.originData.columns)

        #tab1의 data type 테이블 rendering
        self.ui.typeTable.setRowCount(colnum) # 보여줄 컬럼 개수만큼 행 만들기
        for rowindex in range(colnum): #컬럼 개수만큼 행에 값 넣기         
            self.ui.typeTable.setItem(rowindex, 0, QTableWidgetItem(str(self.originData.columns[rowindex]))) #setitem 컬럼이름 
            self.ui.typeTable.setItem(rowindex, 1, QTableWidgetItem(str(types[rowindex]))) #setitem 데이터타입 입력
            self.ui.typeTable.setItem(rowindex, 2, QTableWidgetItem(str(combo_id[rowindex]))) #데이터 속성(식별자, 준식별자, 민감정보, 일반정보)
        
        self.ui.statusbar.showMessage("Imported Data Column: " + str(colnum) + ", Row: " + str(rownum)) #statusbar text, TODO: 기타. change dynamic text
    
    def radioButtonClicked(self):
        col = self.col
        if self.col > len(self.originData.columns)-1 or len(self.originData.columns) <1: # if value is null, do nothing
            print('cell has nothing(radioButtonClicked)')
        else: #if not null, radio button check
            self.removeDictionaryValue(col)
            if self.ui.ID.isChecked(): #식별자
                self.id_dict['식별자'].append(self.originData.columns[col])
                self.setTypeListWidget(self.id_dict['식별자'], col)
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("식별자")))
                print("changed to 식별자")
            elif self.ui.QD.isChecked(): #준식별자
                self.id_dict['준식별자'].append(self.originData.columns[col]) 
                self.setTypeListWidget(self.id_dict['준식별자'], col)           
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("준식별자")))
                print("changed to 준식별자")
            elif self.ui.SA.isChecked(): #민감정보
                self.id_dict['민감정보'].append(self.originData.columns[col])
                self.setTypeListWidget(self.id_dict['민감정보'], col)
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("민감정보")))
                print("changed to 민감정보")
            elif self.ui.GI.isChecked(): #일반정보
                self.id_dict['일반정보'].append(self.originData.columns[col])
                self.setTypeListWidget(self.id_dict['일반정보'], col)
                self.ui.typeTable.setItem(col, 2, QTableWidgetItem(str("일반정보")))
                print("changed to 일반정보")
                
    def removeDictionaryValue(self, col): #식별정보 바뀌면 수정
        old_id = self.ui.typeTable.item(col,2).text() 
        self.id_dict[old_id].remove(self.originData.columns[col])

    def setTypeListWidget(self, data, col): #radio button과 같은 속성만 보여주기
        self.ui.typeListWidget.clear()
        for i in data:
            self.ui.typeListWidget.addItem(i)

    def PrivacyAdd(self): #add 버튼 누르면 프라이버시 모델 설정 가능
        self.ui.privacyTable.insertRow(self.ui.privacyTable.rowCount())
        privacy_list = ["K", "L", "T"]
        self.privacycom = QComboBox() 
        self.privacycom.addItems(privacy_list)
        self.ui.privacyTable.setCellWidget(self.ui.privacyTable.rowCount()-1, 0, self.privacycom)
        self.privacycom.currentIndexChanged.connect(self.updatePrivacyModelTable)

    def updatePrivacyModelTable(self): # setting privacyTable, L이나 T 모델에서 컬럼 선택하도록하기
        combobox = self.sender()
        ix = self.ui.privacyTable.indexAt(combobox.pos())
        if self.privacycom.currentIndex() == 1:
            self.IDcom = QComboBox()
            ID_list = []
            if self.ui.typeTable.item(0,0) is None:
                print("typeTable is none")
            else:
                for i in range(self.ui.typeTable.rowCount()):
                    if(self.ui.typeTable.item(i, 2).text() == "민감정보"):
                        ID_list.append(self.ui.typeTable.item(i, 0).text())
                self.IDcom.addItems(ID_list) 
            self.ui.privacyTable.setCellWidget(ix.row(), 2, self.IDcom)
        else:
            self.ui.privacyTable.removeCellWidget(ix.row(),2)
            
    def PrivacyDelete(self):
        self.ui.privacyTable.removeRow(self.ui.privacyTable.currentRow())

    def run(self):
        self.privacy = PrivacyModel(self)
        self.Final_Output = self.deData.copy() #비식별화만 된 데이트를 프라이버시 모델에 입력

        #프라이버시 모델 적용
        for r in range(self.ui.privacyTable.rowCount()):
            widget = self.ui.privacyTable.cellWidget(r, 0)
            if isinstance(widget, QComboBox):
                current_value = widget.currentText()
                if(current_value == 'K'):
                    number = self.ui.privacyTable.item(r, 1).text()
                    self.Final_Output = self.privacy.K_anonymity(self.Final_Output, int(number))
                elif(current_value == 'L'):
                    number = self.ui.privacyTable.item(r, 1).text()
                    columnName = self.ui.privacyTable.cellWidget(r, 2).currentText()
                    self.Final_Output = self.privacy.L_diversity(self.Final_Output, number, columnName)
                elif(current_value == 'T'):
                    print(self.ui.privacyTable.item(r, 1).text())
        
        print("dtypes",self.originData.dtypes)
        print("columns", self.originData.columns)

        #데이터 유용성 데이터 부분
        #한국인터넷진흥원, 개인정보 비식별 기술 경진대회 설명회 (n.p.: 한국인터넷진흥원, n.d.), 8.
        #string형 제외
        for col in range(len(self.originData.columns)):
            #print(col)
            if str(self.originData.dtypes[col]) == "object":
                print(self.originData.dtypes[col])
                originData_int = self.originData.drop([self.originData.columns[col]], axis =1)
                finalData_int = self.Final_Output.drop([self.originData.columns[col]], axis =1)

        print("@@",originData_int.columns)

        origin = originData_int.values.tolist() 
        final = finalData_int.values.tolist() 

        print("origin len : ",len(origin))
        print("final len : ",len(final))

        befMoPlus_list = []
        befMo_sqrt = [] #최종 분모 리스트
        aftMoPlus_list = []
        aftMo_sqrt = [] #최종 분모 리스트
        Ja_list = [] #최종 분자 리스트
        usab = []
        usab_ave = 0

        for i in range(len(origin)):
            befMoPlus = 0
            aftMoPlus = 0
            Ja_val = 0

            for j in range(len(origin[0])):
                befMoPlus += pow(origin[i][j],2)
                aftMoPlus += pow(final[i][j],2)
                Ja_val += origin[i][j] * final[i][j]
                #print(bef_val[i][j], "*", aft_val[i][j], "=", bef_val[i][j] * aft_val[i][j])

            befMoPlus_list.append(befMoPlus)
            befMo_sqrt.append(math.sqrt(befMoPlus_list[i])) #sqrt : 제곱근
            aftMoPlus_list.append(aftMoPlus)
            aftMo_sqrt.append(math.sqrt(aftMoPlus_list[i])) #sqrt : 제곱근
            Ja_list.append(Ja_val)
            usab.append(Ja_list[i] / (befMo_sqrt[i] * aftMo_sqrt[i]))
            usab_ave += usab[i]

        print(usab)
        usab_ave = usab_ave / len(origin)
        print(str(usab_ave)+"%")

        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.usab_txt.setText("Usability : " + str(usab_ave)+"%")

        #tab2의 before table setItem
        BeforeDataModel = PandasModel(self.originData)
        self.ui.INPUTDATAtable.setModel(BeforeDataModel)

        AfterDataModel = PandasModel(self.Final_Output)
        self.ui.OUTPUTDATAtable.setModel(AfterDataModel)
        self.setGraph()
        #self.ui.tabWidget.setCurrentIndex(2) #탭 전환


    def InitializingGraphUI(self):
        self.before, _ = plt.subplots(figsize=(5,5)) #original code: self.before, self.ax1
        self.before_canvas = FigureCanvas(self.before) # figure - canvas 연동
        self.ui.inputGraph1.addWidget(self.before_canvas) #layout에 figure 삽입
        self.before_canvas.draw() 

        self.after, _ = plt.subplots(figsize=(5,5))
        self.after_canvas = FigureCanvas(self.after) # figure - canvas 연동
        self.ui.outputGraph1.addWidget(self.after_canvas) #layout에 figure 삽입
        self.after_canvas.draw() 


    def setGraph(self):
        #set graph
        graphcount = self.originData.copy()
        self.correlation_beforegraph(len(graphcount.columns), self.originData)
        self.max = 0
        list = []
        lenth = self.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        graphcount = graphcount.groupby(list).count()
        graphcount = 1 / graphcount
        print(graphcount[graphcount.columns[0]])
        self.risk_beforegraph(self.ui.inputGraph, graphcount[graphcount.columns[0]])
        

        graphcount = self.Final_Output.copy()
        self.correlation_aftergraph(len(graphcount.columns), graphcount)
        list = []
        lenth = self.ui.typeTable.rowCount() #컬럼개수
        for i in range(lenth): #준식별자 컬럼만 리스트에 삽입
            if(self.ui.typeTable.item(i,2).text() == '준식별자'):
                list.append(self.ui.typeTable.item(i, 0).text())

        graphcount = graphcount.groupby(list).count()
        graphcount = 1 / graphcount
        print(graphcount[graphcount.columns[0]])
        self.risk_aftergraph(self.ui.outputGraph, graphcount[graphcount.columns[0]], self.max.max())
        

    def correlation_beforegraph(self, columns, datas):
        self.ui.inputGraph1.removeWidget(self.before_canvas)
        self.before, _ = plt.subplots(figsize=(columns,columns))
        self.before_canvas = FigureCanvas(self.before) # figure - canvas 연동
        self.ui.inputGraph1.addWidget(self.before_canvas) #layout에 figure 삽입
        
        corr = datas.corr()
        colormap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(corr, cmap=colormap, annot=True, fmt=".2f")

        self.before_canvas.draw() 


    def correlation_aftergraph(self, columns, datas):
        self.ui.outputGraph1.removeWidget(self.after_canvas)
        self.after, _ = plt.subplots(figsize=(columns,columns))
        self.after_canvas = FigureCanvas(self.after) # figure - canvas 연동
        self.ui.outputGraph1.addWidget(self.after_canvas) #layout에 figure 삽입
        
        corr = datas.corr()
        colormap = sns.diverging_palette(220, 10, as_cmap=True)
        sns.heatmap(corr, cmap=colormap, annot=True, fmt=".2f")

        self.after_canvas.draw() 


    def risk_beforegraph(self, widget, data):
        """ reference: https://yapayzekalabs.blogspot.com/2018/11/pyqt5-gui-qt-designer-matplotlib.html tab2의 리스크 그래프 그리기"""
        widget.canvas.axes.clear()
        widget.canvas.axes.hist(data)
        widget.canvas.axes.set_title('Risk of Re-Identification')
        self.max, x, _ = widget.canvas.axes.hist(data)
        widget.canvas.draw()
    
    def risk_aftergraph(self, widget, data, max):
        """ reference: https://yapayzekalabs.blogspot.com/2018/11/pyqt5-gui-qt-designer-matplotlib.html tab2의 리스크 그래프 그리기"""
        widget.canvas.axes.clear()
        widget.canvas.axes.hist(data)
        widget.canvas.axes.set_title('Risk of Re-Identification')
        widget.canvas.axes.set_ylim([0, max])
        widget.canvas.draw()


    def SaveFileDialog(self):
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py);; CSV Files(*.csv);; Excel Files(*.xlsx)", 
                                                  "CSV Files(*.csv)",
                                                  options=options)
        if self.fileName:
            try:
                output = self.Final_Output.copy()
            except:
                output = self.deData.copy()

            print(output)
            output.to_csv(self.fileName, encoding='ms949', index=False)  

    def CloseWindow(self, event):
        close = QtWidgets.QMessageBox.question(self,
                                     "QUIT",
                                     "Are you sure want to exit process?",
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()



#nonidentifierMethod window
class NonIdentif(QMainWindow):
    """
    self.originData: 원본데이터
    self.deData: 비식별 데이터
    """

    def __init__(self, col=0, parent=None):
        super(NonIdentifierMethod, self).__init__(parent)
        self.SelectColumn = col
        self.SelectColumnName = mainwindow.originData.columns.values[col]
        self.InitUI()

    def InitUI(self):
        self.ui = uic.loadUi("./UI/SelectNonIdentifierMethod.ui") #insert your UI path
        self.ui.show()

        self.before = mainwindow.originData[mainwindow.originData.columns[self.SelectColumn]].to_frame() #pull one column and convert list
        self.rownum = len(self.before.index) # get row count
        self.colnum = len(self.before.columns) # get column count

        if(mainwindow.ui.typeTable.item(self.SelectColumn, 1).text() != 'int64'): #int64만 수치데이터 method 사용
            self.ui.Method5.setEnabled(False)
            self.ui.Method6.setEnabled(False)

        self.ui.nextButton.clicked.connect(self.NextButton) #비식별화 방식 선택(6개 중 택 1 가능)
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    #radio button event start 
    def NextButton(self):

        if(self.ui.Method1.isChecked()): #Swap UI 보여주기 및 데이터 rendering
            self.ui = uic.loadUi("./UI/Swap.ui") #insert your UI path
            self.ui.show()
            self.ui.ImportButton.hide()

            """유니크 값 추출 후 테이블에 저장"""
            uniqueIndex = self.before[self.SelectColumnName].unique().tolist()
            uniqueIndex.sort()

            self.ui.swapTable.setRowCount(len(uniqueIndex)) 
            self.ui.swapTable.setHorizontalHeaderLabels(['before', 'after'])

            for i in range(len(uniqueIndex)):
                self.ui.swapTable.setItem(i,0,QTableWidgetItem(str(uniqueIndex[i])))

            """선택한 컬럼의 데이터만 보여주기"""
            self.ui.compareTable.setRowCount(self.rownum)
            self.ui.compareTable.setHorizontalHeaderLabels([self.SelectColumnName, self.SelectColumnName])

            for j in range(self.rownum):
                self.ui.compareTable.setItem(j,0,QTableWidgetItem(str(self.before[self.SelectColumnName][j])))

            #self.ui.runButton.clicked.connect(self.Swap)
            self.ui.runButton.clicked.connect(lambda: self.Swap(uniqueIndex))
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("교환"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)

        elif(self.ui.Method2.isChecked()): # Shuffle UI 보여주기 및 데이터 rendering
            self.ui = uic.loadUi("./UI/Shuffle.ui") #insert your UI path
            self.ui.show()

            self.ui.BeforeData.setRowCount(self.rownum) #Set Column Count s    
            self.ui.BeforeData.setHorizontalHeaderLabels(list(self.before.columns))

            #for i in range(colnum):
            for j in range(self.rownum): #rendering data (inputtable of Tab1)
                self.ui.BeforeData.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Shuffle)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("재배열"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method3.isChecked()):
            self.ui = uic.loadUi("./UI/CategoricalData.ui") #insert your UI path
            self.ui.show()

            self.ui.nextButton.clicked.connect(self.Categorical_next)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method4.isChecked()): # 마스킹 및 삭제
            self.ui = uic.loadUi("./UI/maskingData.ui") #insert your UI path
            self.ui.show()

            self.m_level = self.ui.maskingText.textChanged.connect(self.usedbyMasking)
            self.m_index = self.ui.m_comboBox.currentIndexChanged.connect(self.usedbyMasking)

            self.before = mainwindow.originData[self.SelectColumnName].to_frame() #pull one column and convert list
            rownum = len(self.before.index) # get row count
            colnum = len(self.before.columns) # get column count

            self.ui.nextButton.clicked.connect(self.Masking)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method5.isChecked()): # 통계값 처리 UI 및 박스 그래프 보여주기
            self.ui = uic.loadUi("./UI/Aggregation.ui") #insert your UI path
            self.ui.show()
            self.RemoveFlag = False

            #Rendering before box plot start
            self.beforeFig = plt.Figure()
            self.beforeCanvas = FigureCanvas(self.beforeFig) # figure - canvas 연동
            self.ui.beforePlot.addWidget(self.beforeCanvas) #layout에 figure 삽입
            
            self.ax1 = self.beforeFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
            self.beforeCanvas.draw() 
            self.AggregationbeforeGraph(mainwindow.originData[self.SelectColumnName])
            #Rendering before box plot end

            #Rendering after box plot start
            self.afterFig = plt.Figure()
            self.afterCanvas = FigureCanvas(self.afterFig) # figure - canvas 연동
            self.ui.afterPlot.addWidget(self.afterCanvas) #layout에 figure 삽입

            self.ax2 = self.afterFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
            self.afterCanvas.draw() 
            #Rendering after box plot end

            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.AllPart.currentIndexChanged.connect(self.ComboBoxSetting)
            self.ui.columns.currentIndexChanged.connect(self.ColumnComboSetting)

            self.ui.runButton.clicked.connect(self.Outlier)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method6.isChecked()): # 라운딩 UI 및 before data 테이블 값 넣기
            self.ui = uic.loadUi("./UI/Rounding.ui") #insert your UI path
            self.ui.show()
            self.ui.randomLabel.hide()
            
            self.ui.BeforeData.setRowCount(self.rownum) #Set Column Count s 
            self.ui.BeforeData.setHorizontalHeaderLabels(list(self.before.columns))

            for j in range(self.rownum): #rendering data (inputtable of Tab1)
                self.ui.BeforeData.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Rounding)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("라운딩"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
    #radio button event end 

    def usedbyMasking(self):
        self.m_level = self.ui.maskingText.toPlainText()
        self.m_index = self.ui.m_comboBox.currentIndex()
        try:
            self.m_level = int(self.m_level)
            if(self.m_level<1):
                self.m_level/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass

    #data swap start
    def Swap(self, uniqueIndex):      
        """swapTable의 after 값으로 바꾸기"""
        self.after = self.before.copy()
        self.swap_list = []
        for i in range(len(uniqueIndex)):
            self.after.loc[self.after[self.SelectColumnName]==str(uniqueIndex[i]), self.SelectColumnName] = self.ui.swapTable.item(i,1).text()
            self.swap_list.append((str(uniqueIndex[i]) + "->" + self.ui.swapTable.item(i,1).text()))

        for j in range(self.rownum):
            self.ui.compareTable.setItem(j,1,QTableWidgetItem(str(self.after[self.SelectColumnName][j])))
    #data swap end

    #data shuffle(재배열) start          
    def Shuffle(self):
        self.shufflenumber = self.ui.shffleText.toPlainText()
        try:  #숫자만 입력, 그 외 값은 예외처리
            self.shufflenumber = int(self.shufflenumber)
            if(self.shufflenumber<1):
                self.shufflenumber/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass

        tempList = self.before[self.before.columns[0]].values.tolist()
        
        for i in range(self.shufflenumber): #shuffle 
    	    shuffle(tempList)

        self.ui.AfterData.setRowCount(self.rownum) #Set Column Count s   
        self.ui.AfterData.setHorizontalHeaderLabels(list(self.before.columns))
        
        for i in range(self.rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(tempList[i])))
        #self.after[self.SelectColumnName] = tempList
        self.after = DataFrame(data={self.SelectColumnName: tempList})
    #Shuffle() end

    def Categorical_next(self):

        if(self.ui.ordering.isChecked()):
            self.ui = uic.loadUi("./UI/ordering_categorical.ui")
            self.ui.show()
        
            self.original_uniq = self.before[self.SelectColumnName].unique()
            self.ui.original.setRowCount(len(self.original_uniq))
            self.ui.original.setHorizontalHeaderLabels(['values'])

            self.ui.categorical.setHorizontalHeaderLabels(['categorical'])
            self.ui.categorical.setRowCount(len(self.original_uniq))

            self.original_uniq = list(self.original_uniq)
            self.original_pop = self.original_uniq.copy()   # type: list
            self.groupEle = []
            self.str_groupEle = []
            self.a = 0

            for v in range(len(self.original_uniq)):
                self.ui.original.setItem(v,0,QTableWidgetItem(str(self.original_uniq[v])))
            
            self.ui.runButton.clicked.connect(self.Ordering_Categorical)
            self.ui.cancelButton.clicked.connect(self.ui.hide)

        elif(self.ui.intervals.isChecked()):
            self.ui = uic.loadUi("./UI/intervals_categorical.ui") #insert your UI path
            self.ui.show()

            self.ui.original.setRowCount(self.rownum) #Set Column Count s 
            self.ui.original.setHorizontalHeaderLabels(['original'])

            for j in range(self.rownum): #rendering data (inputtable of Tab1)
                self.ui.original.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.runButton.clicked.connect(self.Intervals_Categorical)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("연속 변수 범주화"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
    
    def Ordering_Categorical(self):
        orderValue = self.ui.orderText.toPlainText()
        UsrChckVal = orderValue.split(',')
        print(UsrChckVal)
        UsrChckVal = [int (i) for i in UsrChckVal] #배열 원소 int형으로 변환


        categoricalNum = len(self.original_pop) - len(UsrChckVal)
        groupEle_tmp = []
        
        try:
            if categoricalNum >= 0:
                for c in range(len(UsrChckVal)):
                    groupEle_tmp.append(self.original_uniq[UsrChckVal[c]-1])
                    self.original_pop.remove(groupEle_tmp[c])

                self.groupEle.append(groupEle_tmp)
                groupEle_tmp = str(groupEle_tmp)
                groupEle_tmp = groupEle_tmp.replace("'","")
                self.str_groupEle.append(groupEle_tmp)
                self.ui.categorical.setItem(self.a, 0, QTableWidgetItem(str(groupEle_tmp)))
                print(len(self.groupEle[self.a]))
                self.a = self.a + 1
            
        except ValueError:
            QtWidgets.QMessageBox.about(self, 'Error','이미 범주화 처리가 된 요소입니다.')
        pass
      
        self.ui.finishButton.clicked.connect(self.Ordering_Categorical_finish)

    def Ordering_Categorical_finish(self):
        self.after = self.before.copy()

        self.o_Categorical = []

        for b in range(self.a):
            for z in range(len(self.groupEle[b])):
                self.after.loc[self.after[self.SelectColumnName]==str((self.groupEle[b][z])), self.SelectColumnName] = str((self.str_groupEle[b]))
                for j in range(len(self.original_uniq)):
                    if self.original_uniq[j] == self.groupEle[b][z]:
                        self.o_Categorical.append(str(self.original_uniq[j]) + "  " + str(self.str_groupEle[b]))
        self.finishButton("순위 변수 범주화")

    def Intervals_Categorical(self):
        self.after = self.before.copy()

        self.i_Categorical = []

        self.ui.categorical.setRowCount(self.rownum) #Set Column Count s 
        self.ui.categorical.setHorizontalHeaderLabels(['categorical'])

        minValue = self.ui.minText.toPlainText()
        maxValue = self.ui.maxText.toPlainText()
        interValue = self.ui.interText.toPlainText()

        try:
            minValue = int(minValue)
            maxValue = int(maxValue)
            interValue = int(interValue)
            if(minValue<1):
                minValue/0
            elif(maxValue<1):
                maxValue/0
            elif(interValue<1):
                interValue/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
        pass
            
        for j in range(self.rownum):
            if self.before[self.before.columns[0]][j] < minValue:
                self.after[self.after.columns[0]][j] = "<" + str(minValue)
                self.i_Categorical.append(str(self.before[self.before.columns[0]][j]) + "  " + str(self.after[self.after.columns[0]][j]))
                self.ui.categorical.setItem(j,0,QTableWidgetItem(str(self.after[self.after.columns[0]][j])))
            elif self.before[self.before.columns[0]][j] >= maxValue:
                self.after[self.after.columns[0]][j] = ">= " + str(maxValue)
                self.i_Categorical.append(str(self.before[self.before.columns[0]][j]) + "  " + str(self.after[self.after.columns[0]][j]))
                self.ui.categorical.setItem(j,0,QTableWidgetItem(str(self.after[self.after.columns[0]][j])))
            else:
                ii = int((maxValue-minValue)/interValue)
                for i in range(ii):
                    if self.before[self.before.columns[0]][j]-minValue >= i*interValue and self.before[self.before.columns[0]][j]-minValue < (i+1)*interValue:
                        self.after[self.after.columns[0]][j] = "[" + str(minValue+i*interValue) + "," + str(minValue+(i+1)*interValue) + ")"
                        self.i_Categorical.append(str(self.before[self.before.columns[0]][j]) + "  " + str(self.after[self.after.columns[0]][j]))
                        self.ui.categorical.setItem(j,0,QTableWidgetItem(str(self.after[self.after.columns[0]][j])))
             
    def Masking(self):
        self.ui = uic.loadUi("./UI/maskingData_review.ui") #insert your UI path
        self.ui.show()
        self.ui.maskingLevel.setRowCount(self.rownum) #Set Column Count s    
        
        self.after = self.before.copy()

        before_uniq = self.before[self.before.columns[0]].unique()
        
        unique_len = []
        mask = []
        after_uniq = before_uniq.copy()

        for i in before_uniq:
            unique_len.append(len(i)-1)

        for j in range(self.rownum): #rendering data (inputtable of Tab1)
            for u in range(len(before_uniq)):
                if(self.m_index == 0): # * masking
                    if self.m_level > unique_len[u]:
                        t_lev = unique_len[u]+1
                        mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], "*"*t_lev))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                    else:
                        mask.append(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1], "*"*self.m_level))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(self.m_level-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                elif(self.m_index == 1): # 0 masking
                    if self.m_level > unique_len[u]:
                        t_lev = unique_len[u]+1
                        mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], "0"*t_lev))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                    else:
                        mask.append(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1], "0"*self.m_level))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(self.m_level-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                elif(self.m_index == 2): # remove
                    if self.m_level > unique_len[u]:
                        t_lev = unique_len[u]+1
                        mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], " "*t_lev))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
                    else:
                        mask.append(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(self.m_level-1):unique_len[u]+1], " "*self.m_level))
                        after_uniq[u] = after_uniq[u][0:unique_len[u]-(self.m_level-1)]
                        after_uniq[u] = after_uniq[u]+mask[u]
                        if self.before[self.before.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                            self.after[self.after.columns[0]][j] = str(self.after[self.after.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
            
            self.ui.maskingLevel.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))
            self.ui.maskingLevel.setItem(j,1,QTableWidgetItem((self.after[self.after.columns[0]][j])))        

        
        #self.ui.backButton.clicked.connect(self.ui.hide)
        self.ui.finishButton.clicked.connect(lambda: self.finishButton("마스킹"))
        self.ui.cancelButton.clicked.connect(self.ui.hide)

    #data Rounding start
    def Rounding(self):
        number = self.ui.roundText.toPlainText()
        try: #숫자만 입력, 그 외 값은 예외처리
            number = int(number)
            if(number<1):
                number/0
        except Exception:
            QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number and bigger than 0')
        pass

        self.RoundingLevel = ""
        index = self.ui.comboBox.currentIndex()
        self.after = self.before.copy()

        if(index == 0):# 올림
            self.ui.randomLabel.hide()
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ", 올림"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = ((self.after.loc[i, self.SelectColumnName]+9*pow(10, number-1))//pow(10, number))*pow(10, number) # change number, up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+9*10^n-1)//10^n)*10^n # change number, up
        elif(index == 1):#내림
            self.ui.randomLabel.hide()
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ",내림"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = (self.after.loc[i, self.SelectColumnName]//pow(10, number))*pow(10, number) # change number, down
                #after.loc[i, SelectColumnName] = (after.loc[i, SelectColumnName]//10^n-1)*10^n # change number, down
        elif(index == 2):#5를 기준으로 up down, 반올림
            self.ui.randomLabel.hide()
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ", 반올림"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = ((self.after.loc[i, self.SelectColumnName]+5*pow(10, number-1))//pow(10, number))*pow(10, number) # change number, 4down, 5up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+5)//10)*10 # change number, 4down, 5up
        elif(index == 3): #random 값을 기준으로 up down
            randomN = random.randint(0,9)
            self.ui.randomLabel.show() #show random value label
            self.ui.randomLabel.setText("Value: " + str(randomN)) #랜덤 값 보여주기
            self.RoundingLevel = self.RoundingLevel + str(pow(10, number-1)) + ", 랜덤(" + str(randomN) + ")"
            for i in range(self.rownum):
                self.after.loc[i, self.SelectColumnName] = ((self.after.loc[i, self.SelectColumnName]+(10-randomN))//pow(10, number))*pow(10, number) # change number, 4down, 5up
                #after.loc[i, SelectColumnName] = ((after.loc[i, SelectColumnName]+(10-randomN))//10^n-1)*10^n # change number, 4down, 5up
            
        #rendering aftetable
        self.ui.AfterData.setRowCount(self.rownum) #Set Column Count     
        self.ui.AfterData.setHorizontalHeaderLabels(list(self.after.columns))

        for i in range(self.rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(self.after[self.after.columns[0]][i])))
    
    """if(DataFromTable[SelectColumnName].dtype == np.float64):
            DataFromTable[SelectColumnName] = round(DataFromTable[SelectColumnName],1) # change number 4down, 5up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.ceil) # up
            #DataFromTable[SelectColumnName] = DataFromTable[SelectColumnName].apply(np.floor) # down""" #float 처리, 지금 비사용        
    #data Rounding end

    #통계값 aggregation start
    def Outlier(self):
        self.after = self.before.copy() 
        self.AggregationLevel = ""

        #reference: https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame/31502974#31502974
        q1 = self.after[self.SelectColumnName].quantile(0.25) #calculate q1
        q3 = self.after[self.SelectColumnName].quantile(0.75) #calculate q3
        iqr = q3-q1 #Interquartile range
        fence_low  = q1-1.5*iqr 
        fence_high = q3+1.5*iqr

        #change 4분위수
        index = self.ui.AllPart.currentIndex()
        
        normal = self.after.loc[(self.after[self.SelectColumnName] >= fence_low) & (self.after[self.SelectColumnName] <= fence_high)] #select not outlier data(normal data)
        
        if index == 0:
            self.after = self.AllAggregation(self.after) #모든 값을 총계나 평균으로 변경            
            self.AggregationafterGraph(self.after[self.SelectColumnName]) #Rendering after box plot
            self.AggregationLevel = self.AggregationLevel + "ALL(" + str(self.ui.function.currentText()) + ")"
        elif index == 1:
            self.after = self.partAggregation(normal, self.after, fence_low, fence_high)  #이상치 값만 처리
            self.AggregationafterGraph(self.after[self.SelectColumnName]) #Rendering after box plot
            self.AggregationLevel = self.AggregationLevel + "PART(" + str(self.ui.function.currentText()) + ")"
        elif index == 2:
            self.after = mainwindow.originData.copy() 
            self.after = self.partGroupAggregation(self.after)
            base = str(self.ui.columns.currentText())
            self.AggregationafterGraph(self.after.groupby(base)[self.SelectColumnName].apply(list))
            self.AggregationLevel = (self.AggregationLevel + "GROUP(" + 
                                    str(self.ui.function.currentText()) + "), " +
                                    str(self.ui.group.currentText()) +
                                    " of " +
                                    str(self.ui.columns.currentText()))

            

        """ float로 변경될 경우, 반올림 후 int로 재변환"""
        self.after[self.SelectColumnName]=round(self.after[self.SelectColumnName],0)
        self.after[self.SelectColumnName] = self.after[self.SelectColumnName].astype(int)

        if(self.RemoveFlag == True):
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("통계 처리 삭제"))
        else:
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("통계 처리"))
    #통계값 aggregation end

    #aggregation ui에 있는 comboBox에 값 넣기
    def ComboBoxSetting(self, index):
        if index == 0: #한 컬럼만 처리 + 모두 하나의 값으로 통일
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("총합")
            self.ui.function.addItem("평균값")
            self.AggregationbeforeGraph(mainwindow.originData[self.SelectColumnName])
        elif index == 1: #한 컬럼만 처리 + 이상치만 처리
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("평균값")
            self.ui.function.addItem("최대값")
            self.ui.function.addItem("최소값")
            self.ui.function.addItem("중앙값")
            self.ui.function.addItem("최빈값")
            self.ui.function.addItem("삭제")
            self.AggregationbeforeGraph(mainwindow.originData[self.SelectColumnName])
        elif index == 2: #한 컬럼에서 일부만 처리 + 이상치만 처리
            self.ui.function.clear() 
            self.ui.function.addItem("평균값")
            self.ui.function.addItem("중앙값")
            self.ui.function.addItem("최빈값")
            self.ui.function.addItem("삭제")
            
            self.ui.columns.show() #컬럼 이름 넣기(현재 선택한 컬럼 제외)
            self.ui.columns.clear()
            for i in mainwindow.originData.columns:
                if i != self.SelectColumnName:
                    self.ui.columns.addItem(i)

            self.ui.group.show()
            self.ui.group.clear() #선택한 컬럼에 유니크한 값만 뽑아서 comboBox에 추가
            array = mainwindow.originData[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))


    def ColumnComboSetting(self): # 컬럼별(그룹)일 때 group combobox 세팅
        base = str(self.ui.columns.currentText())
        if base:
            self.AggregationbeforeGraph(mainwindow.originData.sort_values([self.SelectColumnName]).groupby(base)[self.SelectColumnName].apply(list))

            self.ui.group.show()
            self.ui.group.clear() #선택한 컬럼에 유니크한 값만 뽑아서 comboBox에 추가
            array = mainwindow.originData[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))


    #모든 값을 총계나 평균으로 변경
    def AllAggregation(self, Outlier):
        self.RemoveFlag = False
        index = self.ui.function.currentIndex() 
        if index == 0: #총합으로 통일
            Outlier[self.SelectColumnName] = Outlier[self.SelectColumnName].sum()
        elif index == 1: #평균으로 통일
            Outlier[self.SelectColumnName] = Outlier[self.SelectColumnName].mean()
        return Outlier

    #이상치 값만 처리
    def partAggregation(self, Normal, Outlier, low, high):
        index = self.ui.function.currentIndex() 
        if index == 0: #MEAN
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].mean()
        elif index == 1: #MAX
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].max()
        elif index == 2: #MIN
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].min()
        elif index == 3: #MEDIAN
            self.RemoveFlag = False
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = Normal[self.SelectColumnName].median()
        elif index == 4: #MODE
            self.RemoveFlag = False
            mode = Normal[self.SelectColumnName].value_counts().idxmax() #최빈값
            Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)] = mode
        elif index == 5: #REMOVE
            self.RemoveFlag = True
            b_length = len(Outlier.index)
            Outlier = Outlier.loc[(Outlier[self.SelectColumnName] >= low) & (Outlier[self.SelectColumnName] <= high)]
            self.RemoveRowCount = b_length - len(Outlier.index)
        return Outlier

    #그룹화 후 이상치 값 선별 및 처리
    def partGroupAggregation(self, result):
        groupcol = str(self.ui.columns.currentText()) #그룹 기준 컬럼
        groupvalue = str(self.ui.group.currentText())   #그룹 기준 값

        Outlier = mainwindow.originData[mainwindow.originData[groupcol].isin([groupvalue])]
        
        q1 = Outlier[self.SelectColumnName].quantile(0.25) #calculate q1
        q3 = Outlier[self.SelectColumnName].quantile(0.75) #calculate q3
        iqr = q3-q1 #Interquartile range
        low  = q1-1.5*iqr 
        high = q3+1.5*iqr

        list = []
        Normal = Outlier.loc[(Outlier[self.SelectColumnName] >= low) & (Outlier[self.SelectColumnName] <= high)] #select normal data  
        Outlier = Outlier.loc[(Outlier[self.SelectColumnName] < low) | (Outlier[self.SelectColumnName] > high)]
        for row in Outlier.index: 
            list.append(row)

        index = self.ui.function.currentIndex() 
        if index == 0: #MEAN    
            self.RemoveFlag = False
            for i in range(len(list)):
                result[self.SelectColumnName][list[i]] = Normal[self.SelectColumnName].mean()
        elif index == 1: #MEDIAN
            self.RemoveFlag = False
            for i in range(len(list)):
                result[self.SelectColumnName][list[i]] =  Normal[self.SelectColumnName].median()
        elif index == 2: #MODE
            self.RemoveFlag = False
            for i in range(len(list)):
                mode = Normal[self.SelectColumnName].value_counts().idxmax() #최빈값
                result[self.SelectColumnName][list[i]] =  mode
        elif index == 3: #REMOVE
            self.RemoveFlag = True
            self.RemoveRowCount = len(list)
            for i in range(len(list)):
                result = result.drop(result.index[list[i]])
        return result   

    def AggregationbeforeGraph(self, data):
        self.beforeFig.clear()
        self.ax1 = self.beforeFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
        self.ax1.boxplot(data)
        self.ax1.grid()
        self.beforeCanvas.draw() 

    def AggregationafterGraph(self, data):
        self.afterFig.clear() #canvas clear
        self.ax2 = self.afterFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
        self.ax2.boxplot(data)
        self.ax2.grid()
        self.afterCanvas.draw() 

    #데이터 mainwindow.deData 및 methodTable 저장 및 UI 끄기
    def finishButton(self, methodname):
        #global mainwindow.deData, mainwindow.originData

        mainwindow.deData[self.SelectColumnName] = self.after[self.SelectColumnName] #change values
        self.ui.hide()
        
        if(methodname == "통계 처리 삭제"):
            changednumber = self.RemoveRowCount
            mainwindow.deData = mainwindow.deData.dropna(subset=[mainwindow.deData.columns[self.SelectColumn]]) #통계값에서 생기는 null 삭제 작업 필요
            mainwindow.deData = mainwindow.deData.reset_index(drop=True)
        else:
            changednumber = self.calculateCahngeValue(self.before, self.after, self.SelectColumnName)
        
        print(mainwindow.deData)

        #methodTable에 이미 비식별 메소드가 있다면 삭제
        if(self.SelectColumnName in mainwindow.methodCol_List):
            print("this is duplicated check")
            mainwindow.ui.methodTable.removeRow(int(mainwindow.methodCol_List[self.SelectColumnName])) #컬럼이 저장된 행 삭제
            for key, value in mainwindow.methodCol_List.items():
                if value > mainwindow.methodCol_List[self.SelectColumnName]:
                    mainwindow.methodCol_List[key] -= 1
            del mainwindow.methodCol_List[self.SelectColumnName]  #딕셔너리에서 컬럼 삭제


        if(methodname == "교환"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.swap_list, changednumber)
        elif(methodname == "재배열"):
            self.methodTable_Level(self.SelectColumnName, methodname,  ("Suffled " + str(self.shufflenumber)), changednumber)
        elif(methodname == "연속 변수 범주화"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.i_Categorical, changednumber)
        elif(methodname == "순위 변수 범주화"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.o_Categorical, changednumber)
        elif(methodname == "마스킹"): 
            self.methodTable_Level(self.SelectColumnName, methodname, ("level " + str(self.m_level)), changednumber)
        elif(methodname == "통계 처리"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.AggregationLevel, changednumber)
        elif(methodname == "통계 처리 삭제"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.AggregationLevel, changednumber)
        elif (methodname == "라운딩"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.RoundingLevel, changednumber)

        mainwindow.methodCol_List[self.SelectColumnName]  = mainwindow.ui.methodTable.rowCount()-1 #컬럼이 저장된 행 저장  
        print(mainwindow.methodCol_List)


    def methodTable_Level(self, colName, method, level, changeNumber):
        mainwindow.ui.methodTable.insertRow(mainwindow.ui.methodTable.rowCount())
        mainwindow.ui.methodTable.setItem(mainwindow.ui.methodTable.rowCount()-1, 0, QTableWidgetItem(str(colName))) #column name
        mainwindow.ui.methodTable.setItem(mainwindow.ui.methodTable.rowCount()-1, 1, QTableWidgetItem(str(method))) #비식별 method
        mainwindow.ui.methodTable.setItem(mainwindow.ui.methodTable.rowCount()-1, 2, QTableWidgetItem(str(level))) #detail
        mainwindow.ui.methodTable.setItem(mainwindow.ui.methodTable.rowCount()-1, 3, QTableWidgetItem(str(changeNumber))) #영향받은 row 수 
 

    def methodTable_Box(self, colName, method, level_list, changeNumber):
        levelcom = QComboBox() 
        levelcom.addItems(level_list)

        mainwindow.ui.methodTable.insertRow(mainwindow.ui.methodTable.rowCount())
        mainwindow.ui.methodTable.setItem(mainwindow.ui.methodTable.rowCount()-1, 0, QTableWidgetItem(str(colName))) #column name
        mainwindow.ui.methodTable.setItem(mainwindow.ui.methodTable.rowCount()-1, 1, QTableWidgetItem(str(method))) #비식별 method
        mainwindow.ui.methodTable.setCellWidget(mainwindow.ui.methodTable.rowCount()-1, 2, levelcom)
        mainwindow.ui.methodTable.setItem(mainwindow.ui.methodTable.rowCount()-1, 3, QTableWidgetItem(str(changeNumber))) #영향받은 row 수

    def calculateCahngeValue(self, beforedata, afterdata, colname):
        df = beforedata[colname] != afterdata[colname]
        return (df == True).sum()  




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWidget()
    sys.exit(app.exec_())
