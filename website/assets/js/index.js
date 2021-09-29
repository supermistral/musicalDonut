import { controlButtonsHandler } from "./control_buttons";
import { CSS_CLASSES, BASE_URL } from "./constants";
import { getCookie, isTouchDevice, setCookie } from "./utils/dom";
import { popupClickHandler } from "./utils/popup";


const imageInitClickHandler = () => {
    const imagesWrappers = document.querySelectorAll(".img-cover img");
    if (imagesWrappers.length === 0) {
        return;
    }

    const wrapperContent = document.getElementById("content");
    const fullscreenClass = CSS_CLASSES.popup.fullscreen;
    const targetNoClickClass = CSS_CLASSES.popup.targetNoClick;

    imagesWrappers.forEach(item => {
        item.addEventListener('click', (e) => {

            const imageSrc = e.target.src;
            const imageAlt = e.target.alt;

            let fullsizeWrapper = document.createElement('div');    
            fullsizeWrapper.className = "img-fullsize__wrapper " + fullscreenClass;
            fullsizeWrapper.innerHTML = "<div class='img-fullsize__inner'>" +
                "<img class='" + targetNoClickClass + "' src='" + imageSrc + "' alt='" + imageAlt + "'>" + 
                "<div class='cross'></div></div></div>";

            popupClickHandler(fullsizeWrapper);

            wrapperContent.append(fullsizeWrapper);
        });
    });
};

const sliderHandler = () => {
    const sliders = document.querySelectorAll('.img-cover.slider');
    if (sliders.length === 0) {
        return;
    }

    const itemImgClassName = "item-img";
    const maxHeigth = 800;

    const sliderResizeHandler = () => {
        const newWidth = window.innerWidth;

        sliders.forEach(item => {
            const sliderCover = item.querySelector('.slider-cover');
            if (newWidth >= maxHeigth) {
                sliderCover.style.height = null;
                return;
            }
            sliderCover.style.height = newWidth + "px";
        });
    }

    window.addEventListener('resize', e => {
        sliderResizeHandler();
    });

    sliders.forEach(item => {
        const images = item.querySelectorAll("." + itemImgClassName);
        const imagesLength = images.length;
        let imageIndex = 0;

        const arrowPrev = item.querySelector('.prev');
        const arrowNext = item.querySelector('.next');
        let nodeCurNum = item.querySelector('.info span');

        const prevClick = () => {
            const imgCur = images[imageIndex];
            imageIndex = imageIndex > 0 ? imageIndex - 1 : imagesLength - 1;
            const imgNext = images[imageIndex];

            imgCur.className = itemImgClassName + " anim-right";
            imgNext.className = itemImgClassName + " active from-right";
        };

        const nextClick = () => {
            const imgCur = images[imageIndex];
            imageIndex = imageIndex < imagesLength - 1 ? imageIndex + 1 : 0;
            const imgNext = images[imageIndex];

            imgCur.className = itemImgClassName + " anim-left";
            imgNext.className = itemImgClassName + " active from-left";
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
    });

    if (document.body.clientWidth <= maxHeigth) {
        sliderResizeHandler();
    }
};

const musicSliderHandler = () => {
    // Список всех песен
    const songRefs = document.querySelectorAll('.song__control');
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
    
    const setActiveSongs = (service, elem = null) => {
        const setActiveSong = (songRef) => {
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
        }

        elem 
            ? setActiveSong(elem)
            : songRefs.forEach(songRef => { setActiveSong(songRef) });
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

    const getClientY = event => event.clientY || event.touches[0].clientY;
    const getClientX = event => event.clientX || event.touches[0].clientY; 

    const musicSliderMouseDownHandler = e => {
        e.preventDefault();
        musicSlider.classList.add("active");

        const shiftY = getClientY(e) - musicSlider.getBoundingClientRect().top;
        const diffHeight = musicItem.offsetHeight - musicSlider.offsetHeight;

        const mouseMoveHandler = event => {
            let top = getClientY(event) - shiftY - musicItem.getBoundingClientRect().top;
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
            moveSlider();
        };
        
        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('touchmove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
        document.addEventListener('touchend', mouseUpHandler);
    }

    musicSlider.addEventListener('mousedown', e => {
        musicSliderMouseDownHandler(e);
    });
    musicSlider.addEventListener('touchstart', e => {
        musicSliderMouseDownHandler(e);
    });
    
    musicSlider.ondragstart = () => false;

    const songRefsRequest = (songId, callback) => {
        if (songId === null)
            return;

        const url = `${BASE_URL}/articles/song/${songId}/refs/`;

        fetch(url, {headers: {
            'x-requested-with': 'XMLHttpRequest', 
            'credentials': 'same-origin'
        }})
            .then(response => {
                if (!response.ok) {
                    throw new Error('Произошла ошибка запроса');
                }
                return response.json();
            })
            .then(data => {
                callback(data);
            })
            .catch(e => {
                alert(e);
            });
    }

    songRefs.forEach(songItem => {
        const songBlockContainer = songItem.querySelector('.song__refs');
        
        // кнопка показа виджетов
        const buttonSongRefs = songItem.querySelector('.open-refs');

        const setSongRefElements = ({ html, is_enabled, elem, elemParent }) => {
            elem.innerHTML = html;

            if (is_enabled) {
                setActiveSongs(currentService, elemParent);
                showMusicSlider(elemParent);
            }
        }

        buttonSongRefs.addEventListener('click', e => {
            // songItem.classList.toggle('hidden');
            if (songBlockContainer.hasChildNodes()) {
                songRefs.forEach((item, i) => {
                    const elem = item.querySelector('.song__refs');
                    if (i === 0) {
                        songRefsRequest(
                            item.dataset.id || null,
                             data => setSongRefElements({...data, elem: elem})
                        );
                    } else {
                        setSongRefElements({ html: '', is_enabled: false, elem: elem });
                    }
                });
            } else {
                songRefs.forEach(item => {
                    const elem = item.querySelector('.song__refs');
                    songRefsRequest(
                        item.dataset.id || null, 
                        data => setSongRefElements({...data, elem: elem, elemParent: item})
                    );
                });
            }
        });

        const showMusicSlider = (elem = songItem) => {
            // элемент с песней / плейлистом
            const songContainer = elem.querySelector('.song__container');
            // блок настроек для отображения слайдера
            const songInfo = elem.querySelector('.song__info');
            console.log(elem);

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
    const searchButtons = document.querySelectorAll('.search-button');

    if (searchButtons.length === 0) return;

    const wrapperContent = document.getElementById("content");
    const targetNoClickClass = CSS_CLASSES.popup.targetNoClick;

    const searchButtonClickHandler = () => {
        const div = document.createElement('div');
        const searchFormString = "<div class='search-form__inner " + targetNoClickClass +
            "'><div class='search-form-top'><div class='text'>Найти</div></div><form class='search-form'>" +
            "<input type='text' placeholder='найти...' name='search'>" +
            "<button type='submit'><i class='fas fa-arrow-circle-right'></i></button></form>" +
            "<div class='search-form-bottom'>заголовок, исполнитель, песня</div></div>";

        div.className = "search-form__wrapper " + CSS_CLASSES.popup.fullscreen;
        div.innerHTML = searchFormString;

        popupClickHandler(div);

        const input = div.querySelector('input');
        const button = div.querySelector('button');
        const isEmptyInput = el => el.value.trim().length === 0;

        input.addEventListener('keyup', e => {
            button.disabled = isEmptyInput(e.target);
        });

        input.addEventListener('blur', e => {
            button.disabled = true;
        });

        button.disabled = isEmptyInput(input);
        wrapperContent.append(div);
        input.focus();
    }
    
    searchButtons.forEach(item => {
        item.addEventListener('click', searchButtonClickHandler);
    });
};

const scrollHandler = () => {
    const headerSections = document.querySelector('.header-sections');

    if (!headerSections) return;

    let     lastScroll              = window.pageYOffset;
    const   contentBottomContainer  = document.querySelector('.content-header-text-bottom__container'),
            header                  = document.querySelector('header'),
            delta                   = headerSections.offsetHeight,
            classHide               = "hidden",
            classBlock              = "blocked",
            classHeaderBlock        = "blocked";

    const scrollHandlerOnSectionPage = () => {
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
    };

    const scrollHandlerOnNonSectionPage = () => {
        const currentScroll = window.pageYOffset;
        const contentBottomContainerTop = contentBottomContainer.getBoundingClientRect().top 
            - header.offsetHeight + contentBottomContainer.offsetHeight;

        if (contentBottomContainerTop <= 0) {
            if (!headerSections.classList.contains(classBlock)) {
                headerSections.classList.add(classBlock, classHide);
                header.classList.add(classHeaderBlock);
            } else if (currentScroll > lastScroll && lastScroll > 0) {
                if (!headerSections.classList.contains(classHide)) {
                    headerSections.classList.add(classHide);
                }
            } else {
                headerSections.classList.remove(classHide);
            }
        } else {
            headerSections.classList.remove(classBlock);
            header.classList.remove(classHeaderBlock);
        }

        lastScroll = currentScroll;
    };

    window.addEventListener(
        'scroll', 
        contentBottomContainer ? 
            scrollHandlerOnNonSectionPage : 
            scrollHandlerOnSectionPage
    );
};

// Доделать почту
const mailingClickHandler = () => {
    const mailingButton = document.querySelector('mailing-button');
    if (!mailingButton) return;

    mailingButton.addEventListener('click', e => {
        const   wrapperContent      = document.getElementById("content"),
                targetNoClickClass  = CSS_CLASSES.popup.targetNoClick,
                div                 = document.createElement('div');
        
        const newsletterFormString = "<div class='newsletter-form__inner " + targetNoClickClass +
            "'></div>";

        div.className = 'newsletter-form__wrapper ' + CSS_CLASSES.popup.fullscreen;
    });

    const mailingRequest = () => {
        
    }
}

const hidePreloader = () => {
    const preloader = document.getElementById('preloader');
    preloader.classList.add('will-be-hidden');

    setTimeout(() => {
        preloader.remove();
    }, 1000);
}

const setArticleCardsTouchEvent = () => {
    if (isTouchDevice()) {
        const   articleCards = document.querySelectorAll('.article-card'),
                touchClass   = 'touch';

        articleCards.forEach(card => {
            const articleContent = card.querySelector('.article-card-content');

            articleContent.addEventListener('click', e => {
                if (card.classList.contains(touchClass)) {
                    card.classList.remove(touchClass);
                } else {
                    articleCards.forEach(el => el.classList.remove(touchClass));
                    card.classList.add(touchClass);
                }
            });
        });
    }
}

window.addEventListener('DOMContentLoaded', () => {
    scrollHandler();
    searchFormClickHandler();
    controlButtonsHandler();
    imageInitClickHandler();
    sliderHandler();
    musicSliderHandler();
    setArticleCardsTouchEvent();
});

window.addEventListener('load', e => {
    hidePreloader();
})