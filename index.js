const text=document.querySelector("textarea"),
speechBtn=document.querySelector("button");
const v=document.getElementById("voice").value;
function getVoices() {
    let voices = speechSynthesis.getVoices();
    if(!voices.length){
      let utterance = new SpeechSynthesisUtterance("");
      speechSynthesis.speak(utterance);
      voices = speechSynthesis.getVoices();
    }
    return voices;
  }

function textTospeech(text1){
    let speak=new SpeechSynthesisUtterance(text1);
    speak.rate = rate.value;
    speak.voice=getVoices()[voice.value];
    speechSynthesis.speak(speak);
}

speechBtn.addEventListener("click",e=>{
    e.preventDefault();
    if(text.value !== ""){
        textTospeech(text.value)
    }
});
