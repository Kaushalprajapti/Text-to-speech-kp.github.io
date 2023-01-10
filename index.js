const text=document.querySelector("textarea"),
speechBtn=document.querySelector("button");

function textTospeech(text1){
    let speak=new SpeechSynthesisUtterance(text1);
    speechSynthesis.speak(speak);
}

speechBtn.addEventListener("click",e=>{
    e.preventDefault();
    if(text.value !== ""){
        textTospeech(text.value)
    }
});