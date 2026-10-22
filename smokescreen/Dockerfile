FROM golang:1.25-alpine AS build
RUN apk add --no-cache git
# Stripe 製 SSRF 対策フォワードプロキシをソースからビルド
RUN go install github.com/stripe/smokescreen@latest

FROM alpine:3.20
COPY --from=build /go/bin/smokescreen /usr/local/bin/smokescreen
COPY config.yaml /etc/smokescreen/config.yaml
EXPOSE 4750
# デフォルトでプライベート/ループバック/リンクローカル宛を拒否する。
# 明示許可は config.yaml の allow_ranges / allow_addresses で行う。
CMD ["smokescreen", "--config-file", "/etc/smokescreen/config.yaml"]
