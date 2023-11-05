

const header = document.querySelector('header');
const burger = header.querySelector('.header__burger');
const menu = header.querySelector('.header__menu');
const header_buttons = header.querySelector('.header__buttons');  



// Language selector configuration 
const installLanguagesSelector = () => {
    const languages_list = header.querySelector('.languages');
    const languages_active = languages_list.querySelector('.languages__active');

    languages_list.addEventListener('click', (event) => {

        event.stopPropagation();

        burger.classList.remove('active');
        menu.classList.remove('active');
        document.documentElement.classList.remove('header-blocked');


        if(event.target.closest('.languages__list')) return false;

        languages_list.classList.toggle('active');

        document.body.addEventListener('click', () => {

            languages_list.classList.remove('active');

        }, {once:true});

    })
}


// Burger (the menu button for mobile)
const installBurger = () => {
    const languages_list = header.querySelector('.languages');
    
    if (!burger) return; 
    
    burger.addEventListener('click', (event) => {

        event.stopPropagation();
    
        languages_list.classList.remove('active');
    
        burger.classList.toggle('active');
        menu.classList.toggle('active');
        document.documentElement.classList.toggle('header-blocked');
    
        if(burger.classList.contains('active')) {
    
            document.documentElement.scrollIntoView({
                'block': 'start',
                'behavior': 'smooth'
            })
    
        }
    
        document.body.addEventListener('click', (event) => {
    
            menu.classList.remove('active');
            burger.classList.remove('active');
            document.documentElement.classList.remove('header-blocked');
    
    
        }, {once:true})
    });    
}


// Menu configuration 
const installMenu = () => {
    const languages_list = header.querySelector('.languages');

    const replaceHeaderButtons = () => {
        if(document.documentElement.offsetWidth < 1001) {

            if(!menu.querySelector('.header__buttons')) menu.append(header_buttons);

            return;

        }


        if(!menu.querySelector('.header__buttons')) return;

        header.querySelector('.header').append(header_buttons);

    }

    menu.addEventListener('click', (event) => {
        languages_list.classList.remove('active');
        event.stopPropagation();
        return false;
    });
    
    window.addEventListener('resize', replaceHeaderButtons);
    replaceHeaderButtons();
}



function toggleSpoiler(spoiler, init = false) {
    const container = spoiler.closest('.spoilers');
    const spoiler_container = spoiler.querySelector('.spoiler__container');
    const fontSize = parseInt(getComputedStyle(spoiler).fontSize);

    if(init) return show();
    spoiler.classList.toggle('active');

    if(spoiler.classList.contains('active')) return show();
    spoiler_container.style.height = 0;

    function show() {
        spoiler_container.style.height = 'auto';
        const height = spoiler_container.offsetHeight / fontSize + 'em';
        spoiler_container.style.height = 0;

        if(container) {
            const active_spoiler = [...container.querySelectorAll('.spoiler.active')].find( item => item !== spoiler);
            if(active_spoiler) {
                active_spoiler.classList.remove('active');
                active_spoiler.querySelector('.spoiler__container').style.height = 0;
            }
        }
        setTimeout( () => {
            spoiler_container.style.height = height;
        }, 10)
    }
}

installToggleSpoiler = () => {
    const spoilers = document.querySelectorAll('.spoiler');
    spoilers.forEach( spoiler => {
        const spoiler_touch = spoiler.querySelector('.spoiler__touch');

        if(spoiler.classList.contains('active')) toggleSpoiler(spoiler, true);

        spoiler_touch.addEventListener('click', () => {
            toggleSpoiler(spoiler);
        });
    })
}


addOnLoadEvent(installToggleSpoiler);
addOnLoadEvent(installLanguagesSelector);
addOnLoadEvent(installBurger);
addOnLoadEvent(installMenu);


