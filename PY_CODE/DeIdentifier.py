import numpy as np

#swap(교환기법)
def Swap(dataframe, origin_list, swap_list):  #데이터프레임, 바꾸고 싶은 값 리스트 
    """값 변경"""
    for i in range(len(origin_list)):
        dataframe.loc[dataframe[dataframe.columns[0]]==origin_list[i], dataframe.columns[0]] = swap_list[i]     
    return dataframe

#shuffle(재배열)        
def Shuffle(dataframe, number):  #데이터프레임, 셔플횟수
    for _ in range(number):
        dataframe[dataframe.columns[0]] = np.random.permutation(dataframe[dataframe.columns[0]].values)
    return dataframe

#rounding(라운딩)
def Rounding(dataframe, r_index=0, r_level=0, randomN=0): #데이터프레임, 라운딩방법, 자리수   
    if(r_index == "올림"):# 올림
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
    data = dataframe.copy()
    return dataframe

#categorical(범주화)
def Categorical(dataframe, c_index):
    #need to implement
    return dataframe;


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



