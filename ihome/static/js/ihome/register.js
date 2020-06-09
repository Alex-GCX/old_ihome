function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 保存图片验证码编号
var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 形成图片验证码的后端地址， 设置到页面中，让浏览请求验证码图片
    // 1. 生成图片验证码编号
    imageCodeId = generateUUID();
    // 设置图片url
    var url = "/api/v1.0/image_codes/" + imageCodeId;
    $(".image-code img").attr("src", url);
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var req_data = {
        image_code: imageCode,
        image_code_id: imageCodeId
    }
    $.get('/api/v1.0/smscodes/' + mobile, req_data, function(resp){
        if (resp.errno == '0'){
            //验证码短信发送成功
            //重新刷新图片验证码
            generateImageCode();
            //倒计时60秒
            var num = 60;
            //serInterval(func, milliseconds) 每xxx毫秒执行一次func
            var timer = setInterval(function (){
                if (num>=1){
                    //设置按钮显示当前秒数num
                    $('.phonecode-a').html(num+'秒');
                    num -= 1;
                }else{
                    //计时完成,将按钮重置可点击状态
                    $('.phonecode-a').html('获取验证码');
                    $('.phonecode-a').attr('onclick', 'sendSMSCode();');
                    //清空timer
                    clearInterval(timer)
                }
            }, 1000)
        }else{
            alert(resp.errmsg)
            $('.phonecode-a').attr('onclick', 'sendSMSCode();');
        }
    })
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
        //发送ajax注册请求
        //组织数据
        var req_data = {
            mobile: mobile,
            phonecode: phoneCode,
            password: passwd,
            password2: passwd2
        }
        var req_json = JSON.stringify(req_data)
        $.ajax({
            url: '/api/v1.0/users/',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: req_json,
            header: {
                'X-CSRFToken': getCookie('csrf_token')
            },  //请求头,将csrf_token值放到请求中,方便后端csrf进行验证
            success: function(resp){
                if (resp.errno == '0'){
                    location.href='/index.html'
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    });
})
