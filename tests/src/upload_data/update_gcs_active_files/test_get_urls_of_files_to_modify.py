import datetime as dt
import pandas as pd
from upload_data.update.get_updates_pages import (
    get_new_pages,
    get_modified_pages,
    get_deleted_pages,
)


active_pages = [
    [
        983053,
        dt.datetime.now() - dt.timedelta(days=1),
        dt.datetime.now() - dt.timedelta(days=1),
        "same"
    ],
    [
        1933313,
        dt.datetime.now() - dt.timedelta(days=1),
        dt.datetime.now(),
        "added and modified"
    ],
    [
        786434,
        dt.datetime.now(),
        dt.datetime.now(),
        "added"
    ],
    [
        589826,
        dt.datetime.now() - dt.timedelta(days=1),
        dt.datetime.now() - dt.timedelta(minutes=10),
        "modified"
    ],
]

previous_pages = [
    [
        983053,
        dt.datetime.now() - dt.timedelta(days=1),
        dt.datetime.now() - dt.timedelta(days=1),
        "same"
    ],
    [
        589826,
        dt.datetime.now() - dt.timedelta(days=1),
        dt.datetime.now() - dt.timedelta(days=1),
        "modified"
    ],
    [
        589838,
        dt.datetime.now() - dt.timedelta(days=4),
        dt.datetime.now() - dt.timedelta(days=4),
        "deleted"
    ]
]


df_active_pages = pd.DataFrame(active_pages, columns=['page_id', 'created_at', 'modified_at', 'status'])
df_previous_pages = pd.DataFrame(previous_pages, columns=['page_id', 'created_at', 'modified_at', 'status'])


def test_found_new_pages():
    df_new = get_new_pages(df_active_pages, df_previous_pages)
    assert df_new['page_id'].values[0] == 1933313
    assert df_new['page_id'].values[1] == 786434


def test_modified_pages():
    df_modified = get_modified_pages(df_active_pages, df_previous_pages)
    assert df_modified['page_id'].values[0] == 589826


def test_deleted_pages():
    df_deleted = get_deleted_pages(df_active_pages, df_previous_pages)
    assert df_deleted['page_id'].values[0] == 589838
