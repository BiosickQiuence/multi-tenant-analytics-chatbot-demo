# Real curl demo transcript

Personal portfolio demo by Zhuangyi Qiu. Rule-based mode and synthetic data. All requests below were executed by curl against the live local FastAPI server. Only API-key text in displayed commands is masked. Responses are complete. The fixed analytics clock is 2026-11-10 12:00 UTC.

## 1. Acme — totals

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "totals last 7 days"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "c633ed7c-3a6b-431a-8e8b-e7819a4bde7a",
  "answer": "21 posts generated 7,813 engagements and 137,872 impressions. Engagement rate was 5.67%. Scope is instagram, tiktok, x, last 7 complete days. Synthetic demo data.",
  "intent": "totals",
  "template": "totals",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "posts": 21,
      "likes": 6266,
      "comments": 629,
      "shares": 918,
      "impressions": 137872,
      "engagements": 7813,
      "followers_gained": 489,
      "engagement_rate_pct": 5.67
    }
  ]
}
```

## 2. Acme — top posts

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "top posts on instagram last 7 days"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "17bab4a5-b4fc-48b1-9e25-e11057f928a4",
  "answer": "Showing 5 top posts by total engagements. The first is on instagram with 613 engagements. Scope is instagram, last 7 complete days. Synthetic demo data.",
  "intent": "top_posts",
  "template": "top_posts",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "e9de9f6b-b289-55b8-adfa-bdcc4dcafb01",
      "platform": "instagram",
      "posted_at": "2026-11-07T05:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 88",
      "likes": 513,
      "comments": 43,
      "shares": 57,
      "impressions": 7356,
      "engagements": 613,
      "engagement_rate_pct": 8.33
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "0b12339c-47f0-512d-a83c-e6c8fb1170cc",
      "platform": "instagram",
      "posted_at": "2026-11-04T20:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 85",
      "likes": 353,
      "comments": 12,
      "shares": 26,
      "impressions": 5083,
      "engagements": 391,
      "engagement_rate_pct": 7.69
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "69fc3f44-1fc5-5eda-8f86-978a6d8532a9",
      "platform": "instagram",
      "posted_at": "2026-11-09T11:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 90",
      "likes": 172,
      "comments": 58,
      "shares": 76,
      "impressions": 8568,
      "engagements": 306,
      "engagement_rate_pct": 3.57
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "59fd8709-525c-5e8d-864c-7e70d7d9ce66",
      "platform": "instagram",
      "posted_at": "2026-11-08T08:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 89",
      "likes": 143,
      "comments": 12,
      "shares": 62,
      "impressions": 3038,
      "engagements": 217,
      "engagement_rate_pct": 7.14
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "68211799-4144-59aa-9581-b833df4c9de2",
      "platform": "instagram",
      "posted_at": "2026-11-03T17:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 84",
      "likes": 75,
      "comments": 42,
      "shares": 63,
      "impressions": 1800,
      "engagements": 180,
      "engagement_rate_pct": 10.0
    }
  ]
}
```

## 3. Acme — platform follow-up

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "what about tiktok?", "session_id": "17bab4a5-b4fc-48b1-9e25-e11057f928a4"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "17bab4a5-b4fc-48b1-9e25-e11057f928a4",
  "answer": "Showing 5 top posts by total engagements. The first is on tiktok with 601 engagements. Scope is tiktok, last 7 complete days. Synthetic demo data.",
  "intent": "top_posts",
  "template": "top_posts",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "3d70bcea-0873-5f56-8014-7679a050886a",
      "platform": "tiktok",
      "posted_at": "2026-11-06T06:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 87",
      "likes": 492,
      "comments": 57,
      "shares": 52,
      "impressions": 7212,
      "engagements": 601,
      "engagement_rate_pct": 8.33
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "a3e5df35-ffe9-5a98-8ce0-d8598e71556f",
      "platform": "tiktok",
      "posted_at": "2026-11-09T15:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 90",
      "likes": 476,
      "comments": 20,
      "shares": 59,
      "impressions": 9435,
      "engagements": 555,
      "engagement_rate_pct": 5.88
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "ca5bcfa2-b256-5f08-ab65-6f4dfe156a58",
      "platform": "tiktok",
      "posted_at": "2026-11-04T00:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 85",
      "likes": 392,
      "comments": 6,
      "shares": 52,
      "impressions": 9900,
      "engagements": 450,
      "engagement_rate_pct": 4.55
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "0bcfb2c4-a712-50b3-ab05-53d7e952f035",
      "platform": "tiktok",
      "posted_at": "2026-11-07T09:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 88",
      "likes": 336,
      "comments": 14,
      "shares": 85,
      "impressions": 11310,
      "engagements": 435,
      "engagement_rate_pct": 3.85
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "8df762d1-5c2c-57e0-a115-6cb2502ba698",
      "platform": "tiktok",
      "posted_at": "2026-11-05T03:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 86",
      "likes": 189,
      "comments": 5,
      "shares": 40,
      "impressions": 6786,
      "engagements": 234,
      "engagement_rate_pct": 3.45
    }
  ]
}
```

## 4. Acme — date follow-up

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "and last month?", "session_id": "17bab4a5-b4fc-48b1-9e25-e11057f928a4"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "17bab4a5-b4fc-48b1-9e25-e11057f928a4",
  "answer": "Showing 5 top posts by total engagements. The first is on tiktok with 669 engagements. Scope is tiktok, last calendar month. Synthetic demo data.",
  "intent": "top_posts",
  "template": "top_posts",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "a270eafa-b098-554f-bc03-eca36535fb51",
      "platform": "tiktok",
      "posted_at": "2026-10-25T18:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 75",
      "likes": 535,
      "comments": 49,
      "shares": 85,
      "impressions": 11373,
      "engagements": 669,
      "engagement_rate_pct": 5.88
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "73b9572d-5d0f-5d00-8a4d-b186e4474364",
      "platform": "tiktok",
      "posted_at": "2026-10-29T06:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 79",
      "likes": 568,
      "comments": 35,
      "shares": 24,
      "impressions": 6897,
      "engagements": 627,
      "engagement_rate_pct": 9.09
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "08a85ea9-2096-5611-a8ff-17ac2f7c09c2",
      "platform": "tiktok",
      "posted_at": "2026-10-07T12:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 57",
      "likes": 538,
      "comments": 18,
      "shares": 65,
      "impressions": 18009,
      "engagements": 621,
      "engagement_rate_pct": 3.45
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "e1405ba7-962b-5943-a21a-10406ec14ede",
      "platform": "tiktok",
      "posted_at": "2026-10-31T12:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 81",
      "likes": 559,
      "comments": 30,
      "shares": 4,
      "impressions": 14825,
      "engagements": 593,
      "engagement_rate_pct": 4.0
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "d31e9078-226d-5527-ba39-faf33e3e1adf",
      "platform": "tiktok",
      "posted_at": "2026-10-26T21:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 76",
      "likes": 526,
      "comments": 47,
      "shares": 19,
      "impressions": 14208,
      "engagements": 592,
      "engagement_rate_pct": 4.17
    }
  ]
}
```

## 5. Bluebird — engagement rate

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_bluebird_****' -H 'Content-Type: application/json' --data-binary '{"message": "engagement rate by platform last month"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "c6669e60-3a14-4c6f-b54f-a3022890c2c0",
  "answer": "instagram leads at 5.56% engagement per impression, weighted across posts. Scope is instagram, tiktok, x, last calendar month. Synthetic demo data.",
  "intent": "engagement_rate",
  "template": "engagement_rate",
  "rows": [
    {
      "tenant_id": "d6458d54-3f04-5806-a299-be637a1baf2c",
      "platform": "instagram",
      "posts": 31,
      "likes": 12762,
      "comments": 878,
      "shares": 1306,
      "impressions": 268812,
      "engagements": 14946,
      "followers_gained": 574,
      "engagement_rate_pct": 5.56
    },
    {
      "tenant_id": "d6458d54-3f04-5806-a299-be637a1baf2c",
      "platform": "tiktok",
      "posts": 31,
      "likes": 10639,
      "comments": 1253,
      "shares": 1333,
      "impressions": 248998,
      "engagements": 13225,
      "followers_gained": 609,
      "engagement_rate_pct": 5.31
    },
    {
      "tenant_id": "d6458d54-3f04-5806-a299-be637a1baf2c",
      "platform": "x",
      "posts": 31,
      "likes": 12598,
      "comments": 945,
      "shares": 1414,
      "impressions": 288391,
      "engagements": 14957,
      "followers_gained": 614,
      "engagement_rate_pct": 5.19
    }
  ]
}
```

## 6. Bluebird — follower growth

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_bluebird_****' -H 'Content-Type: application/json' --data-binary '{"message": "follower growth this week"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "413d8132-bfcc-4ca6-9ec4-58cbbeedb2fd",
  "answer": "Posts were attributed 25 followers gained. Scope is instagram, tiktok, x, this week to the demo clock. Synthetic demo data.",
  "intent": "follower_growth",
  "template": "follower_growth",
  "rows": [
    {
      "tenant_id": "d6458d54-3f04-5806-a299-be637a1baf2c",
      "platform": "tiktok",
      "posts": 1,
      "followers_gained": 12
    },
    {
      "tenant_id": "d6458d54-3f04-5806-a299-be637a1baf2c",
      "platform": "x",
      "posts": 1,
      "followers_gained": 12
    },
    {
      "tenant_id": "d6458d54-3f04-5806-a299-be637a1baf2c",
      "platform": "instagram",
      "posts": 1,
      "followers_gained": 1
    }
  ]
}
```

## 7. Acme — posting time

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "best posting weekday and hour last month"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "394aeb68-c454-4d3d-be5a-b37b46a3b66d",
  "answer": "Sunday at 18:00 UTC had the highest mean engagements per post (669.00), based on 1 posts in that time bucket. Scope is instagram, tiktok, x, last calendar month. Synthetic demo data.",
  "intent": "best_posting_time",
  "template": "best_posting_time",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "weekday_number": 7,
      "weekday": "Sunday",
      "hour_utc": 18,
      "posts": 1,
      "average_engagements": 669.0
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "weekday_number": 3,
      "weekday": "Wednesday",
      "hour_utc": 16,
      "posts": 1,
      "average_engagements": 653.0
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "weekday_number": 7,
      "weekday": "Sunday",
      "hour_utc": 23,
      "posts": 1,
      "average_engagements": 653.0
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "weekday_number": 5,
      "weekday": "Friday",
      "hour_utc": 5,
      "posts": 1,
      "average_engagements": 633.0
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "weekday_number": 2,
      "weekday": "Tuesday",
      "hour_utc": 2,
      "posts": 1,
      "average_engagements": 630.0
    }
  ]
}
```

## 8. Acme — comparison

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "compare instagram vs tiktok last month"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "28d76bb7-4e2a-4c3c-aadf-daa8450b631d",
  "answer": "Compared platforms. instagram had 31 posts and 5.83% engagement rate. tiktok had 31 posts and 5.00% engagement rate. Scope is instagram, tiktok, last calendar month. Synthetic demo data.",
  "intent": "compare_platforms",
  "template": "compare_platforms",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "platform": "instagram",
      "posts": 31,
      "likes": 9062,
      "comments": 1145,
      "shares": 1242,
      "impressions": 196257,
      "engagements": 11449,
      "followers_gained": 589,
      "engagement_rate_pct": 5.83
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "platform": "tiktok",
      "posts": 31,
      "likes": 10847,
      "comments": 1062,
      "shares": 1614,
      "impressions": 270524,
      "engagements": 13523,
      "followers_gained": 602,
      "engagement_rate_pct": 5.0
    }
  ]
}
```

## 9. Acme — worst posts

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "worst posts last 7 days"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "e38581c0-3afd-49de-bec2-0af0b34049d3",
  "answer": "Showing 5 worst posts by total engagements. The first is on tiktok with 105 engagements. Scope is instagram, tiktok, x, last 7 complete days. Synthetic demo data.",
  "intent": "worst_posts",
  "template": "worst_posts",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "878172f7-135c-59da-9da9-28e945d14fc7",
      "platform": "tiktok",
      "posted_at": "2026-11-08T12:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 89",
      "likes": 62,
      "comments": 20,
      "shares": 23,
      "impressions": 1470,
      "engagements": 105,
      "engagement_rate_pct": 7.14
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "4b9b6a43-7986-5c3e-bca7-811bb9c3ea6e",
      "platform": "tiktok",
      "posted_at": "2026-11-03T21:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee tiktok post 84",
      "likes": 48,
      "comments": 61,
      "shares": 31,
      "impressions": 1260,
      "engagements": 140,
      "engagement_rate_pct": 11.11
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "69ef7fa3-b465-5f04-8613-1207671decfe",
      "platform": "instagram",
      "posted_at": "2026-11-06T02:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 87",
      "likes": 81,
      "comments": 61,
      "shares": 5,
      "impressions": 1470,
      "engagements": 147,
      "engagement_rate_pct": 10.0
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "ffc657d8-7172-5fbb-ac27-a09ecc9491e7",
      "platform": "instagram",
      "posted_at": "2026-11-05T23:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 86",
      "likes": 95,
      "comments": 3,
      "shares": 50,
      "impressions": 3256,
      "engagements": 148,
      "engagement_rate_pct": 4.55
    },
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "id": "68211799-4144-59aa-9581-b833df4c9de2",
      "platform": "instagram",
      "posted_at": "2026-11-03T17:00:00+00:00",
      "caption": "[SYNTHETIC] Acme Coffee instagram post 84",
      "likes": 75,
      "comments": 42,
      "shares": 63,
      "impressions": 1800,
      "engagements": 180,
      "engagement_rate_pct": 10.0
    }
  ]
}
```

## 10. Acme — local pgvector help

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: demo_acme_****' -H 'Content-Type: application/json' --data-binary '{"message": "what can you answer?"}' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "session_id": "c65da21a-8c00-4786-9e89-d94c6aad6e13",
  "answer": "I can report totals, top posts, worst posts, engagement rates, follower growth, best posting times, and comparisons between two platforms. Try last 7 days, last month, or this week. All data is synthetic.",
  "intent": "help",
  "template": "help_faq",
  "rows": [
    {
      "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
      "question": "What can you answer? Help capabilities analytics",
      "answer": "I can report totals, top posts, worst posts, engagement rates, follower growth, best posting times, and comparisons between two platforms. Try last 7 days, last month, or this week. All data is synthetic.",
      "cosine_distance": 0.24407104385110834
    }
  ]
}
```

## 11. Acme cannot read Bluebird history

```sh
curl --silent --show-error --max-time 20 -X GET http://127.0.0.1:8000/sessions/c6669e60-3a14-4c6f-b54f-a3022890c2c0 -H 'X-API-Key: demo_acme_****' --write-out '
%{http_code}'
```

HTTP 404

```json
{
  "detail": "Session not found."
}
```

## 12. Unknown key is rejected

```sh
curl --silent --show-error --max-time 20 -X POST http://127.0.0.1:8000/chat -H 'X-API-Key: unknown_****' -H 'Content-Type: application/json' --data-binary '{"message": "totals last 7 days"}' --write-out '
%{http_code}'
```

HTTP 401

```json
{
  "detail": "Missing or unknown X-API-Key."
}
```

## 13. Acme — six-message follow-up history

```sh
curl --silent --show-error --max-time 20 -X GET http://127.0.0.1:8000/sessions/17bab4a5-b4fc-48b1-9e25-e11057f928a4 -H 'X-API-Key: demo_acme_****' --write-out '
%{http_code}'
```

HTTP 200

```json
{
  "id": "17bab4a5-b4fc-48b1-9e25-e11057f928a4",
  "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
  "created_at": "2026-11-10T05:41:26.822160+00:00",
  "last_context": {
    "end": "2026-11-01T00:00:00+00:00",
    "start": "2026-10-01T00:00:00+00:00",
    "intent": "top_posts",
    "period": "last calendar month",
    "platforms": [
      "tiktok"
    ]
  },
  "messages": [
    {
      "role": "user",
      "content": "top posts on instagram last 7 days",
      "intent": "top_posts",
      "template": "top_posts",
      "rows": [],
      "created_at": "2026-11-10T05:41:26.823665+00:00"
    },
    {
      "role": "assistant",
      "content": "Showing 5 top posts by total engagements. The first is on instagram with 613 engagements. Scope is instagram, last 7 complete days. Synthetic demo data.",
      "intent": "top_posts",
      "template": "top_posts",
      "rows": [
        {
          "id": "e9de9f6b-b289-55b8-adfa-bdcc4dcafb01",
          "likes": 513,
          "shares": 57,
          "caption": "[SYNTHETIC] Acme Coffee instagram post 88",
          "comments": 43,
          "platform": "instagram",
          "posted_at": "2026-11-07T05:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 613,
          "impressions": 7356,
          "engagement_rate_pct": 8.33
        },
        {
          "id": "0b12339c-47f0-512d-a83c-e6c8fb1170cc",
          "likes": 353,
          "shares": 26,
          "caption": "[SYNTHETIC] Acme Coffee instagram post 85",
          "comments": 12,
          "platform": "instagram",
          "posted_at": "2026-11-04T20:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 391,
          "impressions": 5083,
          "engagement_rate_pct": 7.69
        },
        {
          "id": "69fc3f44-1fc5-5eda-8f86-978a6d8532a9",
          "likes": 172,
          "shares": 76,
          "caption": "[SYNTHETIC] Acme Coffee instagram post 90",
          "comments": 58,
          "platform": "instagram",
          "posted_at": "2026-11-09T11:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 306,
          "impressions": 8568,
          "engagement_rate_pct": 3.57
        },
        {
          "id": "59fd8709-525c-5e8d-864c-7e70d7d9ce66",
          "likes": 143,
          "shares": 62,
          "caption": "[SYNTHETIC] Acme Coffee instagram post 89",
          "comments": 12,
          "platform": "instagram",
          "posted_at": "2026-11-08T08:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 217,
          "impressions": 3038,
          "engagement_rate_pct": 7.14
        },
        {
          "id": "68211799-4144-59aa-9581-b833df4c9de2",
          "likes": 75,
          "shares": 63,
          "caption": "[SYNTHETIC] Acme Coffee instagram post 84",
          "comments": 42,
          "platform": "instagram",
          "posted_at": "2026-11-03T17:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 180,
          "impressions": 1800,
          "engagement_rate_pct": 10.0
        }
      ],
      "created_at": "2026-11-10T05:41:26.824106+00:00"
    },
    {
      "role": "user",
      "content": "what about tiktok?",
      "intent": "top_posts",
      "template": "top_posts",
      "rows": [],
      "created_at": "2026-11-10T05:41:26.837225+00:00"
    },
    {
      "role": "assistant",
      "content": "Showing 5 top posts by total engagements. The first is on tiktok with 601 engagements. Scope is tiktok, last 7 complete days. Synthetic demo data.",
      "intent": "top_posts",
      "template": "top_posts",
      "rows": [
        {
          "id": "3d70bcea-0873-5f56-8014-7679a050886a",
          "likes": 492,
          "shares": 52,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 87",
          "comments": 57,
          "platform": "tiktok",
          "posted_at": "2026-11-06T06:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 601,
          "impressions": 7212,
          "engagement_rate_pct": 8.33
        },
        {
          "id": "a3e5df35-ffe9-5a98-8ce0-d8598e71556f",
          "likes": 476,
          "shares": 59,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 90",
          "comments": 20,
          "platform": "tiktok",
          "posted_at": "2026-11-09T15:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 555,
          "impressions": 9435,
          "engagement_rate_pct": 5.88
        },
        {
          "id": "ca5bcfa2-b256-5f08-ab65-6f4dfe156a58",
          "likes": 392,
          "shares": 52,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 85",
          "comments": 6,
          "platform": "tiktok",
          "posted_at": "2026-11-04T00:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 450,
          "impressions": 9900,
          "engagement_rate_pct": 4.55
        },
        {
          "id": "0bcfb2c4-a712-50b3-ab05-53d7e952f035",
          "likes": 336,
          "shares": 85,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 88",
          "comments": 14,
          "platform": "tiktok",
          "posted_at": "2026-11-07T09:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 435,
          "impressions": 11310,
          "engagement_rate_pct": 3.85
        },
        {
          "id": "8df762d1-5c2c-57e0-a115-6cb2502ba698",
          "likes": 189,
          "shares": 40,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 86",
          "comments": 5,
          "platform": "tiktok",
          "posted_at": "2026-11-05T03:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 234,
          "impressions": 6786,
          "engagement_rate_pct": 3.45
        }
      ],
      "created_at": "2026-11-10T05:41:26.837667+00:00"
    },
    {
      "role": "user",
      "content": "and last month?",
      "intent": "top_posts",
      "template": "top_posts",
      "rows": [],
      "created_at": "2026-11-10T05:41:26.849423+00:00"
    },
    {
      "role": "assistant",
      "content": "Showing 5 top posts by total engagements. The first is on tiktok with 669 engagements. Scope is tiktok, last calendar month. Synthetic demo data.",
      "intent": "top_posts",
      "template": "top_posts",
      "rows": [
        {
          "id": "a270eafa-b098-554f-bc03-eca36535fb51",
          "likes": 535,
          "shares": 85,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 75",
          "comments": 49,
          "platform": "tiktok",
          "posted_at": "2026-10-25T18:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 669,
          "impressions": 11373,
          "engagement_rate_pct": 5.88
        },
        {
          "id": "73b9572d-5d0f-5d00-8a4d-b186e4474364",
          "likes": 568,
          "shares": 24,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 79",
          "comments": 35,
          "platform": "tiktok",
          "posted_at": "2026-10-29T06:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 627,
          "impressions": 6897,
          "engagement_rate_pct": 9.09
        },
        {
          "id": "08a85ea9-2096-5611-a8ff-17ac2f7c09c2",
          "likes": 538,
          "shares": 65,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 57",
          "comments": 18,
          "platform": "tiktok",
          "posted_at": "2026-10-07T12:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 621,
          "impressions": 18009,
          "engagement_rate_pct": 3.45
        },
        {
          "id": "e1405ba7-962b-5943-a21a-10406ec14ede",
          "likes": 559,
          "shares": 4,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 81",
          "comments": 30,
          "platform": "tiktok",
          "posted_at": "2026-10-31T12:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 593,
          "impressions": 14825,
          "engagement_rate_pct": 4.0
        },
        {
          "id": "d31e9078-226d-5527-ba39-faf33e3e1adf",
          "likes": 526,
          "shares": 19,
          "caption": "[SYNTHETIC] Acme Coffee tiktok post 76",
          "comments": 47,
          "platform": "tiktok",
          "posted_at": "2026-10-26T21:00:00+00:00",
          "tenant_id": "91d70aec-239e-52ea-8667-9123266de076",
          "engagements": 592,
          "impressions": 14208,
          "engagement_rate_pct": 4.17
        }
      ],
      "created_at": "2026-11-10T05:41:26.849786+00:00"
    }
  ]
}
```
