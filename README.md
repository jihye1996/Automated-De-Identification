# Automated-De-Identification
add function 
code refactoring
modify algorithm

## Project Overview
It is a tool for Non-Identifying that prevents certain individuals from being exposed to data.  
    
### 1. File Import  
- handling missing values(결측치 처리)     
- Select columns to use(사용할 컬럼 선택)    
- Select data attribute(속성 선택: 식별자, 비식별자, 민감정보, 일반정보)  
- Select data type (데이터 타입 선택)     
    
### 2. Non-Identifying  
- Swap(교환)  
- Shuffle(재배열: 랜덤하게 섞기)    
- Suppression(범주화: 이항변수화, 이산형화)  
- Masking or Remove(마스킹 혹은 삭제)  
- Aggregation(통계값처리: 평균, 최빈, 최소, 최대)  
- Rounding(라운딩: 올림, 내림, 반올림, 랜덤)  
- Privacy Model: K-Anonymity, L-Diversity(프라이버시모델: K-익명성, L-다양성)  
    
### 3. Result: Compare before & after data  
- Re-identification risk graph  
- Data Correlation  

### 4. 추가사항
#### 포크 전 추가된 기능
- 사용자가 지정한 비식별 함수를 조합해 모든 경우의 수 도출(def run 참고)
- 비식별 함수 모듈화(DeIdentifier.py)
- 클래스 분리(ImportDatawin.py, ModifyWin.py, NonIdentifierWin.py)
#### 포크 후 수정사항
- 마스킹 시 앞 혹은 뒤에서 시작 가능(DeIdentifer의 Masking 참고)
- 연속 변수 범주화 시 생기는 오류 수정(DeIdentifer의 I_Categorical 참고)
- 범주화 변수 정보 손실 추가
- 재식별 리스크 평균 추가
- 도출된 경우의 수 중 하나를 더블 클릭하면 세부 분석 가능

## Used tool
-   **Language: Python 3.6.5
-   **Deisgn: Qt Designer

## Installing the source
1. Download.
```
git clone git@github.com:dd-nonidentifying/Non-Identifying.git
```
2. Run the code with python.

# etc
if you want to know details of the program, see the "programOverview.hwp"

