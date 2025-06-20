import json
import os
import pandas as pd
import streamlit as st

# 기본 데이터 파일 경로
DATA_FILE = "business_trip_data.json"
PROJECT_NAMES_FILE = "연구과제명.csv"

# 기본 데이터
DEFAULT_DATA = {
    "project_managers": ["이정석", "최태섭", "한영석", "김병모", "문성대", "김남현"],
    "destinations": [
        "고창", "서울", "부산", "인천", "울산", 
        "여수", "목포", "포항", "통영", "제주", "완도",
        "군산", "보령", "태안", "안산", "화성"
    ]
}

def load_data():
    """데이터 파일에서 데이터를 로드하거나 기본 데이터를 반환"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 기본 데이터에 없는 키가 있으면 추가
            for key in DEFAULT_DATA:
                if key not in data:
                    data[key] = DEFAULT_DATA[key].copy()
            
            return data
        else:
            # 파일이 없으면 기본 데이터로 파일 생성
            save_data(DEFAULT_DATA)
            return DEFAULT_DATA.copy()
            
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        return DEFAULT_DATA.copy()

def save_data(data):
    """데이터를 파일에 저장"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"데이터 저장 오류: {e}")
        return False

def add_new_data(data_type, value, data=None):
    """새로운 데이터 추가"""
    if data is None:
        data = load_data()
    
    if data_type in data and value not in data[data_type]:
        data[data_type].append(value)
        save_data(data)
        return True
    return False

def remove_data(data_type, value, data=None):
    """데이터 제거"""
    if data is None:
        data = load_data()
    
    if data_type in data and value in data[data_type]:
        data[data_type].remove(value)
        save_data(data)
        return True
    return False

def reset_to_default():
    """기본 데이터로 초기화"""
    # 기본 데이터 저장
    save_data(DEFAULT_DATA)
    
    # Streamlit 캐시 클리어 (만약 캐시된 데이터가 있다면)
    if hasattr(st, 'cache_data'):
        st.cache_data.clear()
    if hasattr(st, 'cache_resource'):
        st.cache_resource.clear()
    
    print("DEBUG: 데이터가 초기화되었습니다.")
    return DEFAULT_DATA.copy()

# 데이터 검증 함수들
def validate_data(data):
    """데이터 유효성 검사"""
    required_keys = ["project_managers", "destinations"]
    
    for key in required_keys:
        if key not in data:
            return False, f"필수 키 '{key}'가 없습니다."
        if not isinstance(data[key], list):
            return False, f"'{key}'는 리스트여야 합니다."
        if len(data[key]) == 0:
            return False, f"'{key}'에 최소 하나의 값이 있어야 합니다."
    
    return True, "데이터가 유효합니다."

def get_data_summary(data=None):
    """데이터 요약 정보 반환"""
    if data is None:
        data = load_data()
    
    summary = {}
    for key, values in data.items():
        summary[key] = {
            "count": len(values),
            "items": values
        }
    
    return summary

def load_project_names():
    """Streamlit Secrets 또는 연구과제명.csv 파일에서 연구과제명 목록을 로드"""
    try:
        # 먼저 Streamlit Secrets에서 데이터를 로드하려고 시도
        if hasattr(st, 'secrets'):
            print(f"DEBUG: Secrets 사용 가능, 모든 키 확인 중...")
            print(f"DEBUG: Secrets 키 목록: {list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else 'N/A'}")
            
            # project_names가 있는지 확인
            if 'project_names' in st.secrets:
                # Streamlit Secrets에서 데이터 로드 (강제 새로고침)
                project_names = list(st.secrets["project_names"])
                print(f"DEBUG: Secrets에서 연구과제명 로드됨: {len(project_names)}개")
                # 디버그용 첫 3개 항목 출력
                if len(project_names) > 0:
                    print(f"DEBUG: 첫 3개 항목: {project_names[:3]}")
                return project_names
            else:
                print("DEBUG: project_names 키가 Secrets에 존재하지 않음")
                # Secrets에 있는 모든 키 출력
                try:
                    all_keys = list(st.secrets.keys())
                    print(f"DEBUG: 사용 가능한 Secrets 키: {all_keys}")
                except:
                    print("DEBUG: Secrets 키 목록을 가져올 수 없음")
                    
                # 강제로 다시 시도 (대소문자 구분 없이)
                for key in st.secrets:
                    if 'project' in key.lower():
                        print(f"DEBUG: 유사한 키 발견: {key}")
                        try:
                            project_names = list(st.secrets[key])
                            print(f"DEBUG: {key}에서 연구과제명 로드됨: {len(project_names)}개")
                            return project_names
                        except Exception as e:
                            print(f"DEBUG: {key} 로드 실패: {e}")
                            continue
        
        # Streamlit Secrets가 없으면 CSV 파일에서 로드 (로컬 개발용)  
        elif os.path.exists(PROJECT_NAMES_FILE):
            df = pd.read_csv(PROJECT_NAMES_FILE, encoding='utf-8')
            # 첫 번째 열의 데이터를 리스트로 반환 (NaN 값 제외)
            project_names = df.iloc[:, 0].dropna().tolist()
            print(f"DEBUG: CSV에서 연구과제명 로드됨: {len(project_names)}개")
            return project_names
        else:
            print(f"DEBUG: '{PROJECT_NAMES_FILE}' 파일이 존재하지 않습니다.")
            # 최신 연구과제명 리스트 반환 (2024.12.30 업데이트)
            updated_projects = [
                "내화물생산실 염에 의한 생태독성 증명 컨설팅",
                "해양생물종(윤충류)을 이용한 생태독성 시험 교차검증(분석용역)",
                "염인정 시설 운영 실태 조사",
                "첨단산업 배출수의 어장환경 생태 위해성 관리체계 구축 연구 I",
                "(재)한국화학융합시험연구원 Orthophosphoric acid (CAS No. 7664-38-2) 후발등록 컨설팅",
                "해양오염퇴적물 현장조사 및 분석용역",
                "2025 이차전지 폐수 처리수 방류수역 모니터링",
                "수질 및 수생태계 환경기준(안) 도출 연구(2025)",
                "2025년 폐수배출시설 생태독성관리 기술지원",
                "2025년 이차전지 폐수처리 기술지원",
                "통영항 오염퇴적물 정화사업 사업후 해양환경 모니터링(3년차)",
                "2025년 울산연안 및 광양만 특별관리해역 연안오염총량관리 도입 및 시행 연구",
                "후발등록자 국내참조권 제공 계약",
                "신규 신경독소 시험법 개발 및 실태조사 연구",
                "미세조류 분석자료 데이터베이스 구축"
            ]
            print(f"DEBUG: 최신 연구과제명 사용: {len(updated_projects)}개")
            return updated_projects
    except Exception as e:
        print(f"연구과제명 로드 오류: {e}")
        # 에러 발생 시 최신 리스트 반환 (2024.12.30 업데이트)
        fallback_projects = [
            "내화물생산실 염에 의한 생태독성 증명 컨설팅",
            "해양생물종(윤충류)을 이용한 생태독성 시험 교차검증(분석용역)",
            "염인정 시설 운영 실태 조사",
            "첨단산업 배출수의 어장환경 생태 위해성 관리체계 구축 연구 I",
            "(재)한국화학융합시험연구원 Orthophosphoric acid (CAS No. 7664-38-2) 후발등록 컨설팅",
            "해양오염퇴적물 현장조사 및 분석용역",
            "2025 이차전지 폐수 처리수 방류수역 모니터링",
            "수질 및 수생태계 환경기준(안) 도출 연구(2025)",
            "2025년 폐수배출시설 생태독성관리 기술지원",
            "2025년 이차전지 폐수처리 기술지원",
            "통영항 오염퇴적물 정화사업 사업후 해양환경 모니터링(3년차)",
            "2025년 울산연안 및 광양만 특별관리해역 연안오염총량관리 도입 및 시행 연구",
            "후발등록자 국내참조권 제공 계약",
            "신규 신경독소 시험법 개발 및 실태조사 연구",
            "미세조류 분석자료 데이터베이스 구축",
            "해양 아쿠아포닉스 양식기술 개발",
            "해양 아쿠아포닉스 최적환경 조성 및 운용기술 개발",
            "한-미 공동 해조류 바이오매스 생산 시스템 기술개발",
            "아열대 환경적응 시나리오개발 대응책 및 활용체계 구축",
            "해양 CCS 중규모 실증을 위한 해양 환경 평가·감시 체계 및 기반기술 개발",
            "신규pops(해양환경 잔류성 오염물질 관리기술 개발)",
            "선체부착생물 관리 및 평가 기술 개발",
            "과학기술 기반 해역이용 영향평가기술개발",
            "해양 유해물질 오염원 추적기법개발",
            "해양 생태계 보호기준 마련을 위한 위해성평가",
            "블루카본 기반 기후변화 적응형 해안조성 기술개발",
            "새만금 산단 이차전지 공공 수질관리 고도화시설 기본구상 연구용역",
            "해상풍력 생태계 영향 조사 및 분석 기반 구축",
            "Marine glass를 활용한 염생식물 현장적용 평가",
            "Marine glass를 활용한 해조류 및 수산양식 적용 연구",
            "｢동남해안 해상풍력 발전사업｣ 수중전자기장 조사 용역",
            "고창 갯벌 식생복원사업 기본 및 실시설계용역-시범사업(TestBed) 설계 및 시공",
            "소셜라딕스 시제품 성능시험 인증",
            "주식회사 아이비코퍼레이션 Orthophosphoric acid (CAS No. 7664-38-2) 후발등록 컨설팅",
            "국내산 메탄저감 해조류 대량양식 기술개발 기획연구",
            "주식회사 코센트 Orthophosphoric acid (CAS No. 7664-38-2) 후발등록 컨설팅",
            "SK하이닉스 수계 배출물질 43종(기존물질 39종, 신규물질 4종)에 대한 생태권고치 확인 및 산정 용역",
            "물벼룩 생태독성 분석",
            "2024년 폐수배출시설 TOC관리 기술지원",
            "물품구매계약서:연구재료(Quick press 부속 외)",
            "인천지역 전기공급시설 전력구공사(동송도-서송도) 중 생태독성 염해석 용역",
            "공동사업 계약서 :  해상풍력 수중전자기장 측정장비 판매사업",
            "\"Bobae Offshore Wind Farm Project\" 환경영향평가 중 수중 전자기장조사 및 모델링, 육상 전자기장조사 용역",
            "풍력단지 건설 예정 위치 기반의 AR 영상제공 앱 개발",
            "구미 하이테크밸리 공공폐수처리시설 생태독성 원인규명 용역",
            "기존화학물질 등록 컨설팅",
            "2024년 한강 상수원 취수구 퇴적물 분석 용역",
            "｢완도 장보고 해상풍력 발전사업｣ 수중전자기장 조사 용역",
            "이차전지 폐수의 효율적 관리방안 연구용역",
            "독성원인물질탐색 연구용역",
            "인테그리스 코리아(1000톤 이상) 인산등록컨설팅",
            "영광 한빛해상풍력발전단지 조성사업 환경영향평가 용역 중 전자기장 조사 및 모델링",
            "(재)한국화학융합시험연구원 Orthophosphoric acid (CAS No. 7664-38-2) 후발등록 컨설팅",
            " ㈜이엔에프테크놀로지 아산공장 Orthophosphoric acid (CAS No. 7664-38-2) 후발등록 컨설팅",
            "완도군 해조류 바이오 스마트팩토리 구축 타당성조사 및 기본계획 수립 용역",
            "욕지좌사리 해상풍력 발전단지 개발사업 환경영향평가 중 수중전자기장 현황 조사·분석용역"
        ]
        print(f"DEBUG: 에러 발생으로 최신 연구과제명 사용: {len(fallback_projects)}개")
        return fallback_projects

def get_all_data():
    """모든 데이터를 통합하여 반환 (기본 데이터 + 연구과제명)"""
    data = load_data()
    
    # 연구과제명을 Secrets에서 직접 가져오기 (employee_manager 방식과 동일)
    try:
        if hasattr(st, 'secrets') and 'project_names' in st.secrets:
            print("DEBUG: get_all_data - Secrets에서 project_names 직접 로드 시도")
            # 직접 접근 (employee_manager와 동일한 방식)
            project_names = list(st.secrets["project_names"])
            print(f"DEBUG: get_all_data - Secrets에서 {len(project_names)}개 직접 로드 완료")
            if len(project_names) > 0:
                print(f"DEBUG: get_all_data - 첫 3개: {project_names[:3]}")
            data["project_names"] = project_names
            return data
        else:
            print("DEBUG: get_all_data - Secrets에 project_names 없음, load_project_names() 사용")
            project_names = load_project_names()
            data["project_names"] = project_names
            return data
    except Exception as e:
        print(f"DEBUG: get_all_data - 오류 발생: {e}")
        # 오류 발생 시 기존 방식 사용
        project_names = load_project_names()
        data["project_names"] = project_names
        return data
