import os
import json
import time
import requests
import datetime
import schedule

interval = 5

def run():
    # Получаем бедолаг
    s_date = str(datetime.datetime.now().date())
    print(f"Начинаю сбор бедлаг за {s_date}")
    data = {
        'api_key': '1nkG7UQQJ264b0eb1dda5ce9.26287562',
        'limit': 300,
        'from_date': s_date
    }
    r = requests.post('https://gainnet.ru/api/v1/leads', data=data)
    response = json.loads(r.text)

    bedolagi = response.get('answer')

    print(f'Собрал бедолаг: {len(bedolagi)}')
    ids = []
    if os.path.exists('db.json'):
        print('Читаю базу обработанных бедолаг')
        with open('db.json', 'r') as db_h:
            ids = json.load(db_h)

    # filter already sent
    print('Фильтрую')
    bedolagi = list(filter(lambda x: x['id'] not in ids, bedolagi))
    print(f'Бедолаг после фильтра - {len(bedolagi)}')

    def send(bedolaga):
        data = {
            'edata[name]': bedolaga.get('name', 'Не указано') or 'Не указано',
            'edata[phone]': bedolaga.get('phone', '') or 'no phone',
            'edata[question]': f'Хочет получить юридическую помощь: {bedolaga.get("text", "")}',
            'edata[cd-referral]': 'b3a02e39d06193ba9665438a08612a56',
            'edata[secret]': '1302feaa7661a9acf47b76c80a852e4c'
        }
        r = requests.post('https://leads-reception.feedot.com/api/v1/partner-leads', data=data)
        return r
        

    # Засылаем бедолаг
    allow_send = 20  # avoid suspicious activity 
    sent = 0
    for b in bedolagi:
        s = send(b)
        if not s.status_code in [200, 201, 204]:
            print(f"Бедогала с ID {b['id']} отправлен неуспешно")
            print(s.reason)
            print(s.text)

        sent += 1
        ids.append(b['id'])
        with open('db.json', 'w') as db_h:
            db_h.write(json.dumps(ids))

        if sent == allow_send:
            print(f'Отправил {allow_send} бедолаг, больше не буду во избежание проблем')
            break

    print(f'Отправлено: {sent}')
    print(f'Я попробую еще через {interval} минут')

run()
schedule.every(interval).minutes.do(run)
while True:
    schedule.run_pending()
    time.sleep(1)