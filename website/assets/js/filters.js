
export function filtersStart(filterRequest) {
    this.isSuccessful = true;

    const filtersButton = document.querySelector('.button-filters');
    if (!filtersButton) {
        this.isSuccessful = false;
        return;
    }

    const filterInputs = document.querySelectorAll('.filter-items .filter-item input');
    const selectedFiltersContainer = document.querySelector('.selected-filters');

    const crossForSelectedTemplate = ' <svg version="1.1" xmlns="http://www.w3.org/2000/svg"  preserveAspectRatio="xMaxYMin meet"' +
            'height="0.8em" viewBox="0 0 11 11"><path d="M2.2,1.19l3.3,3.3L8.8,1.2C8.9314,1.0663,9.1127,0.9938,9.3,1' +
            'C9.6761,1.0243,9.9757,1.3239,10,1.7&#xA;&#9;c0.0018,0.1806-0.0705,0.3541-0.2,0.48L6.49,5.5' +
            'L9.8,8.82C9.9295,8.9459,10.0018,9.1194,10,9.3C9.9757,9.6761,9.6761,9.9757,9.3,10&#xA;&#9;' +
            'c-0.1873,0.0062-0.3686-0.0663-0.5-0.2L5.5,6.51L2.21,9.8c-0.1314,0.1337-0.3127,0.2062-0.5,0.2' +
            'C1.3265,9.98,1.02,9.6735,1,9.29&#xA;&#9;C0.9982,9.1094,1.0705,8.9359,1.2,8.81L4.51,5.5L1.19,2.18' +
            'C1.0641,2.0524,0.9955,1.8792,1,1.7C1.0243,1.3239,1.3239,1.0243,1.7,1&#xA;&#9;C1.8858,0.9912,2.0669,1.06,2.2,1.19z"/></svg>';

    let selectedItemsData = {
        selectedArray: [],
        addNode: function(value, filterKey) {
            const div = document.createElement('div');
            const spanInDiv = document.createElement('span');

            div.className = 'selected-filter-item';
            div.dataset.value = value;
            div.dataset.filter = filterKey;
            div.textContent = value;
            spanInDiv.innerHTML = crossForSelectedTemplate;

            div.append(spanInDiv);
            
            // Скрытие из списка и дезактивация соотвествующего инпута, релоад
            div.addEventListener('click', e => {
                const selectedInputs = document.querySelectorAll(`.filter-items div[data-filter=${filterKey}] input:checked`);
                selectedInputs.forEach(input => {
                    if (input.value === div.dataset.value) {
                        input.checked = false;
                        filterRequest();
                        this.removeNode(value);
                    }
                });
            });

            this.selectedArray.push(div);
            selectedFiltersContainer.append(div);
        },
        removeNode: function(value) {
            const div = this.selectedArray.find(item => item.dataset.value === value);
            if (!div) return;
            this.selectedArray = this.selectedArray.filter(item => item !== div);
            div.remove();
        },
        clear: function() {
            this.selectedArray.forEach(div => {
                div.remove();
            });
            this.selectedArray = [];
        }
    };

    const filters = filtersButton.querySelector('button.filters');
    const filterItems = filtersButton.querySelector('.filter-items'); 

    filters.addEventListener('click', e => {
        e.preventDefault();
        
        document.body.className = "hidden";
        
        const contentRect = document.getElementById('content').getBoundingClientRect();
        filterItems.style.right = contentRect.left + "px";
        filtersButton.classList.toggle('active');
    });

    const filtersBackground = filtersButton.querySelector('.filter-background');

    filtersBackground.addEventListener('click', e => {
        e.preventDefault();

        filterRequest();
        document.body.className = "";
        filtersButton.classList.remove('active');
    });

    // Открытие подменю в фильтрах
    const listButtonNames = filtersButton.querySelectorAll('.list-button-name');
    listButtonNames.forEach(item => {
        item.addEventListener('click', e => {
            item.classList.toggle('active');
            let filterItem = item.nextElementSibling;
            if (filterItem.style.maxHeight) {
                filterItem.style.maxHeight = null;
            } else {
                filterItem.style.maxHeight = filterItem.scrollHeight + "px";
            }
        });
    });

    // Заполнение контейнера выбранных фильтров selected-filters

    filterInputs.forEach(item => {
        item.addEventListener('change', e => {
            if (e.target.checked) {
                selectedItemsData.addNode(e.target.value, e.target.name);
            } else {
                selectedItemsData.removeNode(e.target.value);
            }
        });
    });

    // Кнопка очистки фильтров 
    const filterClearButton = filtersButton.querySelector('.filter-clear');
    filterClearButton.addEventListener('click', e => {
        e.preventDefault();
        
        filterInputs.forEach(item => {
            item.checked = false;
        });

        selectedItemsData.clear();
    });


    this.setSelectedFilterItems = (searchParams) => {
        filterInputs.forEach(item => {
            item.checked = false;
        });

        selectedItemsData.clear();

        if (searchParams.has('filter') && searchParams.get('filter') === 'true') { 
            const inputsArray = Array.from(filterInputs);
            const filterItemsContainers = filtersButton.querySelectorAll('div[data-filter]');

            filterItemsContainers.forEach(itemContainer => {
                const filterKey = itemContainer.dataset.filter;

                if (searchParams.has(filterKey)) {
                    const values = searchParams.get(filterKey).split('+');
                    
                    values.forEach(val => {
                        const input = inputsArray.find(el => el.value === val);
                        if (input) {
                            input.checked = true;
                            selectedItemsData.addNode(val, input.name);
                        }
                    });
                }
            });
        }
    }
}