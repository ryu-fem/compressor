#!/bin/sh
set -e

if [ -z "$TELEGRAM_API_ID" ] || [ -z "$TELEGRAM_API_HASH" ]; then
  echo "لازم تحط TELEGRAM_API_ID و TELEGRAM_API_HASH كمتغيرات بيئة (من https://my.telegram.org)"
  exit 1
fi

# شغّل سيرفر تليجرام المحلي في الخلفية
telegram-bot-api \
  --api-id="$TELEGRAM_API_ID" \
  --api-hash="$TELEGRAM_API_HASH" \
  --local \
  --dir=/data \
  --http-port=8081 &

TGAPI_PID=$!

# استنى شوية لحد ما السيرفر يبقى جاهز يستقبل طلبات
sleep 8

echo "===== DEBUG: raw response from local telegram-bot-api ====="
curl -sS "http://127.0.0.1:8081/bot${BOT_TOKEN}/getMe" || echo "curl failed to reach local server"
echo ""
echo "============================================================"

export TELEGRAM_API_BASE_URL="http://127.0.0.1:8081/bot"
export TELEGRAM_API_BASE_FILE_URL="http://127.0.0.1:8081/file/bot"
export TELEGRAM_LOCAL_MODE="1"

# شغّل البوت في المقدمة (عشان لو وقع، الكونتينر كله يعتبر واقع ويعيد Railway تشغيله)
python bot.py

# لو البوت وقف لأي سبب، اقفل سيرفر تليجرام برضه
kill "$TGAPI_PID" 2>/dev/null || true
