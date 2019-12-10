import numpy as np
import time

#swap(교환기법)
def Swap(dataframe, swap_list):  #데이터프레임, 바꾸고 싶은 값 리스트 
    uniqueIndex = dataframe[dataframe.columns[0]].unique().tolist()
    uniqueIndex.sort()

    """값 변경"""
    for i in range(len(uniqueIndex)):
        dataframe.loc[dataframe[dataframe.columns[0]]==uniqueIndex[i], dataframe.columns[0]] = swap_list[i]     
    return dataframe


#shuffle(재배열)        
def Shuffle(dataframe, number):  #데이터프레임, 셔플횟수
    for _ in range(number):
        dataframe[dataframe.columns[0]] = np.random.permutation(dataframe[dataframe.columns[0]].values)
    return dataframe


#rounding(라운딩)
def Rounding(dataframe, r_index=0, r_level=0, randomN=0): #데이터프레임, 라운딩방법, 자리수   
    if(r_index == "올림"):# 올림
        print("DeIdentifier r_index=올림")
        dataframe[dataframe.columns[0]] = ((dataframe[dataframe.columns[0]]+9*pow(10, r_level-1))//pow(10, r_level))*pow(10, r_level) # change number, up
    elif(r_index == "내림"):#내림
        dataframe[dataframe.columns[0]] = (dataframe[dataframe.columns[0]]//pow(10, r_level))*pow(10, r_level) # change number, down
    elif(r_index == "반올림"):#5를 기준으로 up down, 반올림
        dataframe[dataframe.columns[0]] = ((dataframe[dataframe.columns[0]]+5*pow(10, r_level-1))//pow(10, r_level))*pow(10, r_level) # change number, 4down, 5up
    elif(r_index == "랜덤"): #random 값을 기준으로 up down
        dataframe[dataframe.columns[0]] = ((dataframe[dataframe.columns[0]]+(10-randomN))//pow(10, r_level))*pow(10, r_level) # change number, 4down, 5up
            
    return dataframe


#masking(마스킹)
def Masking(dataframe, m_index, m_level):      #데이터프레임['컬럼명'].to_frame(), index, level
    """
    try:  #숫자만 입력, 그 외 값은 예외처리
        m_level = int(m_level)
        if(m_level<1):
            m_level/0
    except Exception:
        print('Error','Input can only be a m_level')
    pass

    beforedata = dataframe[dataframe.columns[0]].to_frame()
    afterdata = beforedata.copy()
    """
    start = time.time()
    afterframe = dataframe.copy()
    before_uniq = dataframe[dataframe.columns[0]].unique()
    
    unique_len = []
    after_uniq = before_uniq.copy()

    for i in before_uniq:
        unique_len.append(len(i)-1)

    max_len = max(unique_len)

    for idx,i in enumerate(unique_len):
        if(m_index == "*"): # * masking
            if i < max_len:
                while i != max_len:
                    after_uniq[idx] = after_uniq[idx] + "*"
                    i += 1
            else:
                after_uniq[idx] = after_uniq[idx][:i] + "*"

            after_uniq[idx] = after_uniq[idx][:max_len-m_level+1] + "*" * m_level
            afterframe.loc[afterframe[afterframe.columns[0]] == before_uniq[idx], afterframe.columns[0]] = after_uniq[idx]

        elif(m_index == "0"): # 0 masking
            if i < max_len:
                while i != max_len:
                    after_uniq[idx] = after_uniq[idx] + "0"
                    i += 1
            else:
                after_uniq[idx] = after_uniq[idx][:i] + "0"

            after_uniq[idx] = after_uniq[idx][:max_len-m_level+1] + "0" * m_level
            afterframe.loc[afterframe[afterframe.columns[0]] == before_uniq[idx], afterframe.columns[0]] = after_uniq[idx]

        elif(m_index == "( )"): # ( ) masking
            if i < max_len:
                while i != max_len:
                    after_uniq[idx] = after_uniq[idx] + " "
                    i += 1
            else:
                after_uniq[idx] = after_uniq[idx][:i] + " "

            after_uniq[idx] = after_uniq[idx][:max_len-m_level+1] + " " * m_level
            afterframe.loc[afterframe[afterframe.columns[0]] == before_uniq[idx], afterframe.columns[0]] = after_uniq[idx]
    print(time.time() -start)
    return afterframe

def O_Categorical(dataframe, groupValue):
    original_uniq = list(dataframe[dataframe.columns[0]].unique())

    groupCat = []
    groupCat_str = []

    start = 0
    end = len(original_uniq)
    
    for _ in range(start, end+groupValue, groupValue):
        groupEle_tmp = original_uniq[start : start + groupValue]
        if groupEle_tmp != []:
            groupCat.append(groupEle_tmp)
            groupEle_tui = str(groupEle_tmp).replace("'","")
            groupCat_str.append(groupEle_tui)
        start = start + groupValue

    del groupEle_tmp

    for idx, cat in enumerate(groupCat):
        for i in range(len(cat)):
            dataframe.loc[dataframe[dataframe.columns[0]] == str(cat[i]), dataframe.columns[0]] = str(groupCat_str[idx])

    return dataframe, groupCat, groupCat_str

def I_Categorical(dataframe, minVal=0, maxVal=0, gapVal=0):
    start = time.time()
    beforeframe = dataframe.copy()
    
    try:
        minVal = int(minVal)
        maxVal = int(maxVal)
        gapVal = int(gapVal)
        if(minVal<1):
            minVal/0
        elif(maxVal<1):
            maxVal/0
        elif(gapVal<1):
            gapVal/0
    except Exception:
        QtWidgets.QMessageBox.about(self, 'Error','숫자만 입력할 수 있습니다.')
    pass

    maxPrint = dataframe[dataframe.columns[0]].max()
    paddingmax = ((maxPrint+9*pow(10, len(str(maxPrint))-1))//pow(10, len(str(maxPrint))))*pow(10, len(str(maxPrint)))

    dataframe.loc[dataframe[dataframe.columns[0]] < minVal, dataframe.columns[0]] = "[0, " + str(minVal) + ")"
    dataframe.loc[beforeframe[beforeframe.columns[0]] >= maxVal, dataframe.columns[0]] = "[" + str(maxVal) + "," + str(paddingmax) + ")"

    tmpList = []
    tmpVal = minVal

    #idx = 1
    while(tmpVal < maxVal):
        tmpList.append(tmpVal)
        tmpVal += gapVal
        #idx += 1
    print(tmpList)

    for i in tmpList:
        dataframe.loc[((beforeframe[beforeframe.columns[0]] >= i) & (beforeframe[beforeframe.columns[0]] < i + gapVal)) == True, dataframe.columns[0]] = "[" + str(i) + "," + str(i+gapVal) + ")"

        
    """
    ii = int((maxVal-minVal)/gapVal)
            for i in range(ii):
        dataframe.loc[((beforeframe[beforeframe.columns[0]]-minVal >= i*gapVal) & (beforeframe[beforeframe.columns[0]]-minVal < (i+1)*gapVal)) == True, dataframe.columns[0]] = "[" + str(minVal+i*gapVal) + "," + str(minVal+(i+1)*gapVal) + ")"
    #print(dataframe)
    """

    print(dataframe)
    print(time.time() -start)
    return dataframe

#aggregation(통계처리)
def Aggregation(dataframe, index, method):
    #reference: https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame/31502974#31502974
    q1 = dataframe[dataframe.columns[0]].quantile(0.25) #calculate q1
    q3 = dataframe[dataframe.columns[0]].quantile(0.75) #calculate q3
    iqr = q3-q1 #Interquartile range
    fence_low  = q1-1.5*iqr 
    fence_high = q3+1.5*iqr

    if index == "ALL": #모든 값을 총계나 평균으로 변경  
        if method == "총합": #총합으로 통일
            sum = dataframe[dataframe.columns[0]].sum()
            print(sum)
            dataframe[dataframe.columns[0]] = sum
            print(dataframe[dataframe.columns[0]])
        elif method == "평균": #평균으로 통일
            mean = dataframe[dataframe.columns[0]].mean()
            print(mean)
            dataframe[dataframe.columns[0]] = dataframe[dataframe.columns[0]].mean()    
            print(dataframe[dataframe.columns[0]]) 
    elif index == "IQR": #이상치 값만 처리
        if method == "평균": #MEAN
            mean =  dataframe[~((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]]> fence_high))].mean()
            print(mean)
            dataframe[dataframe.columns[0]] = np.where(((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]]  > fence_high)), mean, dataframe[dataframe.columns[0]])
        elif method == "최대": #MAX
            max = dataframe[~((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]]> fence_high))].max()
            print(max)
            dataframe[dataframe.columns[0]] = np.where(((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]]  > fence_high)), max, dataframe[dataframe.columns[0]])
        elif method == "최소": #MIN
            min = dataframe[~((dataframe[dataframe.columns[0]]< fence_low) |(dataframe[dataframe.columns[0]]> fence_high))].min()
            print(min)
            dataframe[dataframe.columns[0]] = np.where(((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]]  > fence_high)), min, dataframe[dataframe.columns[0]])
        elif method == "중앙": #MEDIAN
            median = dataframe[dataframe.columns[0]].median()
            print(median)
            dataframe[dataframe.columns[0]] = np.where(((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]]  > fence_high)), median, dataframe[dataframe.columns[0]])
        elif method == "최빈": #MODE
            mode = dataframe[dataframe.columns[0]].value_counts().idxmax() #최빈값
            print(mode)
            dataframe[dataframe.columns[0]] = np.where(((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]]  > fence_high)), mode, dataframe[dataframe.columns[0]])
        elif method == "삭제": #REMOVE
            print("remove")
            dataframe[dataframe.columns[0]] =  dataframe[~((dataframe[dataframe.columns[0]] < fence_low) |(dataframe[dataframe.columns[0]] > fence_high))]

    """ float로 변경될 경우, 반올림 후 int로 재변환"""
    #dataframe[dataframe.columns[0]]=round(dataframe[dataframe.columns[0]],0)
    #dataframe[dataframe.columns[0]] = dataframe[dataframe.columns[0]].astype(int)
    return dataframe


def K_anonymity(dataframe, list, number):
    """준식별자를 기준으로 그룹화해서 동일 레코드 수 계산 ->
    count 컬럼에 저장 -> count>=n 인 값만 추출 -> count 컬럼 delete  """
    try:
        number = int(number)
    except NameError:
        QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
    pass

    dataframe['count'] = dataframe.groupby(list)[list[0]].transform('size')
    dataframe = dataframe.loc[dataframe['count']>=number] #user parameter
    del dataframe['count']
    dataframe = dataframe.reset_index(drop=True)
    print(dataframe)
    return dataframe


def L_diversity(dataframe, list, number, column): 
    """준식별자를 기준으로 그룹화해서 동일 레코드 수에 대한 유니크 값 계산 ->
    count 컬럼에 저장 -> count>=n 인 값만 추출 -> count 컬럼 delete  """
    try:
        number = int(number)
    except NameError:
        QtWidgets.QMessageBox.about(self, 'Error','Input can only be a number')
    pass

    dataframe['count'] = dataframe.groupby(list)[column].transform('nunique') #salary -> 사용자 선택 민감정보
    dataframe = dataframe.loc[dataframe['count']>=number] #2는 사용자로부터 입력받아야되는 숫자
    del dataframe['count']
    dataframe = dataframe.reset_index(drop=True)       
    print(dataframe)
    return dataframe
