# ssrf-lab

SSRF（Server-Side Request Forgery）の仕組みと対策を手を動かして学ぶための、
Docker で完結するローカル学習用ラボ。

> ⚠️ **このリポジトリは意図的に脆弱なコードを含みます。**
> 隔離されたローカル環境でのみ使用してください。インターネットに公開したり、
> 本番ネットワークに接続しないこと。含まれる「シークレット」はすべて
> `THIS-IS-A-FAKE-DUMMY-VALUE` のような明らかなダミーで、実在しません。

## 構成

| サービス | 役割 |
|---|---|
| `vuln-app` (ホスト :8080) | ユーザー指定 URL を無検証で取得する脆弱な Flask アプリ。`/fetch` と OGP プレビュー `/preview` を持つ |
| `internal-service` | 外部に公開しない内部サービス（nginx）。本来 vuln-app 経由でしか到達できない |
| `smokescreen` | Stripe 製 SSRF 対策フォワードプロキシ。プライベート/ループバック/リンクローカル宛を拒否する |

## 使い方

```sh
docker compose up -d --build
```

### SSRF の再現（対策が効いていると遮断される）

```sh
# 正常系: 外部サイトの OGP プレビュー
curl "http://localhost:8080/preview?url=https://github.com"

# SSRF 試行: 内部サービスを踏み台取得 → smokescreen が Deny
curl "http://localhost:8080/preview?url=http://internal-service/"

# ループバック試行 → Deny
curl "http://localhost:8080/fetch?url=http://127.0.0.1:5000/"
```

smokescreen の判定ログ:

```sh
docker compose logs smokescreen | grep CANONICAL-PROXY-DECISION
```

### 対策なしの挙動を見たい場合

`docker-compose.yml` の `vuln-app` から `HTTP_PROXY` / `HTTPS_PROXY` を外して
再起動すると、`requests` がプロキシを経由しなくなり内部サービスへ到達できてしまう
（＝SSRF 成立）。対策ありと比較すること。

## 対策のポイント

- アプリのコードは変更していない。環境変数 `HTTP(S)_PROXY` で `requests` の
  外向き通信を smokescreen に強制しているだけ。
- smokescreen は **DNS 解決後の IP** で判定するため、外部名が内部 IP に解決される
  DNS リバインディング系も解決後 IP で弾ける。
- 既定でグローバルユニキャストのみ許可。プライベート/ループバック/リンクローカルは拒否。

図は [`DIAGRAM.md`](./DIAGRAM.md)（対策前後のシーケンス図）。

## 片付け

```sh
docker compose down
```
