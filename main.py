import requests
import os

from dotenv import load_dotenv
from terminaltables import SingleTable


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if not salary_from:
        return 0.8 * salary_to
    if not salary_to:
        return 1.2 * salary_from
    if salary_from and salary_to:
        return (salary_from + salary_to)/2


def parse_hh(language):
    params = {
        'User-Agent': 'api-test-agent',
        'area': 1,
        'period': 30,
        'per_page': 100
    }
    count = 0
    summary_salary = 0
    params['text'] = f'Разработчик {language}'
    response = requests.get('https://api.hh.ru/vacancies', params=params)
    response.raise_for_status()
    first_page = response.json()
    if first_page['found']:
        for page in range(first_page['pages']):
            params['page'] = page
            response = requests.get(
                'https://api.hh.ru/vacancies',
                params=params
            )
            response.raise_for_status()
            vacancies = response.json()
            for vacancy in vacancies['items']:
                if vacancy['salary'] and \
                        vacancy['salary']['currency'] == 'RUR':
                    summary_salary += predict_salary(
                        vacancy['salary']['from'],
                        vacancy['salary']['to']
                    )
                    count += 1
        result_hh = {
            'vacancies_found': first_page['found'],
            'vacancies_processed': count,
            'average_salary': int(summary_salary / count)
        }
    return result_hh


def parse_sj(language, app_key_sj):
    params = {
        'count': 100,
        'town': 4,
        'catalogues': 48,
        'app_key': app_key_sj
    }
    count = 0
    summary_salary = 0
    params['keyword'] = language
    response = requests.get(
        'https://api.superjob.ru/2.0/vacancies/',
        params=params
    )
    response.raise_for_status()
    first_page = response.json()
    print(first_page['total'])
    if first_page['total']:
        for page in range(int((first_page['total']/params['count']+1))):
            params['page'] = page
            response = requests.get(
                'https://api.superjob.ru/2.0/vacancies/',
                params=params
            )
            response.raise_for_status()
            vacancies = response.json()
            for vacancy in vacancies['objects']:
                if vacancy['payment_from'] or vacancy['payment_to'] != 0 and \
                            vacancy['currency'] == 'rub':
                    summary_salary += predict_salary(
                        vacancy['payment_from'],
                        vacancy['payment_to']
                    )
                    count += 1
        result_sj = {
            'vacancies_found': first_page['total'],
            'vacancies_processed': count,
            'average_salary': int(summary_salary / count)
        }
    return result_sj


def print_table(statistic, title):
    table_data = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата']
    ]

    for language in statistic:
        table_data.append([
            language,
            statistic[language]['vacancies_found'],
            statistic[language]['vacancies_processed'],
            statistic[language]['average_salary']
        ])
    table_instance = SingleTable(table_data, title)
    print(table_instance.table)
    print()


def main():
    load_dotenv()
    app_key_sj = os.environ['APP_KEY_SJ']
    statistic_hh = {}
    statistic_sj = {}
    languages = [
        'C#',
        'Objective-C',
        'Ruby',
        'Java',
        'C',
        'Typescript',
        'Scala',
        'Go',
        'Swift',
        'C++',
        'PHP',
        'JavaScript',
        'Python'
    ]
    for language in languages:
        statistic_hh[language] = parse_hh(language)
        statistic_sj[language] = parse_sj(language, app_key_sj)
    title_hh = 'HeadHunter Moscow'
    title_sj = 'SuperJob Moscow'
    if statistic_hh:
        print_table(statistic_hh, title_hh)
    if statistic_sj:
        print_table(statistic_sj, title_sj)

if __name__ == '__main__':
    main()
