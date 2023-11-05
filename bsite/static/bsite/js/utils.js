
const addOnLoadEvent = (event) => {
    if (window.addEventListener) { // Normal 
        window.addEventListener('load', event, false); 
    } 
    else if (window.attachEvent) { // Microsoft standard 
        window.attachEvent('onload', event);
    }
}


function triggerEvent(el, event) {
    if ("createEvent" in document) {
        var evt = document.createEvent("HTMLEvents");
        evt.initEvent(event, false, true);
        el.dispatchEvent(evt);
    }
    else {
        if (event == 'change') {
            event = "onchange"
        }
        el.fireEvent(event);
        currenciesSelectElement.fireEvent(event);
    }
}
