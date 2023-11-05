
const _getExchangeData = () => {
    return JSON.parse(document.getElementById("exchange_options").textContent)
}

const _getWallets = () => {
    return JSON.parse(document.getElementById("wallets").textContent)
}

const prettifyNumber = (number) => {
    return (1 * Number(number).toFixed(8)).toString()
}

const installExchangeForm = () => {
    const exchange_options = _getExchangeData()

    var currencyFromSelection = document.getElementById("id_exchange_from")
    var currencyToSelection = document.getElementById("id_exchange_to")

    var orderTypesSelection = document.getElementById("id_order_type")
    var changeButton = document.querySelector(".trade__changeButton");
    var fromButton = document.querySelector(".from_button");
    var toButton = document.querySelector(".to_button");
    var sumFrom = document.querySelector("#id_sum_from");
    var sumTo = document.querySelector("#id_sum_to");
    var rate = document.querySelector("#id_rate");


    const getCurrentlySelectedCurrencies = () => {
        return [currencyFromSelection.value, currencyToSelection.value]
    }
    const setActiveCurrencies = (currencyFrom, currencyTo) => {
        var listCurrencyFrom = document.querySelector(".listCurrencyFrom");
        var listCurrencyTo = document.querySelector(".listCurrencyTo");

        currencyFromSelection.value = currencyFrom
        currencyToSelection.value = currencyTo

        listCurrencyFrom.querySelector(".i-" + currencyFrom).classList.add("active")
        listCurrencyTo.querySelector(".i-" + currencyTo).classList.add("active")
    }
    const getExchangePairByPairIDS = (exchanges, from_id, to_id) => {
        for (key of Object.keys(exchanges)) {
            if (exchanges[key].exchange_from == from_id && exchanges[key].exchange_to == to_id)
                return exchanges[key]       
        }       
    }

    const installMaximumExchange = () => {
        if (!wallets) return 
        if (orderTypesSelection.value == "EXTERNAL_TO_BALANCE") {
            sumFrom.max = null 
            return 
        }

        let user_wallets_list = JSON.parse(wallets.innerText) 
        let [input_currency_id, _] = getCurrentlySelectedCurrencies()
        for (let wallet of user_wallets_list) {
            if (wallet.currency.id == input_currency_id) {
                sumFrom.max = wallet.balance
            } 
        }
    }

    const setCurrencySelectionButtonValuesForExchange = (exchange) => {
        exchange_from = exchange.exchange_from_obj;
        exchange_to = exchange.exchange_to_obj;

        fromCurrencyName = fromButton.querySelector('.trade__nameCurrency')
        fromCurrencyName.innerHTML = exchange_from['name'];
        fromCurrencyName.dataset.currencyKey = exchange_from['id'];

        toCurrencyName = toButton.querySelector('.trade__nameCurrency');
        toCurrencyName.innerHTML = exchange_to['name'];
        toCurrencyName.dataset.currencyKey = exchange_to['id'];
    }

    const renderExchangeInfo = (exchange) => {
        exchange_from = exchange.exchange_from_obj;
        exchange_to = exchange.exchange_to_obj;

        minimum_exchange_amount_converted = currencyConvert(
            exchange,
            exchange_from.minimum_exchange_amount,
            exchange_from.symbol,
            exchange_to.symbol,
        );

        from_min_str = prettifyNumber(exchange_from.minimum_exchange_amount) + ' ' + exchange_from['symbol'];
        document.querySelector(".from_trade__field .trade-infoBlock span").innerHTML = from_min_str;
        sumFrom.min = Number(exchange_from.minimum_exchange_amount);

        to_min_str = prettifyNumber(minimum_exchange_amount_converted) + ' ' + exchange_to['symbol'];
        document.querySelector(".to_trade__field .trade-infoBlock span").innerHTML = to_min_str;
        sumTo.min = minimum_exchange_amount_converted;

        document.querySelector('.request__courseBlockInfo').innerHTML = "1 " + exchange_from['symbol'] +
            " <span class='grey'>=</span>" + prettifyNumber(exchange.value_currency) + " " + exchange_to['symbol'] + "</span>";

        document.querySelector('.request__from_cur').innerHTML = exchange_from.symbol;
        document.querySelector('.request__to_cur').innerHTML = exchange_to.symbol;

        rate.value = exchange.value_currency 
    }

    const createExchangeOption = (exchange_object) => {
        var li = document.createElement("li");
        var span = document.createElement("span");
        li.appendChild(span);
        li.setAttribute("class", ("listCurrency__item i-" + exchange_object.id));
        span.appendChild(document.createTextNode(exchange_object.name));
        span.setAttribute("class", "trade__nameCurrency");
        span.dataset.currencyKey = exchange_object.id;
        return li 
    }

    const renderCurrenciesSelectionOptionsForExchange = (exchange_options, exchange) => {
        var listCurrencyFrom = document.querySelector(".listCurrencyFrom");
        var listCurrencyTo = document.querySelector(".listCurrencyTo");

        listCurrencyFrom.innerText = '';
        listCurrencyTo.innerText = '';

        for (let exchange_option of Object.values(exchange_options)) {
            const exchange_from_option = createExchangeOption(exchange_option.exchange_from_obj)
            const exchange_to_option = createExchangeOption(exchange_option.exchange_to_obj)
            if (!listCurrencyFrom.querySelector(".i-" + exchange_option.exchange_from_obj.id)) 
                listCurrencyFrom.append(exchange_from_option)

            if (exchange_option.exchange_from_obj.id == exchange.exchange_from_obj.id) {
                if (!listCurrencyTo.querySelector(".i-" + exchange_option.exchange_to_obj.id))
                    listCurrencyTo.append(exchange_to_option)
            }
        }
    }

    // Rerenders currenciesSelectElement options, button values, information and sets currently active currencies IDs 
    const renderCurrenciesSelection = (exchange) => {
        renderCurrenciesSelectionOptionsForExchange(exchange_options, exchange)
        setCurrencySelectionButtonValuesForExchange(exchange)
        setActiveCurrencies(exchange.exchange_from_obj.id, exchange.exchange_to_obj.id)

        renderExchangeInfo(exchange)
        installMaximumExchange()
    }     

    const getCurrentExchange = () => {
        return exchange_options.find(currency_exchange => 
                (currency_exchange.exchange_from_obj.id == currencyFromSelection.value 
                    &&
                 currency_exchange.exchange_to_obj.id == currencyToSelection.value)
        )
    }

    const setCurrencySelectEventHandler = (event) => {
        const currency = event.target.closest('.listCurrency__item');
        if (!currency) return 

        const field = currency.closest(".trade__field")
        if(currency) {
            if (field.classList.contains("from_trade__field")) {
                currencyFromSelection.value = currency.querySelector(".trade__nameCurrency").dataset.currencyKey
                triggerEvent(currencyFromSelection, "change")
                triggerEvent(sumFrom, "input")
            }
            else {
                currencyToSelection.value = currency.querySelector(".trade__nameCurrency").dataset.currencyKey
                triggerEvent(currencyToSelection, "change")
                triggerEvent(sumTo, "input")
            }
        }
    } 

    const installCurrencySelectionCallbacks = () => {
        document.querySelectorAll('.trade__field').forEach( field => {
            const menu = field.querySelector('.trade__fieldButton');
            menu.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();

                field.classList.add('active-list');

                document.body.addEventListener('click', () => {
                    field.classList.remove('active-list');
                }, {once:true});
            });

            const currency_list_selection = field.querySelector('.listCurrency');
            currency_list_selection.addEventListener('click', event => setCurrencySelectEventHandler(event))
        });
    }

    const setExchangePlaceholder = () => {
        const exchange_placeholder = document.getElementById("exchange_placeholder")
        if (orderTypesSelection.value == "EXTERNAL_TO_BALANCE") {
//            exchange_placeholder.innerText = exchange_placeholder.dataset.exchangeFrom
        }
        else if (orderTypesSelection.value == "BALANCE_TO_EXTERNAL") {
//            renderBalanceToExternal()
        }
        else {
            exchange_placeholder.innerText = exchange_placeholder.dataset.exchangeTo 
        }
    }

    // No need to return the order type in here 
    const getExchangeParamsFromURL = () => {
        const urlParams = new URLSearchParams(window.location.search)
        return {
            exchange_from: urlParams.get("exchange_from"),
            exchange_to: urlParams.get("exchange_to")
        }
    }

    const onMount = () => {
        let {exchange_from, exchange_to} = getExchangeParamsFromURL()

        let order_type = orderTypesSelection.value 
        console.log("Order type: ", order_type)
        if (!["BALANCE_TO_EXTERNAL", "EXTERNAL_TO_BALANCE"].includes(order_type))
            order_type = "EXTERNAL_TO_BALANCE"

        let exchange = null
        if (exchange_from && exchange_to) {
            exchange = getExchangePairByPairIDS(exchange_options, exchange_from, exchange_to)
        }
        if (currencyFromSelection.value && currencyToSelection.value) {
            exchange = getExchangePairByPairIDS(exchange_options, exchange_from, exchange_to)
        } 

        if (!exchange) {        
            exchange = exchange_options[0]
        }

        orderTypesSelection.value = order_type
        currencyFromSelection.value = exchange.exchange_from_obj.id
        currencyToSelection.value = exchange.exchange_to_obj.id

        setExchangePlaceholder()
        renderCurrenciesSelection(exchange)
        installCurrencySelectionCallbacks()
    }

    const getDefaultExchangeForCurrency = (currency_id) => {
        return exchange_options.filter(exchange_option => exchange_option.exchange_from_obj.id == currency_id)[0]
    }

    changeButton.addEventListener("click", function(event) {
        event.preventDefault();
        event.stopPropagation();

        current_sum = sumTo.value 
        let [currency_from_key, currency_to_key] = getCurrentlySelectedCurrencies() 
        let exchange = getExchangePairByPairIDS(exchange_options, currency_to_key, currency_from_key)
        if (!exchange) {
            exchange = getDefaultExchangeForCurrency(currency_to_key)
        }
        currencyFromSelection.value = exchange.exchange_from_obj.id
        currencyToSelection.value = exchange.exchange_to_obj.id

        renderCurrenciesSelection(exchange)

        sumFrom.value = current_sum;
        triggerEvent(sumFrom, "input");
        installMaximumExchange()
    });

    sumFrom.addEventListener("input", function(event) {
        event.stopPropagation();
        
        const current_exchange = getCurrentExchange()

        exchange_from = current_exchange.exchange_from_obj;
        exchange_to = current_exchange.exchange_to_obj;
        commission_percent = current_exchange.commission / 100;
        sum_to_value_without_commission = currencyConvert(current_exchange, this.value);
        sum_to_value = sum_to_value_without_commission - (sum_to_value_without_commission * commission_percent)

        sumTo.value = prettifyNumber(sum_to_value)
        document.querySelector('.request__from_sum').innerHTML = prettifyNumber(sumFrom.value);
        document.querySelector('.request__to_sum').innerHTML = prettifyNumber(sumTo.value);
    });
    sumTo.addEventListener("input", function(event) {
        event.stopPropagation();

        let current_exchange = {...getCurrentExchange()}

        exchange_from = current_exchange.exchange_from_obj;
        exchange_to = current_exchange.exchange_to_obj;
        commission_percent = current_exchange.commission / 100;
        current_exchange.value_currency = 1 / current_exchange.value_currency  // Cause I need to set the sumFrom 

        sum_from_value_without_commission = currencyConvert(current_exchange, this.value)
        sum_from_value = sum_from_value_without_commission + (sum_from_value_without_commission * commission_percent)
        sumFrom.value = prettifyNumber(sum_from_value)

        document.querySelector('.request__to_sum').innerHTML = prettifyNumber(sumTo.value);
        document.querySelector('.request__from_sum').innerHTML = prettifyNumber(sumFrom.value);
    });

    [currencyFromSelection, currencyToSelection].forEach(selection => {
        selection.addEventListener("change", () => {
            const [exchange_from, exchange_to] = getCurrentlySelectedCurrencies()
            let exchange = getExchangePairByPairIDS(exchange_options, exchange_from, exchange_to)
            if (!exchange) {
                exchange = getDefaultExchangeForCurrency(exchange_from)
                currencyFromSelection.value = exchange.exchange_from_obj.id
                currencyToSelection.value = exchange.exchange_to_obj.id
            }
            renderCurrenciesSelection(exchange)
            installMaximumExchange()
        })
    })

    onMount()
    triggerEvent(orderTypesSelection, "change")
}


function getExchangeRate(exchange) {
    return parseFloat(exchange.value_currency)
}

function currencyConvert(exchange, amount) {
    return amount * getExchangeRate(exchange);
}


addOnLoadEvent(installExchangeForm)

