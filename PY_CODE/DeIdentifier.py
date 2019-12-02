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
    dataframe = dataframe.copy()
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

    try:  #숫자만 입력, 그 외 값은 예외처리
        m_level = int(m_level)
        if(m_level<1):
            m_level/0
    except Exception:
        print('Error','Input can only be a m_level')
    pass

    beforedata = dataframe[dataframe.columns[0]].to_frame()
    afterdata = beforedata.copy()
    
    before_uniq = beforedata[beforedata.columns[0]].unique()
        
    unique_len = [] #길이를 저장
    mask = [] #
    after_uniq = before_uniq.copy() #

    for i in before_uniq:
        unique_len.append(len(i)-1) #유니크한 값의 각 길이를 저장

    for j in range(len(beforedata.index)): #rendering data (inputtable of Tab1)
        for u in range(len(before_uniq)):
            if(m_index == 0): # * masking
                if m_level > unique_len[u]:
                    t_lev = unique_len[u]+1
                    mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], "*"*t_lev))
                    after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                    after_uniq[u] = after_uniq[u]+mask[u]
                    if beforedata[beforedata.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                        afterdata[afterdata.columns[0]][j] = str(afterdata[afterdata.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                        
                else:
                    mask.append(after_uniq[u][unique_len[u]-(m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(m_level-1):unique_len[u]+1], "*"*m_level))
                    after_uniq[u] = after_uniq[u][0:unique_len[u]-(m_level-1)]
                    after_uniq[u] = after_uniq[u]+mask[u]
                    if beforedata[beforedata.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                        afterdata[afterdata.columns[0]][j] = str(afterdata[afterdata.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                        
            elif(m_index == 1): # 0 masking
                if m_level > unique_len[u]:
                    t_lev = unique_len[u]+1
                    mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], "0"*t_lev))
                    after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                    after_uniq[u] = after_uniq[u]+mask[u]
                    if beforedata[beforedata.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                        afterdata[afterdata.columns[0]][j] = str(afterdata[afterdata.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                        
                else:
                    mask.append(after_uniq[u][unique_len[u]-(m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(m_level-1):unique_len[u]+1], "0"*m_level))
                    after_uniq[u] = after_uniq[u][0:unique_len[u]-(m_level-1)]
                    after_uniq[u] = after_uniq[u]+mask[u]
                    if beforedata[beforedata.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                        afterdata[afterdata.columns[0]][j] = str(afterdata[afterdata.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
            elif(m_index == 2): # remove
                if m_level > unique_len[u]:
                    t_lev = unique_len[u]+1
                    mask.append(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(t_lev-1):unique_len[u]+1], " "*t_lev))
                    after_uniq[u] = after_uniq[u][0:unique_len[u]-(t_lev-1)]
                    after_uniq[u] = after_uniq[u]+mask[u]
                    if beforedata[beforedata.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                        afterdata[afterdata.columns[0]][j] = str(afterdata[afterdata.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                        
                else:
                    mask.append(after_uniq[u][unique_len[u]-(m_level-1):unique_len[u]+1].replace(after_uniq[u][unique_len[u]-(m_level-1):unique_len[u]+1], " "*m_level))
                    after_uniq[u] = after_uniq[u][0:unique_len[u]-(m_level-1)]
                    after_uniq[u] = after_uniq[u]+mask[u]
                    if beforedata[beforedata.columns[0]][j] == before_uniq[u]: # self.after[self.after.columns[0]][j] == before_uniq[i]:
                        afterdata[afterdata.columns[0]][j] = str(afterdata[afterdata.columns[0]][j]).replace(before_uniq[u], after_uniq[u])
                    
    return afterdata

#categorical(범주화)
def Categorical(dataframe, c_index):
    #need to implement
    return dataframe;

#Aggregation(통계처리)
def Aggregation(dataframe, index, method):
