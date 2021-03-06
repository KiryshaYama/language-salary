import requests
import os

from dotenv import load_dotenv
from terminaltables import SingleTable


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to)/2
    if salary_from:
        return 1.2 * salary_from
    if salary_to:
        return 0.8 * salary_to


def parse_hh(language):
    params = {
        'User-Agent': 'api-test-agent',
        'area': 1,
        'period': 30,
        'per_page': 100,
        'text': f'Разработчик {language}',
        'page': 0
    }
    count = 0
    summary_salary = 0
    while True:
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
        params['page'] += 1
        if params['page'] >= vacancies['pages']:
            break
    if vacancies['found']:
        result_hh = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': count,
            'average_salary': int(summary_salary / count)
        }
        return result_hh


def parse_sj(language, app_key_sj):
    params = {
        'count': 100,
        'town': 4,
        'catalogues': 48,
        'app_key': app_key_sj,
        'keyword': language,
        'page': 0
    }
    count = 0
    summary_salary = 0
    while True:
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
        params['page'] += 1
        if params['page'] > int((vacancies['total']/params['count']+1)):
            break
    if vacancies['total']:
        result_sj = {
            'vacancies_found': vacancies['total'],
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
        if statistic[language]:
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
    if statistic_hh:
        title_hh = 'HeadHunter Moscow'
        print_table(statistic_hh, title_hh)
    if statistic_sj:
        title_sj = 'SuperJob Moscow'
        print_table(statistic_sj, title_sj)

if __name__ == '__main__':
    main()
