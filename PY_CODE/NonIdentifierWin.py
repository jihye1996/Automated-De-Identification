#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import pandas as pd
import numpy as np
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
plt.rc('font', family='Malgun Gothic') #한글 깨짐 방지
plt.rc('axes', unicode_minus=False) #한글 깨짐 방지

#to import UI path
sys.path.append("./UI") # insert your path
sys.path.append("./PY_CODE")


import DeIdentifier

"""
TYPE: 0이면 정수, 아니면 정수
if(mainWin.ui.typeTable.item(self.SelectColumn, 1).text() != 'int64'): #int64만 수치데이터 method 사용

"""
class NonIdentifierWin(QMainWindow):
    def __init__(self, mainWindow, dataframe, type):
        super().__init__()
        self.mainWin = mainWindow
        self.before = dataframe.copy()
        self.type = type
        self.InitUI()

    
    def InitUI(self):
        self.ui = uic.loadUi("./UI/SelectNonIdentifierMethod.ui") #insert your UI path
        print("NonIdentifierWin.py Select UI")
        self.ui.show()

        
        self.rownum = len(self.before.index) # get row count
        self.colnum = len(self.before.columns) # get column count

        self.SelectColumnName = self.before.columns.values[0]

        if(self.type==1):
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
            uniqueIndex = self.before[self.before.columns[0]].unique().tolist()
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

            self.ui.runButton.clicked.connect(lambda: self.Swap(uniqueIndex))
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("swap"))
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
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("shuffle"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method3.isChecked()):
            self.ui = uic.loadUi("./UI/CategoricalData.ui") #insert your UI path
            self.ui.show()

            self.ui.nextButton.clicked.connect(self.Categorical_next)
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method4.isChecked()): # 마스킹 및 삭제
            self.ui = uic.loadUi("./UI/masking.ui") #insert your UI path
            self.ui.show()

            self.ui.afterTable.setRowCount(self.rownum) #Set Column Count s    
            
            for j in range(self.rownum): #rendering data 
                self.ui.afterTable.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.addButton.clicked.connect(lambda: self.addLevel("masking", self.ui.LevelTable))
            self.ui.delButton.clicked.connect(lambda: self.delLevel(self.ui.LevelTable))
            self.ui.runButton.clicked.connect(self.Masking)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("마스킹"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method5.isChecked()): # 통계값 처리 UI 및 박스 그래프 보여주기
            self.ui = uic.loadUi("./UI/Aggregation.ui") #insert your UI path
            self.ui.show()

            #Rendering before box plot start
            self.beforeFig = plt.Figure()
            self.beforeCanvas = FigureCanvas(self.beforeFig) # figure - canvas 연동
            self.ui.beforePlot.addWidget(self.beforeCanvas) #layout에 figure 삽입
            
            self.ax1 = self.beforeFig.add_subplot(1, 1, 1)  # fig를 1행 1칸으로 나누어 1칸안에 넣기
            self.beforeCanvas.draw() 
            self.AggregationbeforeGraph(self.before[self.before.columns[0]])
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
            #self.ui.columns.currentIndexChanged.connect(self.ColumnComboSetting) #don't use anymore, but don't remove

            self.ui.runButton.clicked.connect(self.Aggregation)
            self.ui.addButton.clicked.connect(self.AggregationAdd)
            self.ui.delButton.clicked.connect(lambda: self.delLevel(self.ui.LevelTable))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
        
        elif(self.ui.Method6.isChecked()): # 라운딩 UI 및 before data 테이블 값 넣기
            self.ui = uic.loadUi("./UI/Rounding.ui") #insert your UI path
            self.ui.show()
            
            self.ui.afterTable.setRowCount(self.rownum) #Set Column Count s

            for j in range(self.rownum): #rendering data 
                self.ui.afterTable.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.addButton.clicked.connect(lambda: self.addLevel("rounding", self.ui.LevelTable))
            self.ui.delButton.clicked.connect(lambda: self.delLevel(self.ui.LevelTable))
            self.ui.runButton.clicked.connect(self.Rounding)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("rounding"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
            self.ui.backButton.clicked.connect(self.InitUI)
    #radio button event end 


    #data swap start
    def Swap(self, uniqueIndex):      
        """swapTable의 after 값으로 바꾸기"""
        self.after = self.before.copy()
        self.swap_list = []
        self.swap_values = []
        for i in range(len(uniqueIndex)):
            self.swap_values.append(self.ui.swapTable.item(i,1).text())
            self.after.loc[self.after[self.after.columns[0]]==uniqueIndex[i], self.after.columns[0]] = self.swap_values[i] 
            self.swap_list.append((str(uniqueIndex[i]) + "->" + (str(self.swap_values[i]))))

        for j in range(self.rownum):
            self.ui.compareTable.setItem(j,0,QTableWidgetItem(str(self.before[self.SelectColumnName][j])))
            self.ui.compareTable.setItem(j,1,QTableWidgetItem(str(self.after[self.SelectColumnName][j])))
        
        del self.after
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

        self.after = self.before.copy()

        for _ in range(self.shufflenumber):
            self.after[self.after.columns[0]] = np.random.permutation(self.after[self.after.columns[0]].values)


        self.ui.AfterData.setRowCount(self.rownum) #Set Column Count s   
        self.ui.AfterData.setHorizontalHeaderLabels(list(self.before.columns))
        
        for i in range(self.rownum): #rendering data
            self.ui.AfterData.setItem(i,0,QTableWidgetItem(str(self.after[self.SelectColumnName][i])))
        
        del self.after
    #Shuffle() end

    """마스킹, 범주화"""
    def Categorical_next(self):

        if(self.ui.ordering.isChecked()):
            self.ui = uic.loadUi("./UI/ordering_categorical.ui")
            self.ui.show()
        
            self.original_uniq = self.before[self.SelectColumnName].unique()
            self.ui.original.setRowCount(len(self.original_uniq))
            self.ui.original.setHorizontalHeaderLabels(['values'])

            self.ui.categorical.setHorizontalHeaderLabels(['categorical'])
            self.original_uniq = list(self.original_uniq)
              
            for v in range(len(self.original_uniq)):
                self.ui.original.setItem(v,0,QTableWidgetItem(str(self.original_uniq[v])))
            
            self.ui.runButton.clicked.connect(self.Ordering_Categorical)
            self.ui.cancelButton.clicked.connect(self.ui.hide)

        elif(self.ui.intervals.isChecked()):
            self.ui = uic.loadUi("./UI/intervals_categorical.ui") #insert your UI path
            self.ui.show()

            self.maxV = self.before[self.before.columns[0]].max()
            #self.paddingmax = ((maxV+9*pow(10, len(str(maxV))-1))//pow(10, len(str(maxV))))*pow(10, len(str(maxV)))

            self.i_catGraph(self.ui.i_catGraph, self.before[self.before.columns[0]], self.maxV)
            """
            self.ui.original.setRowCount(self.rownum) #Set Column Count s 
            self.ui.original.setHorizontalHeaderLabels(['original'])

            for j in range(self.rownum): #rendering data (inputtable of Tab1)
                self.ui.original.setItem(j,0,QTableWidgetItem(str(self.before[self.before.columns[0]][j])))

            self.ui.categorical.setRowCount(self.rownum) #Set Column Count s 
            self.ui.categorical.setHorizontalHeaderLabels(['categorical'])
            """
            self.ui.runButton.clicked.connect(self.Intervals_Categorical)
            self.ui.finishButton.clicked.connect(lambda: self.finishButton("연속 변수 범주화"))
            self.ui.cancelButton.clicked.connect(self.ui.hide)
    
    def Ordering_Categorical(self):
        self.groupValue = int(self.ui.orderText.toPlainText()) 

        self.after = self.before.copy()
        self.groupCat_str = DeIdentifier.O_Categorical(self.after, self.groupValue)
        self.after = self.groupCat_str[0]
        self.groupCat = self.groupCat_str[1]
        self.groupCat_str = self.groupCat_str[2]

        self.ui.categorical.setRowCount(len(self.groupCat_str))

        for cat in range(len(self.groupCat_str)):
            self.ui.categorical.setItem(cat, 0, QTableWidgetItem(self.groupCat_str[cat]))

        self.ui.finishButton.clicked.connect(self.Ordering_Categorical_finish)

    def Ordering_Categorical_finish(self):
        self.o_Categorical = []

        for i in range(len(self.original_uniq)):
            for idx, cat in enumerate(self.groupCat):
                for j in range(len(cat)):
                    if self.original_uniq[i] == cat[j]:
                        self.o_Categorical.append(str(self.original_uniq[i]) + " -> " + str(self.groupCat_str[idx]))
        
        self.finishButton("순위 변수 범주화")

    def Intervals_Categorical(self):
        #i_num = self.ui.original.rowCount()

        self.minVal = self.ui.minText.toPlainText()
        self.maxVal = self.ui.maxText.toPlainText()
        self.gapVal = self.ui.interText.toPlainText()

        self.after = self.before.copy()
        self.after = DeIdentifier.I_Categorical(self.after, self.minVal, self.maxVal, self.gapVal)
    
    def i_catGraph(self, widget, data, maxVal):
        
        widget.canvas.axes.clear()
        widget.canvas.axes.hist(data, bins=50, rwidth=0.9, color='gray')
        widget.canvas.axes.set_xlim([0, maxVal])
        widget.canvas.axes.set_xlabel([self.SelectColumnName])
        widget.canvas.draw()

    def Masking(self):
        m_row = self.ui.LevelTable.rowCount()
        self.m_list = []
        for row in range(m_row):
            param_list = []
            for col in range(self.ui.LevelTable.columnCount()):
                table_item = self.ui.LevelTable.item(row,col)
                if col == 0 and isinstance(self.ui.LevelTable.cellWidget(row, 0), QComboBox):
                    current_value = self.ui.LevelTable.cellWidget(row, 0).currentText()
                    param_list.append(current_value)
                else:
                    param_list.append('' if table_item is None else str(table_item.text()))
            self.m_list.append(param_list)
            print("m_list",self.m_list)
            del param_list

        #rendering aftetable 
        self.mask_list = ["원본"]
        self.ui.afterTable.setColumnCount(row+2)   
        for i in range(row+1): #rendering data
            self.after = self.before.copy()
            self.after = DeIdentifier.Masking(self.after, self.m_list[i][0], int(self.m_list[i][1]))[0]  # dataframe, m_index, m_level
            for j in range(self.rownum):
                self.ui.afterTable.setItem(j,i+1,QTableWidgetItem(str(self.after[self.after.columns[0]][j]))) #행, 컬럼
            self.mask_list.append(self.m_list[i][0] + ", level"+ (self.m_list[i][1]))
        self.ui.afterTable.setHorizontalHeaderLabels(self.mask_list)
        self.ui.compareTab.setCurrentIndex(1)
        del self.after
        
    """마스킹, 범주화 끝"""

    #통계값 aggregation start
    def Aggregation(self):
        self.after = self.before.copy() 
        self.AggregationLevel = ""

        #통계처리 방법 선택
        index = self.ui.AllPart.currentText() #대체 범위 선택
        method = self.ui.function.currentText() #대체 방법 선택
        self.after = DeIdentifier.Aggregation(self.after, index, method) #실제 데이터 연산 함수
        self.AggregationafterGraph(self.after[self.after.columns[0]]) #Rendering after box plot
        self.ui.finishButton.clicked.connect(lambda: self.finishButton("aggregation"))
        """
        현재 미사용
        elif index == 2:
            self.after = self.mainWin.originData.copy() 
            self.after = self.partGroupAggregation(self.after)
            base = str(self.ui.columns.currentText())
            self.AggregationafterGraph(self.after.groupby(base)[self.SelectColumnName].apply(list))
            self.AggregationLevel = (self.AggregationLevel + "GROUP(" + 
                                    str(self.ui.function.currentText()) + "), " +
                                    str(self.ui.group.currentText()) +
                                    " of " +
                                    str(self.ui.columns.currentText()))
        """
    #통계값 aggregation end

        
    """
    aggregation ui에 있는 comboBox에 값 넣기
    ComboBoxSetting: AllPart ui combobox setting(All, Unique, group)
    ColumnComboSetting: Allpart가 group일 경우 combobox setting
    """
    def ComboBoxSetting(self, index):
        self.afterFig.clear() #canvas clear
        if index == 0: #한 컬럼만 처리 + 모두 하나의 값으로 통일
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("총합")
            self.ui.function.addItem("평균")
            self.AggregationbeforeGraph(self.before[self.before.columns[0]])
        elif index == 1: #한 컬럼만 처리 + 이상치만 처리
            self.ui.columns.hide()
            self.ui.group.hide()
            self.ui.function.clear() 
            self.ui.function.addItem("평균")
            self.ui.function.addItem("최대")
            self.ui.function.addItem("최소")
            self.ui.function.addItem("중앙")
            self.ui.function.addItem("최빈")
            self.ui.function.addItem("삭제")
            self.AggregationbeforeGraph(self.before[self.before.columns[0]])
        """
        현재 미사용
        elif index == 2: #한 컬럼에서 일부만 처리 + 이상치만 처리
            self.ui.group.show()
            self.ui.group.clear() #선택한 컬럼에 유니크한 값만 뽑아서 comboBox에 추가
            self.ui.function.clear() 
            self.ui.function.addItem("평균값")
            self.ui.function.addItem("중앙값")
            self.ui.function.addItem("최빈값")
            self.ui.function.addItem("삭제")
            
            self.ui.columns.clear()
            self.ui.columns.show() #컬럼 이름 넣기(현재 선택한 컬럼 제외)
            for i in self.mainWin.originData.columns:
                if i != self.SelectColumnName:
                    self.ui.columns.addItem(i)

            array = self.mainWin.originData[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))
        
    def ColumnComboSetting(self): # 컬럼별(그룹)일 때 group combobox 세팅
        base = str(self.ui.columns.currentText())
        if base:
            self.AggregationbeforeGraph(self.mainWin.originData.sort_values([self.SelectColumnName]).groupby(base)[self.SelectColumnName].apply(list))
            array = self.mainWin.originData[str(self.ui.columns.currentText())].unique()
            array.sort()
            for i in range(len(array)):
                self.ui.group.addItem(str(array[i]))
    """
    def AggregationAdd(self):
        index = self.ui.AllPart.currentText() #대체 범위 선택
        method = self.ui.function.currentText() #대체 방법 선택
        rowPosition = self.ui.LevelTable.rowCount()
        self.ui.LevelTable.insertRow(rowPosition)
        self.ui.LevelTable.setItem(rowPosition, 0, QTableWidgetItem(index))
        self.ui.LevelTable.setItem(rowPosition, 1, QTableWidgetItem(method))

    #AggregationbeforeGraph&AggregationafterGraph: show graph
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

    #data Rounding start
    def Rounding(self):
        print("NonIdentifierWin.py Rounding")
        row = self.ui.LevelTable.rowCount()
        self.r_list = []
        for row in range(row):
            param_list = []
            for col in range(self.ui.LevelTable.columnCount()):
                table_item = self.ui.LevelTable.item(row,col)
                print("NonIdentifierWin.py table_item:",table_item)
                if col == 0 and isinstance(self.ui.LevelTable.cellWidget(row, 0), QComboBox):
                    current_value = self.ui.LevelTable.cellWidget(row, 0).currentText()
                    param_list.append(current_value)
                else:
                    param_list.append('' if table_item is None else str(table_item.text()))
            self.r_list.append(param_list)
            print("r_list",self.r_list)
            del param_list

        #rendering aftetable 
        self.round_list = ["원본"]
        self.ui.afterTable.setColumnCount(row+2)   
        for i in range(row+1): #rendering data
            self.after = self.before.copy()
            self.after = DeIdentifier.Rounding(self.after, self.r_list[i][0], int(self.r_list[i][1]))  # dataframe, r_index, r_level, randomN=0
            for j in range(self.rownum):
                self.ui.afterTable.setItem(j,i+1,QTableWidgetItem(str(self.after[self.after.columns[0]][j]))) #행, 컬럼
            self.round_list.append(self.r_list[i][0] + "level"+ (self.r_list[i][1]))
        self.ui.afterTable.setHorizontalHeaderLabels(self.round_list)
        self.ui.compareTab.setCurrentIndex(1)
        del self.after
    #data Rounding end

    def addLevel(self, method, table): #add 버튼 누르면 원하는 메소드 방법 세부 설정 가능
        if(method == "rounding"):
            privacy_list = ["올림", "내림", "반올림"]
            table.insertRow(table.rowCount())
            self.addCombo = QComboBox() 
            self.addCombo.addItems(privacy_list)
            table.setCellWidget(table.rowCount()-1, 0, self.addCombo)

        elif(method == "masking"):
            privacy_list = ["*(front)", "*(back)", "0(front)", "0(back)", "( )(front)", "( )(back)"]
            table.insertRow(table.rowCount())
            self.addCombo = QComboBox() 
            self.addCombo.addItems(privacy_list)
            table.setCellWidget(table.rowCount()-1, 0, self.addCombo)

    def delLevel(self, table):
        table.removeRow(table.currentRow())


    #데이터 self.mainWin.deData 및 methodTable 저장 및 UI 끄기
    def finishButton(self, methodname):

        #methodTable에 이미 비식별 메소드가 있다면 삭제
        if(self.SelectColumnName in self.mainWin.methodCol_List):
            print("this is duplicated check")
            self.mainWin.ui.methodTable.removeRow(int(self.mainWin.methodCol_List[self.SelectColumnName])) #컬럼이 저장된 행 삭제
            for key, value in self.mainWin.methodCol_List.items():
                if value > self.mainWin.methodCol_List[self.SelectColumnName]:
                    self.mainWin.methodCol_List[key] -= 1
            del self.mainWin.methodCol_List[self.SelectColumnName]  #딕셔너리에서 컬럼 삭제


        if(methodname == "swap"):
            self.mainWin.ApplyMethod[self.SelectColumnName] = [[self.SelectColumnName, "swap", 0], [self.SelectColumnName, "swap", self.swap_values]]
            self.methodTable_Box(self.SelectColumnName, methodname, self.swap_list)
            del self.swap_list
            del self.swap_values
        elif(methodname == "shuffle"):
            self.mainWin.ApplyMethod[self.SelectColumnName] = [[self.SelectColumnName, "shuffle", 0], [self.SelectColumnName, "shuffle", self.shufflenumber]]
            self.methodTable_Level(self.SelectColumnName, methodname,  ("Suffled " + str(self.shufflenumber)),)
            del self.shufflenumber
        elif(methodname == "연속 변수 범주화"):
            self.mainWin.ApplyMethod[self.SelectColumnName] = [[self.SelectColumnName, "i_Categorical", 0], [self.SelectColumnName, "i_Categorical", self.minVal, self.maxVal, self.gapVal]]
            self.methodTable_Level(self.SelectColumnName, methodname, ("최소 : " + str(self.minVal) + ", 최대 : " + str(self.maxVal) + ", 간격 : " + str(self.gapVal)))
            del self.minVal
            del self.maxVal
            del self.gapVal
        elif(methodname == "순위 변수 범주화"):
            self.mainWin.ApplyMethod[self.SelectColumnName] = [[self.SelectColumnName, "o_Categorical", 0], [self.SelectColumnName, "o_Categorical", self.groupValue]]
            self.methodTable_Box(self.SelectColumnName, methodname, self.o_Categorical)
            del self.groupValue
            del self.original_uniq
        elif(methodname == "마스킹"):
            del self.mask_list[0]
            self.mask_list = [rst for i, rst in enumerate(self.mask_list) if rst not in self.mask_list[:i]]#중복 제거
            self.methodTable_Box(self.SelectColumnName, methodname, self.mask_list)
            masking_levels = [[self.SelectColumnName, "masking", 0]]
            for i in range(self.ui.LevelTable.rowCount()): #get user's input values in LevelTable
                masking_levels.append([self.SelectColumnName, "masking", self.m_list[i][0], int(self.m_list[i][1])])
            masking_levels =[rst for i, rst in enumerate(masking_levels) if rst not in masking_levels[:i]] #중복제거
            self.mainWin.ApplyMethod[self.SelectColumnName] = masking_levels #dict에 값 넣음
            
            del masking_levels
            del self.m_list
            del self.mask_list
            
        elif(methodname == "통계 처리"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.AggregationLevel)
        elif (methodname == "rounding"):
            del self.round_list[0]
            self.round_list = [rst for i, rst in enumerate(self.round_list) if rst not in self.round_list[:i]]#중복 제거
            self.methodTable_Box(self.SelectColumnName, methodname, self.round_list) # show methodTable
            
            #rounding 경우의 수 계산
            rounding_levels = [[self.SelectColumnName, "rounding", 0]]
            for i in range(self.ui.LevelTable.rowCount()): #get user's input values in LevelTable
                rounding_levels.append([self.SelectColumnName, "rounding", self.r_list[i][0], int(self.r_list[i][1])])
            
            rounding_levels =[rst for i, rst in enumerate(rounding_levels) if rst not in rounding_levels[:i]] #중복제거

            self.mainWin.ApplyMethod[self.SelectColumnName] = rounding_levels #경우의 수 저장
            #안쓰는 변수 제거
            del rounding_levels
            del self.r_list
            del self.round_list

        self.mainWin.methodCol_List[self.SelectColumnName]  = self.mainWin.ui.methodTable.rowCount()-1 #컬럼이 저장된 행 저장  
        print(self.mainWin.methodCol_List)
        print(self.mainWin.ApplyMethod)
        self.ui.hide()

    def methodTable_Level(self, colName, method, level):
        self.mainWin.ui.methodTable.insertRow(self.mainWin.ui.methodTable.rowCount())
        self.mainWin.ui.methodTable.setItem(self.mainWin.ui.methodTable.rowCount()-1, 0, QTableWidgetItem(str(colName))) #column name
        self.mainWin.ui.methodTable.setItem(self.mainWin.ui.methodTable.rowCount()-1, 1, QTableWidgetItem(str(method))) #비식별 method
        self.mainWin.ui.methodTable.setItem(self.mainWin.ui.methodTable.rowCount()-1, 2, QTableWidgetItem(str(level))) #detail
       
    def methodTable_Box(self, colName, method, level_list):
        levelcom = QComboBox() 
        levelcom.addItems(level_list)

        self.mainWin.ui.methodTable.insertRow(self.mainWin.ui.methodTable.rowCount())
        self.mainWin.ui.methodTable.setItem(self.mainWin.ui.methodTable.rowCount()-1, 0, QTableWidgetItem(str(colName))) #column name
        self.mainWin.ui.methodTable.setItem(self.mainWin.ui.methodTable.rowCount()-1, 1, QTableWidgetItem(str(method))) #비식별 method
        self.mainWin.ui.methodTable.setCellWidget(self.mainWin.ui.methodTable.rowCount()-1, 2, levelcom)
        
