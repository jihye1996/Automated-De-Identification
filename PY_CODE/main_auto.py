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
from itertools import product
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
        deData = self.originData.copy()
        result = list(product(*self.ApplyMethod.values()))
        print(result)
        """
        self.privacy = PrivacyModel(self)
        self.Final_Output = deData.copy() #비식별화만 된 데이트를 프라이버시 모델에 입력

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

        """

        """
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

        """


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWidget()
    sys.exit(app.exec_())
