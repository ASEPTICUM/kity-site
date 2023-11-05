

const setTimers = () => {
    const timers = document.querySelectorAll('.timer');
    timers.forEach( timer => {
        let date = {
            date: {
                days: null,
                months: null,
                years: null,
            },
            time: {
                seconds: '',
                minutes: '',
                hours: '',
            }
        };

        if(timer.innerHTML.match(/^(\d+\:){0,2}(\d+)\s\d+\:\d+\:\d+$/)) {
            let array_date = timer.innerHTML.split(' ');
            [ date.date.days = null, date.date.months = null, date.date.years = null ] = array_date[0].split(':').reverse();
            [ date.time.seconds = 0, date.time.minutes = 0, date.time.hours = 0 ] = array_date[1].split(':').reverse();
        } else {
            [ date.time.seconds = 0, date.time.minutes = 0, date.time.hours = 0 ] = timer.innerHTML.split(':').reverse();
        }

        let interval = setInterval(() => {
            if(!timer.innerHTML.match(/[1,2,3,4,5,6,7,8,9]/)) return clearInterval(interval);
            timer.innerHTML = getHTMLTimer();
        }, 1000);

        function getHTMLTimer() {
            date.time.seconds = date.time.seconds - 1;
            if(date.time.seconds < 0) {
                date.time.minutes = date.time.minutes - 1;
                if(date.time.minutes >= 0) date.time.seconds = '59';
            }
            if(date.time.minutes < 0 ) {
                date.time.hours = date.time.hours - 1;
                if(date.time.hours >= 0) date.time.minutes = '59';
            }
            if(date.date.days === null) {
                if(+date.time.hours > 0) {
                        return (date.time.hours < 10  ? '0' + +date.time.hours : +date.time.hours) + ':' +
                        (date.time.minutes < 10  ? '0' + +date.time.minutes : +date.time.minutes) + ':' +
                        (date.time.seconds < 10 ? '0' + +date.time.seconds : +date.time.seconds);
                    }
                return (date.time.minutes < 10  ? '0' + +date.time.minutes : +date.time.minutes) + ':' +
                        (date.time.seconds < 10 ? '0' + +date.time.seconds : +date.time.seconds);
            }

            if(date.time.hours < 0 && date.time.minutes < 0 && date.time.seconds < 0) {
                date.date.days = date.date.days - 1;
                if(date.date.days >= 0) date.time.hours = '24';
            }

            if(date.date.months === null) {
                if(+date.date.days > 0) {
                    return (date.date.days < 10  ? '0' + +date.date.days : +date.date.days) + ':' +
                    (date.time.hours < 10  ? '0' + +date.time.hours : +date.time.hours) + ':' +
                    (date.time.minutes < 10  ? '0' + +date.time.minutes : +date.time.minutes) + ':' +
                    (date.time.seconds < 10 ? '0' + +date.time.seconds : +date.time.seconds);
                }

                return (date.time.hours < 10  ? '0' + +date.time.hours : +date.time.hours) + ':' +
                (date.time.minutes < 10  ? '0' + +date.time.minutes : +date.time.minutes) + ':' +
                (date.time.seconds < 10 ? '0' + +date.time.seconds : +date.time.seconds);
            }
        }
    })
}

addOnLoadEvent(setTimers)
