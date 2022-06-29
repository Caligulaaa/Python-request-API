import requests
import time
from datetime import date, datetime, timedelta
import json
# import csv

def get_data_from_yangex_direct():
    # need const
    url = 'https://api.direct.yandex.com/json/v5/reports'
    token = 'TOKEN'
    start = time.time()

    # all fields  https://yandex.ru/dev/direct/doc/reports/fields-list.html
    fields_name = ["Date", "AdGroupName", "Criteria", "CampaignName", "Cost", "Clicks", "Impressions"]



    #https://yandex.ru/dev/direct/doc/reports/spec.html
    #create need json request from url
    #schem from https://yandex.ru/dev/direct/doc/reports/fields-list.html needs ReportType
    json = {
        'params': {
            'SelectionCriteria': {
                'DateFrom': '2022-06-20',
                'DateTo': '2022-06-28',
            },

            'FieldNames': fields_name,

            'ReportName': 'report-name',
            'ReportType': 'CRITERIA_PERFORMANCE_REPORT',
            'DateRangeType': 'CUSTOM_DATE',
            'Format': 'TSV',
            'IncludeVAT': 'YES',
        }
    }

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, headers=headers, json=json)
    status = response.status_code

    text_to_data = None,
    if status == 200:
        text_to_data = response.text
        print('data get')

    # if report != 200  post new report afte 500 sec request off 
    retry = int(response.headers.get('retryIn', 5))
    while status != 200:
        time.sleep(retry)
        response = requests.post(url, headers=headers, json=json)
        status = response.status_code
        try:
            retry = int(response.headers.get('retryIn'))
            print(f'retry in {retry} seconds')
        except:
            pass

        if status == 200:
            text_to_data = response.text
            break
        elif str(status).startswith('4') or str(status).startswith('5'):
            print(f'status: {status}, text: {response.text}')
        else:
            print(status)

        if time.time() - start > 500:
            print('very very slow')
            exit()

    # get report json if code 200
    if text_to_data:
        try:
            data = text_to_data.split('\n')
            data = [dict(zip(fields_name, row.strip().split('\t'))) for row in data[2:-2]]
            print(f'{len(data)} rows')

            for row_dict in data[-100:]:
                print(row_dict)

            # #write to csv all rows from json data
            # with open('data.csv', 'w') as csvfile:
            #     writer = csv.DictWriter(csvfile, fieldnames = fields_name)
            #     writer.writeheader()
            #     writer.writerows(data)

        except Exception as e:
            print(f'error: {e}')
    else:
        print('NO DATA')

    print(f'request has {time.time() - start} sec')


if __name__ == "__main__":
    get_data_from_yangex_direct()