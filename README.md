# WhatComicsComeNextMonth
## 개요
- 다음 달에 출간될 만화 전자책을 미리 알아보는 서비스입니다.
- 진행중!

## 개발환경
<!-- - Frontend
  - HTML
  - CSS
  - Vanilla JS -->
- Backend
  - Python
  - Django REST Framework
- DB
  - PostgreSQL
- Etc
  - Docker
  - VS Code
  - Pycharm CE
  - Postman
  - Github

## 기능
- 다음 달에 출간되는 만화 전자책을 [ISBN 서지정보](https://www.nl.go.kr/NL/contents/N31101030500.do) 전산으로 미리 알아봅시다.
- 만화책을 사기 위해 충전할 캐시를 미리 계산할 수 있습니다.
- 지금까지 읽은 만화책을 기록할 수 있습니다.
- 자신이 읽은 만화에 평점과 리뷰를 남길 수 있습니다.

## API 명세
### Comic
| **Endpoint**         | **HTTP Method** | **설명**                      |
|-----------------------|-----------------|--------------------------------|
| `/api/comics/`       | **GET**         | 만화 리스트 조회               |
<!-- | `/api/comics/{id}/`  | **GET**         | 특정 만화 상세 조회            | -->

### User
| **Endpoint**         | **HTTP Method** | **설명**                      |
|-----------------------|-----------------|--------------------------------|
| `/user/signup/`           | **POST**        | 사용자 회원가입                |
| `/user/token/`            | **POST**        | JWT 토큰 발급                 |
| `/user/signin/`           | **POST**        | 사용자 로그인                  |

### Cart
| **Endpoint**         | **HTTP Method** | **설명**                            |
|-----------------------|-----------------|-------------------------------------|
| `/cart/`             | **GET**         | 사용자의 장바구니 아이템 조회         |
| `/cart/`             | **POST**        | 만화를 장바구니에 추가                |
| `/cart/`             | **DELETE**      | 장바구니에서 만화 삭제                |

### Rating
| **Endpoint** | **HTTP Method** | **설명** |
|-----------------------|-----------------|-------------------------------------|
| `/archive/?comic_id={comic_id}/` | **GET** | 만화별 평가 조회 |
| `/archive/?user_id={user_id}/` | **GET** | 유저별 만화 평가 조회 |
| `/archive/` | **POST** | 만화 평가 생성 |
| `/archive/pk/` | **DELETE** | 만화 평가 삭제 |



## ERD
<!--![diagram](https://github.com/user-attachments/assets/58e51ca9-d7b3-4334-bbf8-98465ea0de0f)-->
![comic_erd](https://github.com/user-attachments/assets/087d297f-d1bc-4d67-83bf-312da6893b7c)

## 트러블슈팅
### 데이터 불러오기
#### 문제점
- 현재 ISBN 체계에서 종이책은 장르별로 ISBN이 구분되나 전자책은 장르과 무관하게 '전자책' 범주에 하나로 묶임
- 종이책은 만화 장르를 따로 구분할 수 있지만 전자책은 불가능

#### 해결
- 유명 만화출판사를 DB에 저장하여 API에 쿼리할 때 매개변수로 지정
- 그 밖에 만화만을 지정하기 위해 출판사별 부가기호와 KDC 기준 주제 번호를 같이 매개변수로 지정
- 다만 일부 출판사는 발매예정일이 실제 발매일과 다른 경우가 많아 제외 (ex. 소미미디어)
----
### 단행본 걸러내기
#### 문제점
- 만화는 단행본과 연재본으로 나뉨
- 연재본은 필요하지 않기 때문에 DB에 저장할 필요가 없음

#### 해결
```python
def is_numeric(price):
	return bool(re.match(r"[0-9]+$", price))
```
- 단행본과 달리 연재본은 가격이 입력되지 않기 때문에 정규표현식을 사용
----
### 데이터를 표시하는 속도 줄이기
#### 문제점
- 기존 코드는 데이터를 불러오는 부분과 사용자에게 표시하는 부분이 같이 있었기 때문에 속도가 많이 느림

#### 해결
- 페이지네이션
  - 페이지별로 사용자에게 보일 데이터 수를 제한
- 불러오는 과정과 표시하는 과정 분리
  - <img width="149" alt="스크린샷 2024-04-12 22 54 03" src="https://github.com/user-attachments/assets/e9cf4c48-d650-45d8-9916-dc27a3f5bb99">
  - 사용자에게 데이터를 보여주는 코드와 API로 데이터를 불러오는 과정을 완전히 분리
  - 데이터를 불러오는 과정은 Django Celery로 비동기식 동작
#### 결과
- <img width="124" alt="스크린샷 2024-11-14 18 26 06" src="https://github.com/user-attachments/assets/d18379c3-6dc1-4879-b93c-d178e2b2ba86">
- 기존 최대 7296ms가 소요되던 시간이 92ms로 단축

