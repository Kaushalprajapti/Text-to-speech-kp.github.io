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

// const synth = window.speechSynthesis;

// const text = document.querySelector('textarea');
// const play = document.querySelector('#play');
// const rate = document.querySelector('#rate');

// function speak() {
//   if (synth.speaking) {
//     synth.cancel();
//   }
//   const utterThis = new SpeechSynthesisUtterance(text.textContent);
//   utterThis.addEventListener('error', () => {
//     console.error('SpeechSynthesisUtterance error');
//   });
//   utterThis.rate = rate.value;
//   synth.speak(utterThis);
// }

// play.addEventListener('click', speak);