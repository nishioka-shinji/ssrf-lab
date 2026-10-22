# SSRF ラボ シーケンス図

## ① 対策前（SSRF 成立）

```mermaid
sequenceDiagram
    actor Attacker as 攻撃者(ホスト)
    participant App as vuln-app:8080
    participant Internal as internal-service(非公開)

    Note over Attacker,Internal: 攻撃者は internal-service に直接は届かない
    Attacker-xInternal: 直アクセス → 到達不可

    Attacker->>App: GET /preview?url=http://internal-service/
    App->>Internal: requests.get(url) ※URL未検証で代理アクセス
    Internal-->>App: 内部ページ(og:* にシークレット)
    App-->>Attacker: プレビューとして内部情報を返す 💥漏洩
```

## ② 対策後（Smokescreen が遮断）

```mermaid
sequenceDiagram
    actor Attacker as 攻撃者(ホスト)
    participant App as vuln-app:8080
    participant Proxy as smokescreen:4750
    participant Internal as internal-service(private 172.20.x)
    participant Ext as 外部サイト(github.com)

    Attacker->>App: GET /preview?url=http://internal-service/
    App->>Proxy: requests が HTTP_PROXY 経由で送信
    Proxy->>Proxy: URL をDNS解決 → 172.20.x はプライベート帯
    Proxy--xApp: Deny: Private Range (407) 🚫
    App-->>Attacker: 空の結果(漏洩なし)

    Note over Attacker,Ext: 正当な外部宛は通る
    Attacker->>App: GET /preview?url=https://github.com
    App->>Proxy: HTTP_PROXY 経由
    Proxy->>Proxy: 解決先はグローバルユニキャスト → allow
    Proxy->>Ext: 代理アクセス
    Ext-->>Proxy: OGP
    Proxy-->>App: OGP
    App-->>Attacker: プレビュー正常表示 ✅
```

## 要点

- 対策前は App が無検証で内部に代理アクセスしてしまう（SSRF の本質）。
- 対策後は App→外部の間に smokescreen が挟まり、DNS 解決後の IP で判定する。
  プライベート/ループバック/リンクローカル帯は Deny、グローバルユニキャストは Allow。
- アプリのコードは変更せず、環境変数 HTTP(S)_PROXY で requests を経由させているだけ。
```
