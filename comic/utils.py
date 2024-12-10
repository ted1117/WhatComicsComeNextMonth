from datetime import date, datetime, timedelta
import re


def calculate_next_month():
    today = date.today()

    next_month_first_day = datetime(today.year, (today.month + 1) % 12, 1)
    next_month_last_day = datetime(today.year, (today.month + 2) % 12, 1) - timedelta(
        days=1
    )

    return next_month_first_day.strftime("%Y%m%d"), next_month_last_day.strftime(
        "%Y%m%d"
    )


def parse_staff(staff_string):
    # 정규 표현식 패턴들
    pattern = r"저자 : ([^;]+);?"
    pattern2 = r"삽화가\(그림작가\) : ([^;]+);"
    pattern3 = r"원작자 : ([^;]+);"
    pattern4 = r"역자 : ([^;]+);"

    # 정규 표현식 패턴 컴파일
    regex_pattern = re.compile(pattern)
    regex_pattern2 = re.compile(pattern2)
    regex_pattern3 = re.compile(pattern3)
    regex_pattern4 = re.compile(pattern4)

    # 정규 표현식을 사용하여 정보 추출
    authors_list = [author.strip() for author in regex_pattern.findall(staff_string)]
    # authors = authors_list[0] if authors_list else None
    illustrator = regex_pattern2.search(staff_string)
    illustrator = illustrator.group(1).strip() if illustrator else None
    original_author = regex_pattern3.search(staff_string)
    original_author = original_author.group(1).strip() if original_author else None
    translator = regex_pattern4.search(staff_string)
    translator = translator.group(1).strip() if translator else None
    authors = ", ".join(authors_list) if authors_list else illustrator

    return authors, illustrator, original_author, translator


def extract_authors(staff_string):
    # pattern = r"저자 : ([가-힣A-Za-z ]+);?"
    pattern = r"저자 : ([^;]+);?"
    pattern2 = r"삽화가\(그림작가\) : ([^;]+);"
    pattern3 = r"원작자 : ([^;]+);"
    pattern4 = r"역자 : ([^;]+);"
    author_list = re.findall(pattern, staff_string)
    authors = [author.strip() for author in author_list]
    match = re.search(pattern2, staff_string)
    match2 = re.search(pattern3, staff_string)
    match3 = re.search(pattern4, staff_string)
    if match:
        illustrator = match.group(1).strip()
    else:
        illustrator = "asdf"
    original_author = match2.group() if match2 else None
    translator = match3.group(1) if match3 else None

    return authors, illustrator, original_author, translator


def is_numeric(price):
    return bool(re.match(r"[0-9]+$", price))


def is_set(title):
    return bool(re.search("합본", title))
