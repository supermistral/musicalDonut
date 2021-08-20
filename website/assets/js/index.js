import { controlButtonsHandler } from "./control_buttons";


const imageInitClickHandler = () => {
    const imagesWrappers = document.querySelectorAll(".img-cover img");
    if (imagesWrappers.length === 0) {
        return;
    }

    const wrapperContent = document.getElementById("content");
    
    imagesWrappers.forEach(item => {
        item.addEventListener('click', (e) => {
            document.body.className = "hidden";

            const imageSrc = e.target.src;
            const imageAlt = e.target.alt;

            let fullsizeWrapper = document.createElement('div');    
            fullsizeWrapper.className = "img-fullsize__wrapper";
            fullsizeWrapper.innerHTML = "<div class='img-fullsize__inner'>" +
                "<img src='" + imageSrc + "' alt='" + imageAlt + "'>" + 
                "<div class='cross'></div></div></div>";

            fullsizeWrapper.addEventListener('click', (e) => {
                const imgContainer = fullsizeWrapper.querySelector("img");
                if (e.target !== imgContainer) {
                    document.body.className = "";
                    fullsizeWrapper.remove();
                }
            });

            wrapperContent.append(fullsizeWrapper);
        });
    });
};

const sliderHandler = () => {
    const sliders = document.querySelectorAll('.img-cover.slider');
    if (sliders.length === 0) {
        return;
    }

    sliders.forEach(item => {
        const images = item.querySelectorAll('img');
        const imagesLength = images.length;
        let imageIndex = 0;

        const arrowPrev = item.querySelector('.prev');
        const arrowNext = item.querySelector('.next');
        let nodeCurNum = item.querySelector('.info span');

        const prevClick = () => {
            const imgCur = images[imageIndex];
            imageIndex = imageIndex > 0 ? imageIndex - 1 : imagesLength - 1;
            const imgNext = images[imageIndex];

            imgCur.className = "anim-right";
            imgNext.className = "active";
        };

        const nextClick = () => {
            const imgCur = images[imageIndex];
            imageIndex = imageIndex < imagesLength - 1 ? imageIndex + 1 : 0;
            const imgNext = images[imageIndex];

            imgCur.className = "anim-left";
            imgNext.className = "active";
        };

        const clickHandler = (callback) => {
            callback();
            nodeCurNum.textContent = imageIndex + 1;
        };

        const hm = new Hammer(item);
        hm.on("swipeleft", e => {
            clickHandler(nextClick);
        });
        hm.on("swiperight", e => {
            clickHandler(prevClick);
        });
        
        arrowPrev.addEventListener('click', () => {
            clickHandler(prevClick);
        });

        arrowNext.addEventListener('click', () => {
            clickHandler(nextClick);
        });
    })
};

const musicSliderHandler = () => {
    // Список всех песен
    const songRefs = document.querySelectorAll('.song__refs');
    if (songRefs.length === 0)
        return;

    // элемент с настройкой ссылок песни
    let musicItem = document.querySelector('.music-refs');

    const refItems = musicItem.querySelectorAll('.ref-item');
    if (refItems.length === 0) 
        return;

    const lengthOfStep = refItems[0].offsetHeight;
        
    // Слайдер
    let musicSlider = musicItem.querySelector('.music-slider');
    let musicRefsIndex = {
        firstIndex: 0,
        lastIndex: refItems.length - 1,
        indicesOfVisible: Array.from(Array(refItems.length), (v, k) => k),
        updateFirstIndex: function(newIndex) {
            if (newIndex === null) {
                return;
            }
            refItems[this.firstIndex].classList.remove('first');
            this.firstIndex = newIndex;
            refItems[this.firstIndex].classList.add('first');
        },
        updateLastIndex: function(newIndex) {
            if (newIndex === null) {
                return;
            }
            refItems[this.lastIndex].classList.remove('last');
            this.lastIndex = newIndex;
            refItems[this.lastIndex].classList.add('last');
        },
    };

    // Начальный индекс массива рефов и соответствующий сервис
    let currentService = localStorage.getItem('musicService') || 'apple';
    let currentIndex = (() => {
        for (let i = 0; i < refItems.length; ++i) {
            if (refItems[i].dataset.service === currentService) {
                return i;
            }
        }
        return 0;
    })();

    const setMusicService = (service) => {
        localStorage.setItem('musicService', service);
    }
    
    const setActiveSongs = (service) => {
        songRefs.forEach(songRef => {
            const songContainer = songRef.querySelector('.song__container');

            let activeSongBefore = null;
            for (let el of songContainer.children) {
                if (el.classList.contains('active')) {
                    el.classList.remove("active");
                    activeSongBefore = el;
                }
            }

            const song = songContainer.querySelector(`div[data-service=${service}]`);
            if (song) {
                song.classList.add('active');
            } else if (activeSongBefore !== null) {
                activeSongBefore.classList.add('active');
            } else {
                songContainer.children[0].classList.add('active');
            }
        });
    }

    // разница для корректного перемещения слайдера между блоками
    const topOffsetSlider = (refItems[musicRefsIndex.firstIndex].offsetHeight - musicSlider.offsetHeight) / 2;

    const moveSlider = (setActiveFlag = true) => {
        const step = musicRefsIndex.indicesOfVisible[currentIndex] * lengthOfStep + topOffsetSlider;
        musicSlider.style.transform = `translateY(${step}px)`;

        refItems[currentIndex].querySelector('input').checked = true;

        if (setActiveFlag) {
            const currentService = refItems[currentIndex].dataset.service; 
            setActiveSongs(currentService);
            setMusicService(currentService);
        }
    };

    refItems.forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.tagName === "INPUT") {
                const targetId = +e.target.id.replace(/[^\d]/g, '');
                currentIndex = targetId - 1;

                moveSlider();
            }
        });
    });

    musicSlider.addEventListener('mousedown', e => {
        e.preventDefault();
        musicSlider.classList.add("active");

        const shiftY = e.clientY - musicSlider.getBoundingClientRect().top;
        const diffHeight = musicItem.offsetHeight - musicSlider.offsetHeight;

        const mouseMoveHandler = event => {
            let top = event.clientY - shiftY - musicItem.getBoundingClientRect().top;
            if (top < 0) {
                top = 0;
            } else if (top > diffHeight) {
                top = diffHeight;
            }

            musicSlider.style.transform = `translateY(${top}px)`;
        };

        const mouseUpHandler = event => {
            const translateY = +musicSlider.style.transform.replace(/[^\d.]/g, '');
            const indexOfVisible = Math.trunc((translateY + lengthOfStep / 2) / lengthOfStep);
            currentIndex = musicRefsIndex.indicesOfVisible.indexOf(indexOfVisible);

            document.removeEventListener('mouseup', mouseUpHandler);
            document.removeEventListener('mousemove', mouseMoveHandler);

            musicSlider.classList.remove("active");
            moveSlider(false);
        };
        
        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler)
    });
    
    musicSlider.ondragstart = () => false;

    songRefs.forEach(songItem => {
        // элемент с песней / плейлистом
        const songContainer = songItem.querySelector('.song__container');
        // блок настроек для отображения слайдера
        const songInfo = songItem.querySelector('.song__info');

        const showMusicSlider = () => {
            const mouseEnterHandler = event => {
                event.preventDefault();
                
                const songWidgets = Array.from(songContainer.children);
                musicRefsIndex.indicesOfVisible.fill(null);
                
                let firstIndex = null;
                let lastIndex = 0;
                let counterVisible = 0;

                for (let i = 0; i < refItems.length; ++i) {
                    let ref = refItems[i];

                    if (!songWidgets.find(el => el.dataset.service === ref.dataset.service)) {
                        ref.classList.add('hidden');
                    } else {
                        ref.classList.remove('hidden');
                        if (firstIndex === null) {
                            firstIndex = i;
                        }
                        lastIndex = i;
                        musicRefsIndex.indicesOfVisible[i] = counterVisible++;
                    }
                }

                musicRefsIndex.updateFirstIndex(firstIndex);
                musicRefsIndex.updateLastIndex(lastIndex);

                if (musicRefsIndex.indicesOfVisible[currentIndex] === null) {
                    currentIndex = firstIndex;
                }

                // Начальная инициализаця
                moveSlider(false);

                songInfo.append(musicItem);

                setTimeout(() => {
                    musicItem.classList.add('active');
                }, 0); 
            };

            const mouseLeaveHandler = event => {
                musicItem.classList.remove('active');
            };

            songInfo.addEventListener('mouseenter', mouseEnterHandler);
            songInfo.addEventListener('mouseleave', mouseLeaveHandler);
        };

        showMusicSlider();
    });

    setActiveSongs(currentService);
};

const searchFormClickHandler = () => {
    const searchForm = document.querySelector('.search-form form');
    if (searchForm) {
        const input = searchForm.querySelector('input');
        searchForm.querySelector('span').addEventListener('click', e => {
            input.focus();
        });

        const button = searchForm.querySelector('button');
        const isEmptyInput = el => {
            const value = el.value.trim().length;
            button.disabled = value === 0;
        };

        input.addEventListener('keyup', e => {
            isEmptyInput(e.target);
        });

        input.addEventListener('blur', e => {
            button.disabled = true;
        });

        isEmptyInput(input);
    }
};

// const promisefilterRequest = (() => {
//     // Была ли фильтрация без выбора фильтров (пустой выбор)
//     let wasEmptyFiltered = true;
//     let prevStringValues = "";
//     let sortingKey = null;

//     // убрать
//     window.addEventListener('load', e => {
//         const sortingInputItems = document.querySelectorAll('.sorting-items input');
//         sortingInputItems.forEach(input => {
//             input.addEventListener('change', e => {
//                 e.preventDefault();
//                 if (e.target.checked) {
//                     sortingKey = e.target.value;
//                 }
//             });
//         });
//     });

//     return async () => {
//         const selectedInputs = document.querySelectorAll('.button-filters .filter-item input:checked');
//         let selectedData = {};

//         let needFilterKey = {};
//         if (selectedInputs.length !== 0) {
//             needFilterKey["filter"] = true;
//         }

//         selectedInputs.forEach(item => {
//             const parent = item.parentNode.parentNode;
//             const filterKey = parent.dataset.filter;
//             if (selectedData[filterKey] === undefined) {
//                 selectedData[filterKey] = [];
//             }
//             selectedData[filterKey].push(item.value);
//         });

//         if (sortingKey) {
//             selectedData["sorting"] = [sortingKey];
//         }

//         const selectedStringData = {}
//         for (const key in selectedData) {
//             selectedStringData[key] = selectedData[key].join('+');
//         }

//         const stringValues = Object.values(selectedStringData).join('');

//         if (stringValues === prevStringValues && wasEmptyFiltered) {          // пустой выбор подряд
//             return null;
//         } else if (stringValues === prevStringValues && !wasEmptyFiltered) {  // пустой выбор первый в серии
//             wasEmptyFiltered = true;
//         } else {                                                // не пустой выбор
//             wasEmptyFiltered = false;
//         }

//         const url = '?' + new URLSearchParams({
//             ...needFilterKey,
//             ...selectedStringData
//         }); 

//         prevStringValues = stringValues;
//         history.pushState(null, null, url);

//         return fetch(url, {headers: {'x-requested-with': 'XMLHttpRequest'}})
//             .then(response => {
//                 if (!response.ok) {
//                     throw Error("Произошла ошибка с кодом " + response.status);
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 return data.html;
//             });
//     }
// })();

// const filterRequest = () => {
//     // вынести в отдельный файл и вынести из функции
//     const articlesContainer = document.querySelector('.content__articles');

//     promisefilterRequest()
//         .then(data => {
//             if (data !== null) {
//                 articlesContainer.innerHTML = data;
//             }
//         })
//         .catch(e => {
//             // отобразить попап
//             articlesContainer.innerHTML = e.message;
//         });
// }

// const filtersClickHandler = () => {
//     const filtersButton = document.querySelector('.button-filters');

//     if (!filtersButton) {
//         return;
//     }

//     const filters = filtersButton.querySelector('button.filters');
//     const filterItems = filtersButton.querySelector('.filter-items'); 

//     filters.addEventListener('click', e => {
//         e.preventDefault();
        
//         document.body.className = "hidden";
        
//         const contentRect = document.getElementById('content').getBoundingClientRect();
//         filterItems.style.right = contentRect.left + "px";
//         filtersButton.classList.toggle('active');
//     });

//     const filtersBackground = filtersButton.querySelector('.filter-background');

//     filtersBackground.addEventListener('click', e => {
//         e.preventDefault();

//         filterRequest();

//         document.body.className = "";
//         filtersButton.classList.remove('active');
//     });

//     // Открытие подменю в фильтрах
//     const listButtonNames = filtersButton.querySelectorAll('.list-button-name');
//     listButtonNames.forEach(item => {
//         item.addEventListener('click', e => {
//             item.classList.toggle('active');
//             let filterItem = item.nextElementSibling;
//             if (filterItem.style.maxHeight) {
//                 filterItem.style.maxHeight = null;
//             } else {
//                 filterItem.style.maxHeight = filterItem.scrollHeight + "px";
//             }
//         });
//     });

//     // Заполнение контейнера выбранных фильтров selected-filters
//     const selectedFiltersContainer = document.querySelector('.selected-filters');
//     const inputItems = filtersButton.querySelectorAll('.filter-item input');

//     const crossForSelectedTemplate = ' <svg version="1.1" xmlns="http://www.w3.org/2000/svg"  preserveAspectRatio="xMaxYMin meet"' +
//         'height="0.8em" viewBox="0 0 11 11"><path d="M2.2,1.19l3.3,3.3L8.8,1.2C8.9314,1.0663,9.1127,0.9938,9.3,1' +
//         'C9.6761,1.0243,9.9757,1.3239,10,1.7&#xA;&#9;c0.0018,0.1806-0.0705,0.3541-0.2,0.48L6.49,5.5' +
//         'L9.8,8.82C9.9295,8.9459,10.0018,9.1194,10,9.3C9.9757,9.6761,9.6761,9.9757,9.3,10&#xA;&#9;' +
//         'c-0.1873,0.0062-0.3686-0.0663-0.5-0.2L5.5,6.51L2.21,9.8c-0.1314,0.1337-0.3127,0.2062-0.5,0.2' +
//         'C1.3265,9.98,1.02,9.6735,1,9.29&#xA;&#9;C0.9982,9.1094,1.0705,8.9359,1.2,8.81L4.51,5.5L1.19,2.18' +
//         'C1.0641,2.0524,0.9955,1.8792,1,1.7C1.0243,1.3239,1.3239,1.0243,1.7,1&#xA;&#9;C1.8858,0.9912,2.0669,1.06,2.2,1.19z"/></svg>';

//     let selectedItemsData = {
//         selectedArray: [],
//         addNode: function(value, filterKey) {
//             const div = document.createElement('div');
//             const spanInDiv = document.createElement('span');

//             div.className = 'selected-filter-item';
//             div.dataset.value = value;
//             div.dataset.filter = filterKey;
//             div.textContent = value;
//             spanInDiv.innerHTML = crossForSelectedTemplate;

//             div.append(spanInDiv);
            
//             // Скрытие из списка и дезактивация соотвествующего инпута, релоад
//             div.addEventListener('click', e => {
//                 const selectedInputs = filtersButton.querySelectorAll(`div[data-filter=${filterKey}] input:checked`);
//                 selectedInputs.forEach(input => {
//                     if (input.value === div.dataset.value) {
//                         input.checked = false;
                        
//                         filterRequest();
                        
//                         this.removeNode(value);
//                     }
//                 });
//             });

//             this.selectedArray.push(div);
//             selectedFiltersContainer.append(div);
//         },
//         removeNode: function(value) {
//             const div = this.selectedArray.find(item => item.dataset.value === value);
//             if (!div) return;
//             this.selectedArray = this.selectedArray.filter(item => item !== div);
//             div.remove();
//         },
//         clear: function() {
//             this.selectedArray.forEach(div => {
//                 div.remove();
//             });
//             this.selectedArray = [];
//         }
//     };

//     inputItems.forEach(item => {
//         item.addEventListener('change', e => {
//             if (e.target.checked) {
//                 selectedItemsData.addNode(e.target.value, e.target.name);
//             } else {
//                 selectedItemsData.removeNode(e.target.value);
//             }
//         });
//     });

//     const inputs = filtersButton.querySelectorAll('.filter-item input');

//     // Кнопка очистки фильтров 
//     const filterClearButton = filtersButton.querySelector('.filter-clear');
//     filterClearButton.addEventListener('click', e => {
//         e.preventDefault();
        
//         inputs.forEach(item => {
//             item.checked = false;
//         });

//         selectedItemsData.clear();
//     });

//     // Установка active filter-item
//     const setSelectedItems = () => {
//         const searchParams = new URLSearchParams(window.location.search);

//         const inputsArray = [...inputs];
//         const filterItemsContainers = filtersButton.querySelectorAll('div[data-filter]');

//         inputs.forEach(item => {
//             item.checked = false;
//         });

//         selectedItemsData.clear();

//         if (searchParams.has('filter') && searchParams.get('filter') === 'true') { 
//             filterItemsContainers.forEach(itemContainer => {
//                 const filterKey = itemContainer.dataset.filter;
//                 if (searchParams.has(filterKey)) {
//                     const values = searchParams.get(filterKey).split('+');
//                     values.forEach(val => {
//                         const input = inputsArray.find(el => el.value === val);
//                         if (input) {
//                             input.checked = true;
//                             selectedItemsData.addNode(val, input.name);
//                         }
//                     });
//                 }
//             });
//         }
//         // for sorting
//         if (searchParams.has('sorting')) {
//             const sortingKey = searchParams.get('sorting');
//             const sortingInputs = document.querySelectorAll('.button-sorting .sorting-item input');
//             const sortingText = document.querySelector('.button.sorting .text');
//             sortingInputs.forEach(item => {
//                 if (item.value === sortingKey) {
//                     sortingText.textContent = item.nextElementSibling.textContent;
//                     item.checked = true;
//                     return;
//                 }
//             });
//         }
//     }

//     setSelectedItems();

//     window.addEventListener('popstate', e => {
//         setSelectedItems();
//         filterRequest();
//     });
// };

// const sortingClickHandler = () => {
//     const sortingButton = document.querySelector('.button-sorting');
//     if (!sortingButton) {
//         return;
//     }

//     const sorting = sortingButton.querySelector('button.sorting');
//     const sortingItems = sortingButton.querySelector('.sorting-items');

//     sorting.addEventListener('click', e => {
//         e.preventDefault();

//         sortingItems.classList.toggle('active');
//     });

//     const sortingText = sorting.querySelector('.text');
//     const sortingInputItems = sortingButton.querySelectorAll('.sorting-item input');

//     sortingInputItems.forEach(input => {
//         input.addEventListener('change', e => {
//             e.preventDefault();

//             if (e.target.checked) {
//                 sortingText.textContent = e.target.nextElementSibling.textContent;
//                 filterRequest();
//             }
//         });
//     });
// };

const scrollHandler = () => {
    let lastScroll = window.pageYOffset;
    const headerSections = document.querySelector('.header-sections');
    const classHide = "hidden"

    if (!headerSections) return;

    const delta = headerSections.offsetHeight;

    window.addEventListener('scroll', e => {
        const currentScroll = window.pageYOffset;

        if (Math.abs(lastScroll - currentScroll) <= delta) return;
        if (currentScroll > lastScroll && lastScroll > 0) {
            if (!headerSections.classList.contains(classHide)) {
                headerSections.classList.add(classHide);
            }
        } else {
            headerSections.classList.remove(classHide);
        }

        lastScroll = currentScroll;
    });
};

window.addEventListener('DOMContentLoaded', () => {
    scrollHandler();
    searchFormClickHandler();
    // filtersClickHandler();
    // sortingClickHandler();
    controlButtonsHandler();
    imageInitClickHandler();
    sliderHandler();
    musicSliderHandler();
});