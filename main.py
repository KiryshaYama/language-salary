import requests
import json
import os

from dotenv import load_dotenv
from terminaltables import SingleTable


def predict_salary(salary_from, salary_to):
    if salary_from == 0 or salary_from is None:
        return 0.8*salary_to
    if salary_to == 0 or salary_to is None:
        return 1.2 * salary_from
    if salary_from and salary_to != 0:
        return (salary_from + salary_to)/2
    else:
        return None


def predict_rub_salary(vacancy):
    if vacancy['currency'] == 'RUR':
        if vacancy['from'] and vacancy['to'] is not None:
            return (vacancy['from'] + vacancy['to'])/2
        if vacancy['from'] is None:
            return 0.8*vacancy['to']
        if vacancy['to'] is None:
            return 1.2 * vacancy['from']
    else:
        return None


def parse_hh(languages):
    results_hh = {}
    params = {
        'User-Agent': 'api-test-agent',
        'area': 1,
        'period': 30,
        'per_page': 100
    }
    for language in languages:
        count = 0
        summary_salary = 0
        params['text'] = 'Разработчик ' + language
        response = requests.get('https://api.hh.ru/vacancies', params=params)
        response.raise_for_status()
        first_page = json.loads(response.text)
        for page in range(first_page['pages']):
            params['page'] = page
            response = requests.get('https://api.hh.ru/vacancies',
                                    params=params)
            response.raise_for_status()
            vacancies = json.loads(response.text)
            for vacancy in vacancies['items']:
                if vacancy['salary'] is not None and \
                        vacancy['salary']['currency'] == 'RUR':
                    summary_salary += predict_salary(vacancy['salary']['from'],
                                                     vacancy['salary']['to'])
                    count += 1
        result_hh = {
            'vacancies_found': first_page['found'],
            'vacancies_processed': count,
            'average_salary': int(summary_salary / count)
        }
        results_hh[language] = result_hh
    return results_hh


def parse_sj(languages, app_key_sj):
    results_sj = {}
    params = {
        'count': 100,
        'town': 4,
        'catalogues': 48,
        'app_key': app_key_sj
    }
    for language in languages:
        count = 0
        summary_salary = 0
        params['keyword'] = language
        response = requests.get('https://api.superjob.ru/2.0/vacancies/',
                                params=params)
        response.raise_for_status()
        first_page = json.loads(response.text)
        for page in range(int((first_page['total']/params['count']+1))):
            params['page'] = page
            response = requests.get('https://api.superjob.ru/2.0/vacancies/',
                                    params=params)
            response.raise_for_status()
            vacancies = json.loads(response.text)
            for vacancy in vacancies['objects']:
                if vacancy['payment_from'] or vacancy['payment_to'] != 0 and \
                        vacancy['currency'] == 'rub':
                    summary_salary += predict_salary(vacancy['payment_from'],
                                                     vacancy['payment_to'])
                    count += 1
        result_sj = {
            'vacancies_found': first_page['total'],
            'vacancies_processed': count,
            'average_salary': int(summary_salary / count)
        }
        results_sj[language] = result_sj
    return results_sj


def print_table(statistic, title):
    TABLE_DATA = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата']
    ]

    for language in statistic:
        TABLE_DATA.append([
            language,
            statistic[language]['vacancies_found'],
            statistic[language]['vacancies_processed'],
            statistic[language]['average_salary']
        ])
    table_instance = SingleTable(TABLE_DATA, title)
    print(table_instance.table)
    print()


def main():
    load_dotenv()
    app_key_sj=os.environ['APP_KEY_SJ']
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
    statistic_hh = parse_hh(languages)
    statistic_sj = parse_sj(languages, app_key_sj)
    title_hh = 'HeadHunter Moscow'
    title_sj = 'SuperJob Moscow'
    print_table(statistic_hh, title_hh)
    print_table(statistic_sj, title_sj)

if __name__ == '__main__':
    main()
