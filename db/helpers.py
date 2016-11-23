import os, requests, json, time, datetime
import numpy as np
from mongo_schemata import *

opentsdb_url = "http://" \
        + os.environ.get("OPENTSDB_HOST") \
        + ":" + os.environ.get("OPENTSDB_PORT") \
        + "/api/"


def get_ticker_list(q = ''):
    tickers = [stock['ticker'] for stock in Stock.objects(ticker__contains = q)]
    return sorted(tickers)


def check_user(username):
    if User.objects(name = username).first() == None:
        return False
    else:
        return True


def create_user(name, email, password):
    u = User(name = name,
             email = email, 
             password = password)
    u.save()
    print('creating')
    return u


def create_portfolio(username, name, tickers):
    u = User.objects(name = username).first()
    s = Stock.objects(ticker__in = tickers.split(","))
    p = Portfolio(name = name,
                  stocks = s)
    p.save()
    u.portfolios.append(p)
    u.save()
    return p.id


def get_portfolio(portfolio_id):
    return Portfolio.objects(id = portfolio_id).first()


def opentsdb_query(companies, metrics, since):
    n = len(companies) * len(metrics)
    query_template = {
        "aggregator": "sum",
        "rate": "false",
        "tags": {}
    }
    queries = [query_template] * n
    for i, met in enumerate(metrics):
        for j, com in enumerate(companies):
            queries[i + j]['metric'] = com + '.' + met
            queries[i + j]['rate'] = 'false'
            queries[i + j]['tags'] = { 'company': com }

    request_data = {
        "start": since,
        "queries": queries
    }
    print request_data
    request_url = opentsdb_url + "query?summary=true&details=true"
    response = requests.post(request_url, data = json.dumps(request_data))
    # really need some better error handling here
    if not response.ok:
        raise RuntimeError(response.content)

    response_dict = response.json()
    if 'error' in response_dict:
        return {'success': False, 'error': response_dict['error']['message']}
    elif len(response_dict) == 0:
        return {'success': False, 'error': 'Empty response.'}
    else:
        return {'success': True, 'data': response_dict}


def create_mongodb_covar_matrix(mat, names):
    it = np.nditer(mat, flags=['f_index','multi_index'])
    while not it.finished:
        if it.multi_index[0] <= it.multi_index[1]:
            print('Create covariance cell: ' + str(it[0]))
            MatrixItem.objects(i = names[it.multi_index[0]],
                               j = names[it.multi_index[1]]
                              ).update_one(set__v = it[0], upsert = True)

        it.iternext()

    return " ".join([(str(mi['i']) + str(mi['j']) + ": " + str(mi['v'])) for mi in MatrixItem.objects()])


def read_mongodb_covar_matrix(names):
    mis = MatrixItem.objects(i__in = names,
                             j__in = names)
    print(mis)
    return " ".join([(str(mi['i']) + str(mi['j']) + ": " + str(mi['v'])) for mi in mis])

