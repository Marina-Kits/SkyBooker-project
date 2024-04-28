const messageDivs = document.getElementsByClassName('errors-notification');
function hideDiv() {
   for (let i = 0; i < messageDivs.length; i++) {
       messageDivs[i].style.display = 'none';
   }
}
setTimeout(hideDiv, 5000);
