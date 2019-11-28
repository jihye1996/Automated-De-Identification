#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import pandas as pd
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtWidgets

import matplotlib.pyplot as plt
plt.rc('font', family='Malgun Gothic') #한글 깨짐 방지
plt.rc('axes', unicode_minus=False) #한글 깨짐 방지

#to import UI path
sys.path.append("./UI") # insert your path
sys.path.append("./PY_CODE")

import DeIdentifier

class NonIdentifierWin(QMainWindow):
    def __init__(self, mainWindow, dataframe, type):
        super().__init__()
        self.mainWin = mainWindow
        self.before = dataframe.copy()
        self.type = type
        self.InitUI()

    
    def InitUI(self):
        self.ui = uic.loadUi("./UI/SelectNonIdentifierMethod.ui") #insert your UI path
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

    #data Rounding start
    def Rounding(self):
        row = self.ui.LevelTable.rowCount()
        self.r_list = []
        for row in range(row):
            param_list = []
            for col in range(self.ui.LevelTable.columnCount()):
                table_item = self.ui.LevelTable.item(row,col)
                if col == 0 and isinstance(self.ui.LevelTable.cellWidget(row, 0), QComboBox):
                    current_value = self.ui.LevelTable.cellWidget(row, 0).currentText()
                    param_list.append(current_value)
                else:
                    param_list.append('' if table_item is None else str(table_item.text()))
            self.r_list.append(param_list)
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

    def addLevel(self, method, table): #add 버튼 누르면 프라이버시 모델 설정 가능
        if(method == "rounding"):
            privacy_list = ["올림", "내림", "반올림", "랜덤"]

        table.insertRow(table.rowCount())
        self.addCombo = QComboBox() 
        self.addCombo.addItems(privacy_list)
        table.setCellWidget(table.rowCount()-1, 0, self.addCombo)

    def delLevel(self, table):
        table.removeRow(table.currentRow())


    #데이터 mainwindow.deData 및 methodTable 저장 및 UI 끄기
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
            self.mainWin.ApplyMethod[self.SelectColumnName] = ["swap", [0, 0], [1, self.swap_values]]
            self.methodTable_Box(self.SelectColumnName, methodname, self.swap_list)
            del self.swap_list
            del self.swap_values
        elif(methodname == "shuffle"):
            self.mainWin.ApplyMethod[self.SelectColumnName] = ["shuffle", [0, 0], [1, self.shufflenumber]]
            self.methodTable_Level(self.SelectColumnName, methodname,  ("Suffled " + str(self.shufflenumber)),)
            del self.shufflenumber
        elif(methodname == "연속 변수 범주화"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.i_Categorical)
        elif(methodname == "순위 변수 범주화"):
            self.methodTable_Box(self.SelectColumnName, methodname, self.o_Categorical)
        elif(methodname == "마스킹"): 
            self.methodTable_Level(self.SelectColumnName, methodname, ("level " + str(self.m_level)))
        elif(methodname == "통계 처리"):
            self.methodTable_Level(self.SelectColumnName, methodname, self.AggregationLevel)
        elif (methodname == "rounding"):
            del self.round_list[0]
            self.methodTable_Box(self.SelectColumnName, methodname, self.round_list)
            temp_list = ["rounding", [0,0]]
            for i in range(self.ui.LevelTable.rowCount()):
                temp_list.append([self.r_list[i][0], int(self.r_list[i][1])])
                
            self.mainWin.ApplyMethod[self.SelectColumnName] = temp_list
            del temp_list
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
        
