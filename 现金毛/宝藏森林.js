var token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3ZWJtYW4ub3JhbmdlRmFuLmNuIiwiYXVkIjoid2VibWFuLm9yYW5nZUZhbi5jbiIsImlhdCI6MTc1MjY2MzMxOSwibmJmIjoxNzUyNjYzMzE5LCJleHAiOjE3NTI5MjI1MTksImV4dGVuZCI6eyJpZCI6MTA1MTgsImNsaWVudCI6Ik1PQklMRSIsImludml0ZV9jb2RlIjoiNTgwMjc5NSJ9fQ.MCOySWt1SsajNQXLfSqJioWohqgNvTTUfitJet8d74c"
while (true) {
    var temp = http.postJson("https://app.hzp4687.com/app/fighting/attack", {}, {
        "headers": {
            "Accept-Encoding": "identity",
            "Content-Type": "application/json",
            "Authorization": "Bearer "+token,//eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3ZWJtYW4ub3JhbmdlRmFuLmNuIiwiYXVkIjoid2VibWFuLm9yYW5nZUZhbi5jbiIsImlhdCI6MTc1MjY2Mjg3NCwibmJmIjoxNzUyNjYyODc0LCJleHAiOjE3NTI5MjIwNzQsImV4dGVuZCI6eyJpZCI6MTA1MTgsImNsaWVudCI6Ik1PQklMRSIsImludml0ZV9jb2RlIjoiNTgwMjc5NSJ9fQ.re6oxabhegRMSOdGyGcKy8PWx0xJHYGPYwX2EXgE8jw", //"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3ZWJtYW4ub3JhbmdlRmFuLmNuIiwiYXVkIjoid2VibWFuLm9yYW5nZUZhbi5jbiIsImlhdCI6MTc1MjY2MjQ4NCwibmJmIjoxNzUyNjYyNDg0LCJleHAiOjE3NTI5MjE2ODQsImV4dGVuZCI6eyJpZCI6MTA1MTgsImNsaWVudCI6Ik1PQklMRSIsImludml0ZV9jb2RlIjoiNTgwMjc5NSJ9fQ.MwA1ty3JqI1McbiwUnZ0pLQ2wRMCcE2qY1NPvJo__XE", //"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3ZWJtYW4ub3JhbmdlRmFuLmNuIiwiYXVkIjoid2VibWFuLm9yYW5nZUZhbi5jbiIsImlhdCI6MTc1MjY2MTcyMSwibmJmIjoxNzUyNjYxNzIxLCJleHAiOjE3NTI5MjA5MjEsImV4dGVuZCI6eyJpZCI6MTA1MTgsImNsaWVudCI6Ik1PQklMRSIsImludml0ZV9jb2RlIjoiNTgwMjc5NSJ9fQ.VCc7DMDC68jafx0jxSDqexo1s1kaodXzWlMCkfjONyg",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; PDYT20 Build/SP1A.210812.016)",
            "Host": "app.hzp4687.com",
            "Connection": "Keep-Alive",
            "Content-Length": "2"
        }
    }).body.json();
    if (temp.code == 200) {
        log("打怪成功获得金币 >>> " + temp.data.reward_props[0].num + "|金币余额 >>> " + temp.data.after_props[0].num);
    } else {
        log("没体力了观看视频补充体力")
        var temp = http.postJson("https://app.hzp4687.com/app/player/recover_sta", {}, {
            "headers": {
                "Accept-Encoding": "identity",
                "Content-Type": "application/json",
                "Authorization":"Bearer "+token,//eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3ZWJtYW4ub3JhbmdlRmFuLmNuIiwiYXVkIjoid2VibWFuLm9yYW5nZUZhbi5jbiIsImlhdCI6MTc1MjY2Mjg3NCwibmJmIjoxNzUyNjYyODc0LCJleHAiOjE3NTI5MjIwNzQsImV4dGVuZCI6eyJpZCI6MTA1MTgsImNsaWVudCI6Ik1PQklMRSIsImludml0ZV9jb2RlIjoiNTgwMjc5NSJ9fQ.re6oxabhegRMSOdGyGcKy8PWx0xJHYGPYwX2EXgE8jw", //"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3ZWJtYW4ub3JhbmdlRmFuLmNuIiwiYXVkIjoid2VibWFuLm9yYW5nZUZhbi5jbiIsImlhdCI6MTc1MjY2MjQ4NCwibmJmIjoxNzUyNjYyNDg0LCJleHAiOjE3NTI5MjE2ODQsImV4dGVuZCI6eyJpZCI6MTA1MTgsImNsaWVudCI6Ik1PQklMRSIsImludml0ZV9jb2RlIjoiNTgwMjc5NSJ9fQ.MwA1ty3JqI1McbiwUnZ0pLQ2wRMCcE2qY1NPvJo__XE",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; PDYT20 Build/SP1A.210812.016)",
                "Host": "app.hzp4687.com",
                "Connection": "Keep-Alive",
                "Content-Length": "2"
            }
        }).body.json();
        if (temp.code == 200) {
            log("观看视频成功获得体力 >>> " + temp.data.sta);
        } else {
            log(temp.msg)
            break;
        }
    }
    sleep(1000)
}