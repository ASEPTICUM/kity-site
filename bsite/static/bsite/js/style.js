

(function setRightVh() {
    let vh = window.innerHeight * 0.01;

    document.documentElement.style.setProperty('--vh', `${vh}px`);

    window.addEventListener('resize', () => {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    });
})();


// Custom placeholders
const installCustomPlaceholders = () => {
    const input_containers = document.querySelectorAll('.input-container');

    if (!input_containers) return;

    input_containers.forEach( container => {

        const input = container.querySelector('input') || container.querySelector('textarea');
        const placeholder = container.querySelector('.input-placeholder');
        const fontSize = parseFloat(getComputedStyle(placeholder).fontSize);

        if(!placeholder) return;
        
        let width_placeholder = (placeholder.offsetWidth + 8) / fontSize  + 'em';

        document.fonts.addEventListener('load', () => {
            width_placeholder = (placeholder.offsetWidth + 8) / fontSize  + 'em';
        })

        input.style.textIndent = width_placeholder;

        input.addEventListener('focus', () => {
            placeholder.classList.add('active');
            input.style.textIndent = 0;
        })

        input.addEventListener('blur', () => {
            placeholder.classList.remove('active');
            input.style.textIndent = width_placeholder;
        })
    })

    const makeResponsiveHeightOfTextarea = () => {
        const tx = document.querySelectorAll('.textarea');
        if(!tx.length) return false;

        for (let i = 0; i < tx.length; i++) {
            tx[i].setAttribute('style', 'height:' + (tx[i].scrollHeight) + 'px;overflow-y:hidden;');
            tx[i].addEventListener("input", OnInput, false);
            tx[i].addEventListener('blur', onBlur, false);
        }

        function OnInput() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        }

        function onBlur() {
            const placeholder = this.closest('.input-container') && this.closest('.input-container').querySelector('.input-placeholder');

            let buffer = null;

            if(placeholder) {
                buffer = this.value;
                this.value = placeholder.innerHTML + this.value;
            }

            // Fucking magic 
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            
            if(buffer !== null) this.value = buffer;
        }
    }
    makeResponsiveHeightOfTextarea() 
}


addOnLoadEvent(installCustomPlaceholders);



