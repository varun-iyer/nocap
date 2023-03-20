import cProfile
import pandas as pd
import sqlite3
import csv


DATA = "./data"
COURTS = f"{DATA}/courts-2023-02-28.csv"
DOCKETS = f"{DATA}/dockets-2023-02-28.csv"
CLUSTERS = f"{DATA}/opinion-clusters-2023-02-28.csv"
CITATIONS = f"{DATA}/citation-map-2023-02-28.csv"
RANDOM_DOCKET_IDS = [int(no) for no in open(f"{DATA}/10k-docket-ids.csv").readlines()]

def load_pandas(fname=DOCKETS):
    try:
        return load_pandas.dockets_df
    except AttributeError:
        pass
    parse_dates = [
        'date_cert_granted',
        'date_cert_denied',
        'date_argued',
        'date_reargued',
        'date_reargument_denied',
        'date_filed',
        'date_terminated',
        'date_last_filing',
        'date_blocked'
    ]

    docket_type = {
        'appeal_from_str': 'string',
        'assigned_to_str': 'string',
        'referred_to_str': 'string',
        'case_name_short' : 'string',
        'case_name': 'string',
        'case_name_full': 'string',
        'court_id': 'string',
        'cause':'string',
        'nature_of_suit':'string',
        'jury_demand':'string',
        'jurisdiction_type':'string',
        'appellate_fee_status':'string',
        'appellate_case_type_information':'string',
        'mdl_status':'string',
        'filepath_ia':'string',
    }

    load_pandas.dockets_df = pd.concat(pd.read_csv(fname, dtype=docket_type, parse_dates=parse_dates, iterator=True, chunksize=10000))
    return load_pandas.dockets_df

def access_pandas(docket_ids: list=RANDOM_DOCKET_IDS):
    df = load_pandas()
    for dockid in docket_ids:
        df[df['id']==dockid]

def load_sqlite(fname=DOCKETS):
    try:
        return load_sqlite.dockets_db
    except AttributeError:
        pass
    db = sqlite3.connect(":memory:")
    load_sqlite.dockets_db = db
    cur = db.cursor()
    cur.execute("CREATE TABLE docket(id, date_terminated)")
    batch_size = 10000
    chunk = []
    with open(fname) as dockets:
        reader = csv.DictReader(dockets)
        for row in reader:
            chunk.append((row['id'], row['date_terminated']))
        if len(chunk) == batch_size:
            cur.executemany("INSERT INTO docket VALUES(?, ?)", data)
            db.commit()
            chunk = []
    return load_sqlite.dockets_db

def access_sqlite(docket_ids: list=RANDOM_DOCKET_IDS):
    db = load_sqlite()
    cur = db.cursor()
    for dockid in docket_ids:
        cur.execute("SELECT date_terminated FROM docket WHERE id=(?)", (dockid,)).fetchone()

def load_dict(fname=DOCKETS):
    try:
        return load_dict.dockets_dict
    except AttributeError:
        pass
    load_dict.dockets_dict = {}
    with open(fname) as dockets:
        reader = csv.DictReader(dockets)
        for row in reader:
            load_dict.dockets_dict[int(row['id'])] = row['date_terminated']
    return load_dict.dockets_dict

def access_dict(docket_ids: list=RANDOM_DOCKET_IDS):
    dict_ = load_dict()
    for dockid in docket_ids:
        a = dict_[dockid]

def profile_pandas():
    print("LOAD_PANDAS()")
    cProfile.run("load_pandas()")
    print("ACCESS_PANDAS()")
    cProfile.run("access_pandas()")
    del load_pandas.dockets_df

def profile_sqlite():
    print("LOAD_SQLITE()")
    cProfile.run("load_sqlite()")
    print("ACCESS_SQLITE()")
    cProfile.run("access_sqlite()")
    del load_sqlite.dockets_db

def profile_dict():
    print("LOAD_dict()")
    cProfile.run("load_dict()")
    print("ACCESS_dict()")
    cProfile.run("access_dict()")
    del load_dict.dockets_dict

profile_dict()
