
function shadow(){
    //var zhezhao = document.getElementById("zhezhao");
    var common = document.getElementById("common");
    //zhezhao.style.display = "block";
    common.style.opacity= .5;
    return false;
}
function cancelShadow(){
//    var zhezhao = document.getElementById("zhezhao");
    var common = document.getElementById("common");
  //  zhezhao.style.display = "none";
    common.style.opacity= 1;
    return false;
}
function showLogin() {
    var loginDiv = document.getElementById("loginDiv");    
    loginDiv.style.display = "block";
    return shadow();
}
function hidLogin() {
    var loginDiv = document.getElementById("loginDiv");    
    loginDiv.style.display = "none";
    return cancelShadow();
        
}
function showRegister() {
    var registerDiv = document.getElementById("RegisterDiv");
    registerDiv.style.display = "block";    
    return shadow();
}
function hidRegister() {
    var registerDiv = document.getElementById("RegisterDiv"); 
    registerDiv.style.display = "none";
    return cancelShadow();    
    
}
function submitRegister(){
   
  

}
function searchLocation(){ 
    var name = document.getElementById("wifi-name");    
    var location = document.getElementById("location");    
    var ssid = document.getElementById("ssid");    
    var mac = document.getElementById("mac"); 
    var twice = document.getElementById("twice"); 
  window.location.assign("/wifi?name="+name.value+"&ssid="+ssid.value+"&mac="+mac.value+'&twice=1');
}
function submitLogin(){
    var loginForm = document.getElementById("loginForm");    
    if(loginForm.username.value.length==0)
    { 
        alert("用户名不能为空");
        return false;
    }
    if(loginForm.password.value.length==0)
    { 
        alert("密码不能为空");
        return false;    
    }    
        
}
