import numpy as np
import time
import pandas as pd
#for machine learning
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier  
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

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
        dataframe[dataframe.columns[0]] = round_up_dataframe(dataframe[dataframe.columns[0]], r_level)
    elif(r_index == "내림"):#내림
        dataframe[dataframe.columns[0]] = round_down_dataframe(dataframe[dataframe.columns[0]], r_level)
    elif(r_index == "반올림"):#5를 기준으로 up down, 반올림
        dataframe[dataframe.columns[0]] = round_half_up_dataframe(dataframe[dataframe.columns[0]], r_level)
        
    """
    if(r_index == "올림"):# 올림
        print("DeIdentifier r_index=올림")
        dataframe[dataframe.columns[0]] = ((dataframe[dataframe.columns[0]]+9*pow(10, r_level-1))//pow(10, r_level))*pow(10, r_level) # change number, up
    elif(r_index == "내림"):#내림
        dataframe[dataframe.columns[0]] = (dataframe[dataframe.columns[0]]//pow(10, r_level))*pow(10, r_level) # change number, down
    elif(r_index == "반올림"):#5를 기준으로 up down, 반올림
        dataframe[dataframe.columns[0]] = ((dataframe[dataframe.columns[0]]+5*pow(10, r_level-1))//pow(10, r_level))*pow(10, r_level) # change number, 4down, 5up
    elif(r_index == "랜덤"): #random 값을 기준으로 up down
        dataframe[dataframe.columns[0]] = ((dataframe[dataframe.columns[0]]+(10-randomN))//pow(10, r_level))*pow(10, r_level) # change number, 4down, 5up
    """        
    return dataframe

#올림
def round_up_dataframe(data, decimals=0): 
    decimals = ((np.log10(abs(data))).astype(int)+2 - decimals)
    multiplier = np.float_power(10, -decimals)
    rounded = (data*multiplier).apply(np.ceil)/multiplier
    return rounded.astype(int)

#내림
def round_down_dataframe(data, decimals=0):
    decimals = ((np.log10(abs(data))).astype(int)+2 - decimals)
    multiplier = np.float_power(10, -decimals)
    rounded = (data*multiplier).apply(np.floor)/multiplier
    return rounded.astype(int)

#반올림
def round_half_up_dataframe(data, decimals=0):
    decimals = ((np.log10(abs(data))).astype(int)+2 - decimals)
    multiplier = np.float_power(10, -decimals)
    rounded = (data*multiplier+0.5).apply(np.floor)/multiplier
    return rounded.astype(int)

#masking(마스킹)
def Masking(dataframe, m_index, m_level):      #데이터프레임['컬럼명'].to_frame(), index, level

    origin = dataframe.copy().astype(str)
    data = origin.copy()
    sum = 0
    
    if(m_index == "*(front)"): # * / 앞에서부터 마스킹
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: len(x[:m_level])*"*"  + (x[m_level:])  if m_level>0 else x)
        after_uniq = data[data.columns[0]].unique() #마스킹 결과 가져오기
        after_uniq = [w.replace('*', '') for w in after_uniq] # 마스킹 문자 제거하기
        for idx,i in enumerate(after_uniq):
            sum += (pow(origin[origin.columns[0]].str.contains(after_uniq[idx]).sum(), 2)) #마스킹 제거된 문자열을 포함하는 거 count
            
    elif(m_index == "*(back)"):#* / 뒤에서부터 마스킹
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: x[:len(x)-m_level] + len(x[len(x)-m_level:])*"*" if len(x) >= m_level else len(x[:])*"*")
        after_uniq = data[data.columns[0]].unique() #마스킹 결과 가져오기
        after_uniq = [w.replace('*', '') for w in after_uniq] # 마스킹 문자 제거하기
        for idx,i in enumerate(after_uniq):
            sum += (pow(origin[origin.columns[0]].str.contains(after_uniq[idx]).sum(), 2)) #마스킹 제거된 문자열을 포함하는 거 count
            
    elif(m_index == "0(front)"): # 0 / 앞에서부터 마스킹
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: len(x[:m_level])*"0"  + (x[m_level:])  if m_level>0 else x) 
        after_uniq = data[data.columns[0]].unique() #마스킹 결과 가져오기
        after_uniq = [w.replace('0', '') for w in after_uniq] # 마스킹 문자 제거하기
        for idx,i in enumerate(after_uniq):
            sum += (pow(origin[origin.columns[0]].str.contains(after_uniq[idx]).sum(), 2)) #마스킹 제거된 문자열을 포함하는 거 count
            
    elif(m_index == "0(back)"):# 0 / 뒤에서부터 마스킹
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: x[:len(x)-m_level] + len(x[len(x)-m_level:])*"0" if len(x) >= m_level else len(x[:])*"*") 
        after_uniq = data[data.columns[0]].unique() #마스킹 결과 가져오기
        after_uniq = [w.replace('0', '') for w in after_uniq] # 마스킹 문자 제거하기
        for idx,i in enumerate(after_uniq):
            sum += (pow(origin[origin.columns[0]].str.contains(after_uniq[idx]).sum(), 2)) #마스킹 제거된 문자열을 포함하는 거 count
            
    elif(m_index == "( )(front)"): # 0 / 앞에서부터 마스킹
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: len(x[:m_level])*""  + (x[m_level:])  if m_level>0 else x) 
        after_uniq = data[data.columns[0]].unique() #마스킹 결과 가져오기
        for idx,i in enumerate(after_uniq):
            sum += (pow(origin[origin.columns[0]].str.contains(after_uniq[idx]).sum(), 2)) #문자열을 포함하는 거 count
            
    elif(m_index == "( )(back)"):# 0 / 뒤에서부터 마스킹
        data[data.columns[0]] = data[data.columns[0]].apply(lambda x: x[:len(x)-m_level] + len(x[len(x)-m_level:])*"" if len(x) >= m_level else len(x[:])*"*") 
        after_uniq = data[data.columns[0]].unique() #마스킹 결과 가져오기
        for idx,i in enumerate(after_uniq):
            sum += (pow(origin[origin.columns[0]].str.contains(after_uniq[idx]).sum(), 2)) #문자열을 포함하는 거 count
    
    sum = round((sum/len(data[data.columns[0]])), 2)
    print(data)
    return data, sum


def O_Categorical(dataframe, groupValue):
    original_uniq = list(dataframe[dataframe.columns[0]].unique())
    #분모: len(original_uniq)
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

    sum =0
    for idx, cat in enumerate(groupCat):
        for i in range(len(cat)):
            sum = sum + (len(cat) * len(dataframe.loc[dataframe[dataframe.columns[0]] == str(cat[i])]))
            dataframe.loc[dataframe[dataframe.columns[0]] == str(cat[i]), dataframe.columns[0]] = str(groupCat_str[idx])

    sum = round(sum/len(original_uniq),2)
    
    return dataframe, groupCat, groupCat_str, sum

def I_Categorical(dataframe, minVal=0, maxVal=0, gapVal=0):
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
    #paddingmax = ((maxPrint+9*pow(10, len(str(maxPrint))-1))//pow(10, len(str(maxPrint))))*pow(10, len(str(maxPrint)))
    sum = 0
    sum = sum + (minVal * len(dataframe.loc[dataframe[dataframe.columns[0]] < minVal])) #최소값(사용자입력값) * 최소(사용자입력값)보다 작은 값 개수
    dataframe.loc[dataframe[dataframe.columns[0]] < minVal, dataframe.columns[0]] = "[0, " + str(minVal) + ")"
    sum = sum + (maxPrint * len(beforeframe.loc[beforeframe[beforeframe.columns[0]] > maxVal])) # 최대값(데이터프레임) * 최대(사용자 입력)보다 큰 값 개수
    dataframe.loc[beforeframe[beforeframe.columns[0]] >= maxVal, dataframe.columns[0]] = "[" + str(maxVal) + ", )" # + str(paddingmax) + ")"

    sum = sum + (gapVal * len(dataframe.loc[((beforeframe[beforeframe.columns[0]] >= minVal) & (beforeframe[beforeframe.columns[0]] <maxVal))])) # 최대값(데이터프레임) * 최대(사용자 입력)보다 큰 값 개수

    tmpList = []
    tmpVal = minVal
    
    while(tmpVal < maxVal):
        tmpList.append(tmpVal)
        tmpVal += gapVal

    for i in tmpList:
        if(i+gapVal<maxVal):
            dataframe.loc[((beforeframe[beforeframe.columns[0]] >= i) & (beforeframe[beforeframe.columns[0]] < i + gapVal)) == True, dataframe.columns[0]] = "[" + str(i) + "," + str(i+gapVal) + ")"
        else:
            dataframe.loc[((beforeframe[beforeframe.columns[0]] >= i) & (beforeframe[beforeframe.columns[0]] < maxVal)) == True, dataframe.columns[0]] = "[" + str(i) + "," + str(maxVal) + ")"

    sum = round(sum/len(dataframe), 2)
    print(dataframe)
    return dataframe, sum

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


def K_anonymity_Without_Masking_Category(data, lists, number): #데이터프레임, 준식별자리스트, k값
    """준식별자를 기준으로 그룹화해서 동일 레코드 수 계산 ->
    count 컬럼에 저장 -> count<n 인 값 변환 -> count 컬럼 "*"로 변환  """
    try:
        number = int(number)
    except NameError:
        number=1
    pass
    
    dataframe = data.copy()
    
    if(number>=2):
        dataframe['count'] = dataframe.groupby(lists)[lists[0]].transform('size') #그룹화해서 동질집합 수 count에 저장
        
        for i in lists:
            dataframe[i] = dataframe['count'].apply(lambda x: "*" if x<number else x) # K만족하지 못하면 "*"로 변환
        del dataframe['count']
        print(dataframe)
    
    return dataframe


def L_diversity_Without_Masking_Category(data, lists, number, column):  #데이터프레임, 준식별자리스트, l 값, 민감정보 컬럼
    """준식별자를 기준으로 그룹화해서 동일 레코드 수에 대한 유니크 값 계산 ->
    count 컬럼에 저장 -> count>=n 인 값만 추출 -> count 컬럼 "*"로 변환  """
    try:
        number = int(number)
    except NameError:
        number=1
    pass
    dataframe = data.copy()

    if(number>=2):
        dataframe['count'] = dataframe.groupby(lists)[column].transform('nunique') #그룹화해서 동질집합 수 count에 저장
        for i in lists:
            dataframe[i] = dataframe['count'].apply(lambda x: "*" if x<number else x) # K만족하지 못하면 "*"로 변환
        del dataframe['count']
        print(dataframe)
        
    return dataframe

def Calculate_risk(data, lists):

    results = data.groupby(lists)[lists[0]].count().tolist() 

    sums = 0
    results = [1/number for number in results] #1/N으로 변경
    for number in results:
        sums+=number

    sums = (sums/len(results)) #합 구하기
    sums = round(sums/data.shape[0], 2)*100 #퍼센트 구하기,
    return (str(sums) + "%")

def Calculate_RecordLinking(origin, Final):
    #make train data
    train_df = pd.DataFrame()
    cols = origin.columns
    train_df['feature'] = origin[cols].astype(str).apply(' '.join, axis=1)
    train_df['Y']= train_df.index

    score_df = pd.DataFrame()
    cols = Final.columns
    score_df['feature'] = Final[cols].astype(str).apply(' '.join, axis=1)
    score_df['Y']= score_df.index

    #prepare train_X
    count_vect = CountVectorizer()
    text = train_df['feature'].tolist()
    matrix = count_vect.fit_transform(text)
    #prepare train_Y
    targets = train_df['Y'].tolist()   
    encoder = LabelEncoder()
    targets = encoder.fit_transform(targets)
    #make model
    randomForest = RandomForestClassifier()
    randomForest.fit(matrix, targets)

    #not finished