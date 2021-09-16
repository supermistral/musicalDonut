import { filtersStart } from "./filters";
import { sortingStart } from "./sorting";


let wasEmptyFiltered = true;
let prevStringValues = "";
let sortingKey = null;


export const updateSortingKey = (value) => {
    sortingKey = value;
};


const getSelectedStringData = (selectedInputs) => {
    let selectedData = {};

    selectedInputs.forEach(item => {
        const parent = item.parentNode.parentNode;
        const filterKey = parent.dataset.filter;
        if (selectedData[filterKey] === undefined) {
            selectedData[filterKey] = [];
        }
        selectedData[filterKey].push(item.value);
    });

    if (sortingKey) {
        selectedData["sorting"] = [sortingKey];
    }

    const selectedStringData = {}
    for (const key in selectedData) {
        selectedStringData[key] = selectedData[key].join('+');
    }

    return selectedStringData;
};


const getSelectedStringValues = () => {
    const selectedInputs = document.querySelectorAll('.button-filters .filter-item input:checked');
    const selectedStringData = getSelectedStringData(selectedInputs);

    return Object.values(selectedStringData).join('');
};


const promisefilterRequest = async (needHistory = true) => {
    const selectedInputs = document.querySelectorAll('.button-filters .filter-item input:checked');

    let needFilterKey = {};
    if (selectedInputs.length !== 0) {
        needFilterKey["filter"] = true;
    }

    const selectedStringData = getSelectedStringData(selectedInputs);
    const stringValues = Object.values(selectedStringData).join('');

    if (stringValues === prevStringValues && wasEmptyFiltered) {          // пустой выбор подряд
        return null;
    } else if (stringValues === prevStringValues && !wasEmptyFiltered) {  // пустой выбор первый в серии
        wasEmptyFiltered = true;
    } else {                                                // не пустой выбор
        wasEmptyFiltered = false;
    }
    
    const url = '?' + new URLSearchParams({
        ...needFilterKey,
        ...selectedStringData
    });

    console.log(stringValues);

    prevStringValues = stringValues;
    if (needHistory) history.pushState(null, null, url);

    return fetch(url, {headers: {'x-requested-with': 'XMLHttpRequest'}})
        .then(response => {
            if (!response.ok) {
                throw Error("Произошла ошибка с кодом " + response.status);
            }
            return response.json();
        })
        .then(data => {
            return data.html;
        });
};


export const controlButtonsHandler = () => {
    const articlesContainer = document.querySelector('.content__articles');

    const filterRequest = (needHistory = true) => {
        promisefilterRequest(needHistory)
            .then(data => {
                if (data !== null) {
                    articlesContainer.innerHTML = data;
                }
            })
            .catch(e => {
                // отобразить попап
                articlesContainer.innerHTML = e.message;
            });
    }
    const filters = new filtersStart(filterRequest);
    const sorting = new sortingStart(filterRequest);

    const filtersFlag = filters.isSuccessful;
    const sortingFlag = sorting.isSuccessful;

    if (!(filtersFlag || sortingFlag)) return;

    const setSelectedItems = () => {
        const searchParams = new URLSearchParams(window.location.search);

        filtersFlag && filters.setSelectedFilterItems(searchParams);
        sortingFlag && sorting.setSelectedSortingItems(searchParams);
    }

    window.addEventListener('popstate', e => {
        setSelectedItems();
        filterRequest(false);
    });

    setSelectedItems();

    prevStringValues = getSelectedStringValues();
};