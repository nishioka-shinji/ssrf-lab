from flask import Flask, request, Response, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 学習用の脆弱なエンドポイント。
# ユーザーが渡した URL を検証せずそのままサーバー側で取得するため SSRF が成立する。
@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return "usage: /fetch?url=http://example.com", 400
    try:
        r = requests.get(url, timeout=5)
        return Response(r.content, status=r.status_code,
                        content_type=r.headers.get("content-type", "text/plain"))
    except Exception as e:
        return f"error: {e}", 502


# OGP プレビュー機能を模した脆弱なエンドポイント。
# ユーザーが貼った URL をサーバーが取得し og:* を抜き出して返す。
# URL を検証しないため /fetch と同様に SSRF が成立する。
@app.route("/preview")
def preview():
    url = request.args.get("url")
    if not url:
        return "usage: /preview?url=http://example.com", 400
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        og = {}
        for tag in soup.find_all("meta"):
            prop = tag.get("property", "")
            if prop.startswith("og:"):
                og[prop] = tag.get("content", "")
        if not og:
            title = soup.title.string if soup.title else ""
            og = {"title": title, "note": "no OGP tags; falling back to <title>"}
        return jsonify({"requested_url": url, "preview": og})
    except Exception as e:
        return f"error: {e}", 502


@app.route("/")
def index():
    return "Vulnerable SSRF demo app. Try /fetch?url=... or /preview?url=...\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
