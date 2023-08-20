# flaskモジュールからFlaskクラスをインポート
from flask import Flask, render_template, redirect

import pandas as pd
import datetime


CSV_URL = "https://raw.githubusercontent.com/HB-enpitsu/99-imabari-bot/main/latest.csv"

CACHE_TIMEOUT = datetime.timedelta(minutes=30)
cache = pd.DataFrame()
cache_timestamp = None

# Flaskクラスをインスタンス化してapp変数に代入
app = Flask(__name__)


def fetch_data():
    global cache, cache_timestamp

    if not cache.empty and (datetime.datetime.now() - cache_timestamp) < CACHE_TIMEOUT:
        return cache

    cache = pd.read_csv(CSV_URL, parse_dates=[0])
    cache_timestamp = datetime.datetime.now()

    return cache


# 今日を表示
@app.route("/")
def today_get():
    df = fetch_data()

    dt_now = pd.Timestamp.now(tz="Asia/Tokyo").tz_localize(None)
    dt_ytd = dt_now - pd.Timedelta(days=1)

    dt_830 = dt_now.replace(hour=8, minute=30, second=0, microsecond=0)

    if dt_now >= dt_830:
        df_today = df[df["date"].dt.date == dt_now.date()].copy()
    else:
        df_today = df[
            (df["date"].dt.date == dt_now.date())
            | (
                (df["date"].dt.date == dt_ytd.date())
                & (df["time"].str.contains("翌日", na=False))
            )
        ].copy()

    df_today["display"] = "show"
    df_today["display"].mask(
        (df_today["date"].dt.date == dt_now.date()) & (df_today["type"] != "指定なし"),
        "hide",
        inplace=True,
    )

    posts_by_hosp = df_today.groupby("date").apply(
        lambda x: x.to_dict(orient="records")
    )

    return render_template("index.html", posts_by_hosp=posts_by_hosp)


# 今月を表示
@app.route("/list")
def month_get():
    df_month = fetch_data()

    posts_by_hosp = df_month.groupby("date").apply(
        lambda x: x.to_dict(orient="records")
    )

    return render_template("list.html", posts_by_hosp=posts_by_hosp)


# お知らせを表示
@app.route("/info")
def link_get():
    # 広報いまばりのURL生成のために年月を作成
    dt_now = datetime.datetime.now()
    return render_template("info.html", post_date=f"{dt_now:%Y%m}")


# 404エラーは今日へ移動
@app.errorhandler(404)
def page_not_found(error):
    return redirect("/")


# スクリプトとして直接実行した場合
if __name__ == "__main__":
    # FlaskのWEBアプリケーションを起動
    app.run(debug=True)

    # 外部アクセス可
    # app.run(debug=True, host="0.0.0.0", port=5050)
