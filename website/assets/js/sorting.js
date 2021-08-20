import { updateSortingKey } from './control_buttons';


export function sortingStart(filterRequest) {
    this.isSuccessful = true;

    const sortingButton = document.querySelector('.button-sorting');
    if (!sortingButton) {
        this.isSuccessful = false;
        return;
    }

    const sortingText = sortingButton.querySelector('.button.sorting .text');

    const updateSorting = (text, key) => {
        sortingText.textContent = text;
        updateSortingKey(key);
    }

    const sorting = sortingButton.querySelector('button.sorting');
    const sortingItems = sortingButton.querySelector('.sorting-items');

    sorting.addEventListener('click', e => {
        e.preventDefault();

        sortingItems.classList.toggle('active');
    });

    const sortingInputItems = sortingButton.querySelectorAll('.sorting-item input');

    sortingInputItems.forEach(input => {
        input.addEventListener('change', e => {
            e.preventDefault();

            if (e.target.checked) {
                updateSorting(e.target.nextElementSibling.textContent, e.target.value);
                filterRequest();
            }
        });
    });


    this.setSelectedSortingItems = (searchParams) => {
        if (searchParams.has('sorting')) {
            const sortingKey = searchParams.get('sorting');
            const sortingInputs = document.querySelectorAll('.button-sorting .sorting-item input');

            sortingInputs.forEach(item => {
                if (item.value === sortingKey) {
                    item.checked = true;
                    updateSorting(item.nextElementSibling.textContent, sortingKey);
                    return;
                }
            });
        } else {
            const sortingKey = "date_desc";
            const defaultSelectedInput = sortingItems.querySelector(`input[value=${sortingKey}]`);
            const selectedInput = sortingItems.querySelector('input:checked');

            if (selectedInput !== defaultSelectedInput) {
                defaultSelectedInput.checked = true;
                updateSorting(defaultSelectedInput.nextElementSibling.textContent, null);       // default sortingKey is null
            }
        }
    }
}