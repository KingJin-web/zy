import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpUtil;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.alibaba.fastjson2.annotation.JSONField;
import lombok.Data;

import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * rio强爽
 * 配合我这个工具：https://tool.itmowei.cn/otherTool/rioSignIn.html
 * 自动签到+自动发帖
 *
 * @author Mo
 * @date 2024/08/15
 */
public class RIO强爽自动扫码抽奖评价 {

    //你的token，复制整行，带Bearer开头
    private static final String token = "";

    //串码，多个用回车隔开
    private static final String cap = "";

    public static void main(String[] args) throws InterruptedException {
        String url = "https://club.rioalc.com/api/miniprogram/scan-code";
        List<String> capList = Arrays.asList(cap.split("\n"));
        for (String code : capList) {
            System.out.println("延迟3秒");
            Thread.sleep(3000L);
            System.out.println("------------------------------");
            System.out.println("当前码: " + code);
            HttpRequest post = getPostRequest(url);
            post.body("{\n" +
                    "  \"code\": \"" + code + "\",\n" +
                    "  \"lat\": 23.125203,\n" +
                    "  \"lng\": 113.222111\n" +
                    "}");
            String body = post.execute().body();
            JSONObject jsonObject = JSONObject.parseObject(body);
            if (jsonObject.getInteger("code") != 200) {
                System.out.println("当前瓶盖码出现问题：" + jsonObject.getString("message"));
                continue;
            }
            String draw = draw();
            if (draw == null) {
                continue;
            }
            System.err.println("抽中：" + draw);
        }

        //积分抽奖
        for (int i = 0; i < 10; i++) {
            System.out.println("------------积分抽奖--------------");
            HttpRequest httpRequest = getPostRequest("https://club.rioalc.com/api/miniprogram/luck-activity/45/draw");
            String body = httpRequest.execute().body();
            JSONObject jsonObject = JSONObject.parseObject(body);
            if (jsonObject.getInteger("code") != 200) {
                String message = jsonObject.getString("message");
                System.err.println("积分抽奖遇到问题：" + message);
                break;
            }
            String drawName = jsonObject.getJSONObject("data").getString("draw_name");
            System.out.println("积分抽奖活动抽中：" + drawName);
        }

        //评价
        List<UserSuggestions> userSuggestions = userSuggestions();
        for (UserSuggestions userSuggestion : userSuggestions) {
            JSONObject codeInfo = getCodeInfo(userSuggestion);
            String cateStars = codeInfo.getJSONObject("cate_stars").toString();
            String reviewUrl = "https://club.rioalc.com/api/miniprogram/user-suggestion/review";
            HttpRequest post = getPostRequest(reviewUrl);
            post.body("{\n" +
                    "  \"content\": \"好喝，咿呀呀！\",\n" +
                    "  \"log_id\": " + userSuggestion.getId() + ",\n" +
                    "  \"flavor\": \"" + codeInfo.getString("taste") + "\",\n" +
                    "  \"cate_stars\": " + cateStars + ",\n" +
                    "  \"income_at\": " + new Date().getTime() + ",\n" +
                    "  \"line\": \"" + codeInfo.getString("name") + "\"\n" +
                    "}");
            String body = post.execute().body();
            JSONObject jsonObject = JSONObject.parseObject(body);
            System.out.println(jsonObject);
        }
    }

    private static HttpRequest getPostRequest(String url) {
        HttpRequest post = HttpUtil.createPost(url);
        post.header("User-Agent", "Mozilla/5.0 (Linux; Android 14; 23116PN5BC Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260093 MMWEBSDK/20240404 MMWEBID/4745 MicroMessenger/8.0.49.2600(0x28003133) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android");
        post.header("Accept", "application/json");
        post.header("Accept-Encoding", "gzip,compress,br,deflate");
        post.header("Content-Type", "application/json");
        post.header("authorization", token);
        post.header("charset", "utf-8");
        post.header("Referer", "https://servicewechat.com/wx225b10f204323da5/184/page-frame.html");
        return post;
    }

    public static String draw() {
        String url = "https://club.rioalc.com/api/app/external/draw.do";
        HttpRequest post = getPostRequest(url);
        post.body("{\n" +
                "  \"activityId\": \"35\"\n" +
                "}");
        String body = post.execute().body();
        JSONObject jsonObject = JSONObject.parseObject(body);
        if (jsonObject.getInteger("code") != 200) {
            System.out.println("抽奖出现问题：" + jsonObject.getString("message"));
            return null;
        }
        String string = jsonObject.getJSONObject("data").getString("drawName");
        return string;
    }

    public static JSONObject getCodeInfo(UserSuggestions userSuggestion) {
        String url = "https://club.rioalc.com/api/miniprogram/user-suggestion/get-code-info";
        HttpRequest post = getPostRequest(url);
        post.body("{\n" +
                "  \"user_code_id\": \"" + userSuggestion.getId() + "\",\n" +
                "  \"code\": \"" + userSuggestion.getUrl() + "\",\n" +
                "  \"lat\": 23.125203,\n" +
                "  \"lng\": 113.222111\n" +
                "}");
        String body = post.execute().body();
        JSONObject jsonObject = JSONObject.parseObject(body);
        if (jsonObject.getInteger("code") != 200) {
            return null;
        }
        JSONObject dataJson = jsonObject.getJSONObject("data");
        String taste = dataJson.getString("taste");
        JSONArray flavors = dataJson.getJSONArray("new_flavors").getJSONObject(0).getJSONArray("flavors");
        for (Object flavor : flavors) {
            JSONObject flavorJson = JSONObject.parseObject(flavor.toString());
            if (flavorJson.getString("name").contains(taste)) {
                taste = flavorJson.getString("name");
                break;
            }
        }
        JSONObject json = new JSONObject();
        JSONObject cateStars = new JSONObject();
        JSONArray suggestionCates = dataJson.getJSONArray("suggestion_cate");
        for (Object suggestionCate : suggestionCates) {
            JSONObject suggestionJson = JSONObject.parseObject(suggestionCate.toString());
            cateStars.put(suggestionJson.getString("id"), 5);
        }
        String name = dataJson.getJSONArray("new_flavors").getJSONObject(0).getString("name");
        json.put("name", name);
        json.put("taste", taste);
        json.put("cate_stars", cateStars);
        return json;
    }

    public static List<UserSuggestions> userSuggestions() {
        String url = "https://club.rioalc.com/api/miniprogram/user-suggestions?page=1&per_page=100";
        HttpRequest request = HttpRequest.get(url);
        request.header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b19)XWEB/11205");
        request.header("Accept", "application/json");
        request.header("xweb_xhr", "1");
        request.header("authorization", "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvY2x1Yi5yaW9hbGMuY29tXC9hcGlcL21pbmlwcm9ncmFtXC9hdXRoIiwiaWF0IjoxNzIzOTkzMjU4LCJleHAiOjE3MjQwMDk0NTgsIm5iZiI6MTcyMzk5MzI1OCwianRpIjoidE1EQkV5S1ZQekFra1JwWiIsInN1YiI6NzkxOTA1MCwicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyJ9.DzReI7twdXBSopFSfTBKcKZJPENANQPjGQwIBAy3JgE");
        request.header("content-type", "application/json");
        request.header("sec-fetch-site", "cross-site");
        request.header("sec-fetch-mode", "cors");
        request.header("sec-fetch-dest", "empty");
        request.header("referer", "https://servicewechat.com/wx225b10f204323da5/184/page-frame.html");
        request.header("accept-language", "zh-CN,zh;q=0.9");
        String body = request.execute().body();
        JSONObject jsonObject = JSONObject.parseObject(body);
        if (jsonObject.getInteger("code") != 200) {
            return null;
        }
        List<UserSuggestions> data = jsonObject.getJSONArray("data").toJavaList(UserSuggestions.class);
        data = data.stream().filter(u -> u.getIsSuggested() == 0).collect(Collectors.toList());
        return data;
    }

    @Data
    class UserSuggestions {
        @JSONField(name = "id")
        private Integer id;
        @JSONField(name = "time")
        private Object time;
        @JSONField(name = "scanned_at")
        private String scannedAt;
        @JSONField(name = "brand_logo_src")
        private String brandLogoSrc;
        @JSONField(name = "brand_name")
        private String brandName;
        @JSONField(name = "url")
        private String url;
        @JSONField(name = "is_suggested")
        private Integer isSuggested;
    }

}
